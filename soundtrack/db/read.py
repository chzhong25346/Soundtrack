from ..models import Index, Quote
from sqlalchemy import exists
import logging
logger = logging.getLogger('main.read')

def read_ticker(s):
    list = [obj.symbol for obj in s.query(Index)]
    return list


# def read_exist(s, ticker):
#     ret = s.query(exists().where(Stock.symbol==ticker)).scalar()
#     return ret


# def has_table(e, tname):
#     return e.dialect.has_table(e, table)


def has_index(s):
    return s.query(Index).first()
