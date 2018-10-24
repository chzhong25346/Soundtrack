import urllib3,certifi
import pandas as pd
import json
import time
from datetime import datetime as dt
from alpha_vantage.timeseries import TimeSeries

def fetch_index():
    page= 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    https = urllib3.PoolManager( cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(),)
    try:
        url = https.urlopen('GET',page)
        page_d = pd.read_html(url.data,header=0,keep_default_na=False) # NA -> NaN is National Bank of Canada
        page_d[0].columns = ['symbol', 'company', 'Fillings', 'sector', 'industry', 'Location', 'First Added', 'CIK', 'Founded']
        data = page_d[0]
        data = data.drop(columns=['Fillings', 'Location', 'First Added', 'CIK', 'Founded'])
        data.index.name = 'symbol'
        print(data)
        return data
    except Exception as e:
        print(e)


def get_daily_adjusted(config,ticker,size,today_only):
    key = config.AV_KEY
    ts = TimeSeries(key)
    try:
        time.sleep(15)
        data, meta_data = ts.get_daily_adjusted(ticker,outputsize=size)
        df = pd.DataFrame.from_dict(data).T
        df = df.drop(["7. dividend amount","8. split coefficient"], axis=1)
        df.columns = ["open","high","low","close","adjusted close","volume"]
        if today_only:
            df = df.loc[df.index.max()].to_frame().T
            df.index.name = 'date'
            df = df.reset_index()
            return df
        else:
            df.index.name = 'date'
            df = df.reset_index()
            return df
    except Exception as e:
        print(e)
