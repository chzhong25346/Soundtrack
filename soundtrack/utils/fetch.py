import urllib3,certifi
import pandas as pd
import json
import time
import requests
import os
from ..utils.util import normalize_Todash
from datetime import datetime as dt
from alpha_vantage.timeseries import TimeSeries
import logging
import requests, re
from bs4 import BeautifulSoup
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





class fetchError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
