import pandas as pd
from ..utils.fetch import fetch_index, get_daily_adjusted
from ..utils.util import gen_id
from ..models import Index, Stock


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


def map_stock(config,ticker,size,today_only):
    print(ticker)
    df = get_daily_adjusted(config,ticker,size,today_only)
    df_records = df.to_dict('records')
    model_instnaces = [Stock(
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
