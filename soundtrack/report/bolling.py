import logging
import pandas as pd
from stockstats import StockDataFrame
logger = logging.getLogger('main.bolling')


def bolling(ticker, df):
    pd.set_option('mode.chained_assignment', None)
    stock = StockDataFrame.retype(df)
    # print(stock.tail())



    # Today's Bolling
    boll = round(stock['boll'][-1], 2)
    upper = round(stock['boll_ub'][-1], 2)
    lower = round(stock['boll_lb'][-1], 2)

    # Today's OHLC
    close = stock['close'][-1]
    open = stock['open'][-1]
    high = stock['high'][-1]
    low = stock['low'][-1]

    # # yesterday's Bolling
    # boll2 = round(stock['boll'][-2], 2)
    # upper2 = round(stock['boll_ub'][-2], 2)
    # lower2 = round(stock['boll_lb'][-2], 2)
    #
    # # yesterday's OHLC
    # close2 = stock['close'][-2]
    # open2 = stock['open'][-2]
    # high2 = stock['high'][-2]
    # low2 = stock['low'][-2]

    # Last five days OHLC
    last5 = stock[['close','open','high','low','boll','boll_ub','boll_lb']][-6:-1]

    # If Last five days touched bound
    last5['break'] = (last5['high'] >= last5['boll_ub']) | (last5['low'] <= last5['boll_lb'])
    Is_Last5_break = last5['break'].any()
    # print(last5)
    # print(Is_Last5_break)
    # print(stock.index[-1])

    if ( Is_Last5_break == False and high > upper and close >= upper ):
        # print( {'symbol':ticker,'bolling':'buy'} )
        return {'symbol':ticker,'bolling':'buy'}

    elif ( Is_Last5_break == False and low < lower and close <= lower ):
        # print( {'symbol':ticker,'bolling':'sell'} )
        return {'symbol':ticker,'bolling':'shell'}
