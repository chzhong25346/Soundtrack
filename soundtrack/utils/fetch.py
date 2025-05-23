import urllib3,certifi
import pandas as pd
import json
import time
from dateutil.parser import parse
from curl_cffi import requests as curl_requests
import requests
import os
from ..utils.util import normalize_Todash
from datetime import datetime as dt
from alpha_vantage.timeseries import TimeSeries
import logging
import requests, re
from bs4 import BeautifulSoup
import yfinance as yf
logger = logging.getLogger('main.fetch')


def fetch_index(index_name):
    path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(path, index_name+'.csv')
    try:
        if (index_name == 'nasdaq100'):
            data = pd.read_csv(filename)
            data.columns = ['symbol', 'company']
            # data = data.drop(['lastsale', 'netchange', 'netchange', 'share_volume', 'Nasdaq100_points', 'Unnamed: 7'], axis=1)
            data.index.name = 'symbol'
            data = normalize_Todash(data)
            return data
        elif (index_name == 'tsxci' or index_name == 'sp100'):
            data = pd.read_csv(filename, na_filter = False)
            data.columns = ['symbol', 'company']
            # data = normalize_Todash(data)
            return data
    except Exception as e:
        # logger.error('Failed to fetch index! {%s}' % e)
        raise fetchError('Fetching failed')


def get_daily_adjusted(config,ticker,size,today_only,index_name):
    key = config.AV_KEY
    ts = TimeSeries(key)
    try:
        time.sleep(15)
        if(index_name == 'tsxci'):
            data, meta_data = ts.get_daily_adjusted(ticker+'.TO',outputsize=size)
        else:
            data, meta_data = ts.get_daily_adjusted(ticker,outputsize=size)
        df = pd.DataFrame.from_dict(data).T
        df = df.drop(["7. dividend amount","8. split coefficient"], axis=1)
        df.columns = ["open","high","low","close","adjusted close","volume"]
        if today_only:
            df = df.loc[df.index.max()].to_frame().T # the latest quote
            df.index.name = 'date'
            df = df.reset_index()
            return df
        else:
            df.index.name = 'date'
            df = df.reset_index()
            return df
    except:
        # logger.error('Failed to fetch %s' % ticker)
        raise fetchError('Fetching failed')


def get_da_req(config, ticker, index_name):
    key = config.AV_KEY
    try:
        time.sleep(15)
        if(index_name == 'tsxci'):
            url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}'.format(ticker+'.TO', key)
        else:
            url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}'.format(ticker, key)
        r = requests.get(url)
        data = r.json()['Global Quote']
        df = pd.DataFrame(data, index=[0])
        df.rename(columns={"02. open": "open",
                           "03. high": "high",
                           "04. low": "low",
                           "05. price": "close",
                           "06. volume": "volume",
                           "07. latest trading day": "date",
                            }, inplace=True)
        df['adjusted close'] = df['close']
        df = df[["date","open","high","low","close","adjusted close","volume"]]
        return df
    except:
        raise fetchError('Fetching failed')


def get_tmxmoney_daily(ticker):
    time.sleep(15)
    url = 'https://web.tmxmoney.com/quote.php?qm_symbol={}'.format(ticker)
    try:
        today = dt.today().strftime("%Y-%m-%d")
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        close = float(soup.select("[class~=price] span")[0].get_text())
        volume = int(re.sub(r"\D", "", soup.select("[class~=col-4] strong")[0].get_text()))
        open = float(soup.select("[class~=dq-card] strong")[0].get_text())
        high = float(soup.select("[class~=dq-card] strong")[1].get_text())
        low = float(soup.select("[class~=dq-card] strong")[6].get_text())
        df = pd.DataFrame({'date': today,
                         'close': close,
                         "adjusted close": close,
                         'volume': volume,
                         'open': open,
                         'high': high,
                         'low': low,
                         },index=[0])
        return df
    except:
        raise fetchError('Fetching failed')




