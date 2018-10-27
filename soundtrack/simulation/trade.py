import datetime as dt
import pandas as pd
import logging
from db.mysql import *
from db.read import *
from db.write import *
from db.remove import *
from .trigger import *
logger = logging.getLogger('main.trade')


def execute_order(list,cap,type,engine):
    # BUY or SELL
    if(type=='buy'):
        # for each quote as dict in buy list
        for dict in list:
            # execute buy function
            buy(dict,cap,engine)
    elif(type=='sell'):
        # for each quote as dict in buy list
        for dict in list:
            # execute buy function
            sell(dict,cap,engine)


def buy(dict,cap,engine):
    build_transaction(dict,cap,'buy',engine)
    build_holding(dict,engine)


def sell(dict,cap,engine):
    # if there is already a holding table and found ticker in holding table
    if build_transaction(dict,cap,'sell',engine) is not False:
        # then transaction is completed and holding table is able to build and reflush
        build_holding(dict,engine)


def build_transaction(dict,cap,type,engine):
    '''
    construct dataframe of transaction and write to db
    '''
    # current date
    date = dt.datetime.today().strftime("%m-%d-%Y")
    # ticker,price in list format retrieved from dict
    ticker,price = zip(*dict.items())
    # ticker value
    ticker = ticker[0]
    # price value is float
    price = float(price[0])
    # if type is buy qty is potitive and settlement is negative(sepnding)
    if(type == 'buy'):
        qty = int(cap/price)
        settlement = (price*qty)*-1
    # if type is sell, qty is negative and settlement is potitive(income)
    elif(type == 'sell'):
        # read holding table, if False, table not exits
        df_existing_holding = read_table_df_nodrop_Engine('holding',engine,'ticker')
        # if there is holding table and ticker is found in holding df
        if (df_existing_holding is not False and ticker in df_existing_holding.index.unique()):
            # if sell off all
            if cap == 10000:
                # retrieve quntity which is negative
                qty = (df_existing_holding[(df_existing_holding.index==ticker)].quantity.tolist()[0])*-1
            # if sell off a half
            elif cap == 5000:
                # retrieve quntity which is negative
                qty = ((df_existing_holding[(df_existing_holding.index==ticker)].quantity.tolist()[0])*-1)/2
            # settlement amount is positive(income)
            settlement = abs(price*qty)
        # if no table or no ticker in holding
        else:
            logger.debug('No table or not holding: %s, cannot %s' % (ticker,type))
            return False
    # TRANSACTION dict
    dict_transaction = {'date':date, 'ticker':ticker, 'type':type,'quantity':qty,'price':price,'settlement':settlement}
    # TRANSACTION dataframe
    df_transaction = pd.DataFrame.from_records([dict_transaction],index='date')
    df_transaction.index = pd.to_datetime(df_transaction.index)
    # write df to sql - write.py
    df_to_sql_prikey('transaction',df_transaction,engine,'date')
    logger.debug('(ORDER) %s %s %s shares at %s/share' % (type,ticker,qty,price))


def build_holding(dict,engine):
    '''
    construt dataframe and write/udpate to db
    '''
    # ticker,price in list format retrieved from dict
    ticker,price = zip(*dict.items())
    # ticker value
    ticker = ticker[0]
    # price value is float
    price = float(price[0])
    # get current holding df
    transaction = read_table_df_nodrop_Engine('transaction',engine,'date')
    # all rows in specified ticker
    df_ticker = transaction[(transaction['ticker']==ticker)]
    # all rows in specified ticker and type = buy
    df_ticker_buy = transaction[(transaction['ticker']==ticker) & (transaction['type']=='buy')]
    # sum up quantity of this ticker all of buy and sell records
    qty = df_ticker['quantity'].sum()
    # if there is nothing holding on
    if (qty != 0):
        # average cost each row: sum of (price*qty) / sum of 'qty'
        avg_cost = sum(df_ticker_buy.price*df_ticker_buy.quantity)/sum(df_ticker_buy.quantity)
        # market price is the price from quote that is contained in the dict
        mkt_price = price
        # book value is average cost times quantity
        book_value = avg_cost*qty
        # market value is market price times quantity
        mkt_value = mkt_price*qty
        # changes
        change_dollar = mkt_value - book_value
        change_percent = (mkt_value/book_value-1)*100
        # construct holding dictionary
        dict_holding = {'ticker':ticker,'quantity':qty,'avg_cost':avg_cost,'mkt_price':mkt_price,'book_value':book_value,'mkt_value':mkt_value,'change_dollar':round(change_dollar,2),'change_percent':round(change_percent,2)}
        # constract holding dataframe from the dictionary
        df_holding = pd.DataFrame.from_records([dict_holding])
        # read holding table, if False, table not exits
        df_existing_holding = read_table_df_nodrop_Engine('holding',engine,'ticker')
        # table not exists
        if df_existing_holding is False:
            # new write new table
            df_to_sql_prikey('holding',df_holding,engine,'ticker')
        # table already exists, remove existing row and re-write
        else:
            # delete ticker in holding table - remove.py
            delete_by_fieldValue_Engine('holding','ticker',ticker,engine)
            # update new rows of this ticker - write.py
            df_to_sql_prikey('holding',df_holding,engine,'ticker')
    # if quantity is zero
    else:
        # delete ticker in holding table - remove.py
        delete_by_fieldValue_Engine('holding','ticker',ticker,engine)
