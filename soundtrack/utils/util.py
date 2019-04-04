import hashlib
import logging
import re
logger = logging.getLogger('main.util')


def gen_id(string):
    return int(hashlib.md5(str.encode(string)).hexdigest(), 16)


def normalize_Todash(data):
    data['symbol'] = data['symbol'].str.replace(".","-")
    return data


def groupby_na_to_zero(df, ticker):
    df = df.groupby(ticker).first()
    df.fillna(0, inplace=True)
    return df


def missing_ticker(index):
    tickers = set()
    fh = open('log.log', 'r')
    rx = re.compile("\((.+)\)")
    strings = re.findall(rx, fh.read())
    fh.close()
    for s in strings:
        if(index in s):
            tickers.add(s.split(',')[1])
    logger.info('Found %d missing quotes in %s' % (len(tickers), index))
    return list(tickers)
