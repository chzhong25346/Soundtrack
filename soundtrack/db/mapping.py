import pandas as pd
import datetime as dt
from ..utils.fetch import fetch_index, get_daily_adjusted
from ..utils.util import gen_id
from ..models import Index, Quote, Report


def map_index():
    df = fetch_index()
    df_records = df.to_dict('records')
    model_instnaces = [Index(
        symbol = record['symbol'],
        company = record['company'],
        sector = record['sector'],
        industry = record['industry']
    ) for record in df_records]

    return model_instnaces


def map_quote(config,ticker,size,today_only):
    df = get_daily_adjusted(config,ticker,size,today_only)
    df_records = df.to_dict('records')
    model_instnaces = [Quote(
        id = gen_id(ticker+str(record['date'])),
        symbol = ticker,
        date = record['date'],
        open = record['open'],
        high = record['high'],
        low = record['low'],
        close = record['close'],
        adjusted = record['adjusted close'],
        volume = record['volume']
    ) for record in df_records]

    return model_instnaces


def map_report(config,ticker,date):
    date = dt.datetime.today().strftime("%m-%d-%Y")
    df_records = df.to_dict('records')
    model_instnaces = [Report(
        id = gen_id(ticker+str(date)),
        symbol = ticker,
        yr_high = record['yr_high'],
        yr_low = record['yr_low'],
        industry = record['industry'],
        downtrend = record['downtrend'],
        uptrend = record['uptrend'],
        high_volume = record['high_volume'],
        low_volume = record['low_volume'],
        pattern = record['pattern']
    ) for record in df_records]

    return model_instnaces
