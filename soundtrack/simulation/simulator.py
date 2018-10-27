import datetime as dt
import pandas as pd
import logging
from .db.db.read import *
from .db.db.write import *
from .trigger import *
from .quote import *
from .trade import *
from .rbreaker import rbreaker
logger = logging.getLogger('main.simulator')


def simulator(index_name):
    # report db engine
    engine_report = create_dbengine(db=index_name+"_report")
    # simulation db engine
    engine_simulation = create_dbengine(db=index_name+"_simulation")
    # daily db engine
    engine_dailydb = create_dbengine(db=index_name+"_daily_db")
    # today's table
    tname = dt.datetime.today().strftime("%m-%d-%Y")
    # read report
    df_report = read_table_df_nodrop_Engine(tname,engine_report,'ticker')
    # if buy list is not empty
    if buy_list(df_report):
        # buy list
        all_in,half_in = buy_list(df_report)
        # BUY Order
        if all_in:
            quote_list = get_quote(all_in,engine_dailydb)
            # execute buy order - trade.py
            execute_order(quote_list,10000,"buy",engine_simulation)
        if half_in:
            quote_list = get_quote(half_in,engine_dailydb)
            # execute buy order $5000 - trade.py
            execute_order(quote_list,5000,"buy",engine_simulation)
    # if sell_list is not empty
    if sell_list(df_report):
        # sell list
        all_out,half_out = sell_list(df_report)
        # SELL Order
        if all_out:
            quote_list = get_quote(all_out,engine_dailydb)
            # execute sell order - all holding quantity - trade.py
            execute_order(quote_list,10000,"sell",engine_simulation)
        if half_out:
            quote_list = get_quote(half_out,engine_dailydb)
            # execute sell order - half holding quntity - trade.py
            execute_order(quote_list,5000,"sell",engine_simulation)
    # refreshing holding table
    refresh_holding(engine_simulation, engine_dailydb)
    rbreaker(engine_simulation, engine_dailydb)


def buy_list(df):
    '''
    return lists of tickers based on Buy triggers
    '''
    try:
        #  trigger.py
        all_in = bull_hivolume_uptrend(df)
        logger.debug('buy all: %s', ','.join(all_in))
        half_in = bull_oneyrlow_doji_hivolume(df)
        logger.debug('buy half: %s', ','.join(half_in))
        return all_in,half_in
    except:
        logger.debug('all_in/half_in Empty!')
        return False


def sell_list(df):
    '''
    return lists of tickers based on Sell triggers
    '''
    try:
        # trigger.py
        all_out = bear_hivolume_downtrend(df)
        logger.debug('sell all: %s', ','.join(all_out))
        half_out = bear_oneyrhigh_doji_downtrend(df)
        logger.debug('sell half: %s', ','.join(half_out) )
        return all_out,half_out
    except:
        logger.debug('all_out/half_out Empty!')
        return False


def refresh_holding(engine_simulation, engine_dailydb):
    '''
    read existing holding table, get quote for every ticker
    execute sql to update needed fields.
    '''
    # read holding table, if False, table not exits - db/read.py
    df_holding = read_table_df_nodrop_Engine('holding',engine_simulation,'ticker')
    # table exists
    if df_holding is not False:
        # index is ticker, make it a list
        tickerL = df_holding.index.tolist()
        # [{ticker:price},..] get quote of each ticker - quote.py
        quote_list = get_quote(tickerL,engine_dailydb)
        # each quote in quote list
        for dict in quote_list:
            # ticker,price in list format retrieved from dict
            ticker,price = zip(*dict.items())
            # ticker value
            ticker = ticker[0]
            # the df only includes the ticker
            df_ticker = df_holding[(df_holding.index==ticker)]
            # price value is float
            mkt_price = float(price[0])
            # quntity of the security on holding
            qty = df_ticker.quantity.sum()
            # calculate mkt_value
            mkt_value = qty*mkt_price
            # change in dollar of the security on holding, sum() makes it in int
            change_dollar = round(mkt_value - df_ticker.book_value.sum(),2)
            # change in dollar of the security on holding, sum() makes it in int
            change_percent = round((mkt_value / df_ticker.book_value.sum()-1)*100,2)
            # make a sentence for update (what to update)
            sentence = "`%s`='%s', `%s`='%s', `%s`='%s', `%s`='%s'" % ('mkt_price',mkt_price,'mkt_value',mkt_value,'change_dollar',change_dollar,'change_percent',change_percent)
            # update table with sentence above `ticker` = ticker - db/update.py
            update_Engine('holding',sentence,'ticker',ticker,engine_simulation)
            logger.debug('Refreshing holding: %s at $%s/share, change: $%s(%s percent) ' % (ticker,mkt_price,change_dollar,change_percent))
