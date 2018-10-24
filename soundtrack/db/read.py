from ..models import Index, Stock
from sqlalchemy import exists


def read_ticker(s):
    list = [obj.symbol for obj in s.query(Index)]
    return list


def read_exist(s, ticker):
    ret = s.query(exists().where(Stock.symbol==ticker)).scalar()
    return ret
