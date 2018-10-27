import datetime as dt
import pandas as pd
import logging
from db.mysql import *
from db.read import *
from db.write import *
from .trigger import *
logger = logging.getLogger('main.quote')


def get_quote(list,engine):
    '''
    get today close price from a ticker
    return list = [dic{ticker:price},{}...]
    '''
    order_list = []
    for ticker in list:
        # TICKER in capital case
        equity = ticker
        # ticker.to
        ticker_to = (ticker+'.to').lower()
        # today's df - close price
        price = read_table_df_Engine(ticker_to,engine).iloc()[-1]['close']
        order_list.append({ticker:price})

    return order_list
