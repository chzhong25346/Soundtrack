from ..models import Index, Quote
from sqlalchemy import exists
import datetime as dt
import logging
logger = logging.getLogger('main.read')

def read_ticker(s):
    list = [obj.symbol for obj in s.query(Index)]
    return list


def read_exist(s, ticker):
    date = dt.datetime.today().strftime("%Y-%m-%d")
    ret = s.query(exists().where(Quote.symbol==ticker).where(Quote.date==date)).scalar()
    return ret


# def has_table(e, tname):
#     return e.dialect.has_table(e, table)


def has_index(s):
    return s.query(Index).first()
