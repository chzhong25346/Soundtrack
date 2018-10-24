import os, sys
from .utils.config import Config
from .db.db import Db
from .db.mapping import map_index, map_stock
from .db.write import bulk_save
from .db.read import read_ticker, read_exist


def main():
    Config.DB_NAME='sp500'
    db = Db(Config)
    s = db.session()
    e = db.get_engine()

    # Create table based on Models
    db.create_all()

    # Fetch/Mapping/Write Index
    bulk_save(s, map_index())

    # model_list = map_stock(Config,'A','compact',today_only=True)
    # bulk_save(s, model_list)


    tickerL = read_ticker(s)
    for ticker in tickerL:
        # if (read_exist(s, ticker)) is False:
        try:
            model_list = map_stock(Config,ticker,'compact',today_only=False)
            bulk_save(s, model_list)
        except:
            pass



if __name__ == '__main__':
    main()