def get_yahoo_finance_price(ticker):
    time.sleep(2)
    session = curl_requests.Session(impersonate="chrome99")
    try:
        t = yf.Ticker(ticker, session=session)
        data = t.history(period="1d")
        data.reset_index(inplace=True)
        df = pd.DataFrame({'date': data['Date'].dt.strftime("%Y-%m-%d"),
                         'close': round(data['Close'], 2),
                         "adjusted close": round(data['Close'], 2),
                         'volume': data['Volume'],
                         'open': round(data['Open'], 2),
                         'high': round(data['High'], 2),
                         'low': round(data['Low'], 2),
                         }, index=[0])
        return df
    except Exception as e:
        raise fetchError('Fetching failed')




class fetchError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

######################################## YAHOO Fetching #########




def get_yahoo_bvps(ticker):
    url = 'https://finance.yahoo.com/quote/{0}/key-statistics?p={0}'.format(ticker)
    try:
        html = requests.get(url, headers=_get_headers()).text
    except:
        time.sleep(30)
        html = requests.get(url, headers=_get_headers()).text
    try:
        soup = BeautifulSoup(html,'html.parser')
        soup_script = soup.find("script",text=re.compile("root.App.main")).text
        matched = re.search("root.App.main\s+=\s+(\{.*\})",soup_script)
        if matched:
            json_script = json.loads(matched.group(1))
            cp = json_script['context']['dispatcher']['stores']['QuoteSummaryStore']['defaultKeyStatistics']['bookValue']['fmt']
            return float(cp)
        else:
            return None
    except:
        return None


def get_yahoo_cr(ticker):
    url = 'https://finance.yahoo.com/quote/{0}/key-statistics?p={0}'.format(ticker)
    try:
        html = requests.get(url, headers=_get_headers()).text
    except:
        time.sleep(30)
        html = requests.get(url, headers=_get_headers()).text
    try:
        soup = BeautifulSoup(html,'html.parser')
        soup_script = soup.find("script",text=re.compile("root.App.main")).text
        matched = re.search("root.App.main\s+=\s+(\{.*\})",soup_script)
        if matched:
            json_script = json.loads(matched.group(1))
            cr = json_script['context']['dispatcher']['stores']['QuoteSummaryStore']['financialData']['currentRatio']['fmt']
            return float(cr)
        else:
            return None
    except:
        pass



def _get_headers():
    return {"accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
    "cache-control": "no-cache",
    "dnt": "1",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}


# Stock Chart Fetching

def get_stockcharts_price(ticker):
    if '-' in ticker:
        ticker = ticker.replace('-', '%2F')
    url = 'https://stockcharts.com/j-sum/sum?cmd=symsum&symbol={0}'.format(ticker)
    try:
        html = requests.get(url, headers=_get_headers()).text
    except:
        time.sleep(30)
        html = requests.get(url, headers=_get_headers()).text
    try:
        data = json.loads(html)
        df = pd.DataFrame({'date': parse(data['latestTrade']).strftime("%Y-%m-%d"),
                         'close': data['close'],
                         "adjusted close": data['close'],
                         'volume': data['volume'],
                         'open': data['open'],
                         'high': data['high'],
                         'low': data['low'],
                         }, index=[0])
        return df
    except Exception as e:
        raise fetchError('Fetching failed')


def get_yahoo_finance_price_all(ticker, length="5y"):
    time.sleep(2)
    session = curl_requests.Session(impersonate="chrome99")
    try:
        t = yf.Ticker(ticker, session=session)
        data = t.history(period=length)
        data.reset_index(inplace=True)
        data.rename(columns={"Date": "date", "Open": "open","High": "high","Low":"low","Close":"close","Volume":"volume"}, inplace=True)
        data['adjusted close'] = data['close']
        data = data[["date","open","high","low","close","volume","adjusted close"]]
        data['date'] = data['date'].dt.strftime("%Y-%m-%d")
        return data.drop_duplicates(subset='date', keep="last")
    except:
        return None
