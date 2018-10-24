from .utils.config import Config
from .db.db import Db
from .db.mapping import map_index, map_stock
from .db.write import bulk_save
from .db.read import read_ticker, has_index
import logging
import logging.config
import getopt
import sys

logging.config.fileConfig('soundtrack\log\logging.conf')
logger = logging.getLogger('main')

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"u:",["update="])
    except getopt.GetoptError:
        print('run.py -u <full|compact>')
        print('run.py -r')
        print('run.py -s')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run.py -u <full|compact>')
            print('run.py -r')
            print('run.py -s')
            sys.exit()
        elif opt in ("-u", "--update"):
            if(arg == 'full'):
                type = arg
                today_only = False
                update(type, today_only)  # Full update
            elif(arg == 'compact'):
                type = arg
                today_only = True
                update(type, today_only)  # Compact update for today



def update(type, today_only):
    Config.DB_NAME='sp500'
    db = Db(Config)
    s = db.session()
    e = db.get_engine()
    # Create table based on Models
    db.create_all()

    if has_index is not None:
        # Fetch/Mapping/Write Index
        bulk_save(s, map_index())

    tickerL = read_ticker(s)
    for ticker in tickerL:
        try:
            logger.info('Processing: %s' % (ticker))
            model_list = map_stock(Config,ticker,type,today_only)
            bulk_save(s, model_list)
        except:
            logger.error('Unable to process: %s' % (ticker))
