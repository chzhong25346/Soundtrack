from .utils.config import Config
from .utils.fetch import get_daily_adjusted, get_da_req, get_yahoo_finance_price, fetchError,\
get_stockcharts_price, get_yahoo_finance_price_all
from .utils.util import missing_ticker
from .db.db import Db
from .db.mapping import map_index, map_quote, map_fix_quote, map_report
from .db.write import bulk_save, insert_onebyone, writeError, foundDup
from .db.read import read_ticker, has_index, read_exist
from .email.email import sendMail
from .report.report import report
# from .report.optimize import optimize
from .simulation.simulator import simulator
from .learning.fetch_aer import fetch_aer
import logging
import logging.config
import getopt
import time
import math
import os, sys
logging.config.fileConfig('soundtrack/log/logging.conf')
logger = logging.getLogger('main')

# If fist time create a new function
# Please use Create_all() tables
def main(argv):
    time_start = time.time()
    try:
        opts, args = getopt.getopt(argv,"u:rsea",["update=", "report=", "simulate=", "emailing=", "aer="])
    except getopt.GetoptError:
        print('run.py -u <full|compact|fastfix|slowfix|slowfix_missing> <nasdaq100|tsxci|sp100|eei>')
        print('run.py -r <nasdaq100|tsxci|sp100|eei>')
        print('run.py -s <nasdaq100|tsxci|sp100|eei>')
        print('run.py -e')
        print('run.py -a')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run.py -u <full|compact|fastfix|slowfix|slowfix_missing>  <nasdaq100|tsxci|sp100|eei>')
            print('run.py -r <nasdaq100|tsxci|sp100|eei>')
            print('run.py -s <nasdaq100|tsxci|sp100|eei>')
            print('run.py -e')
            print('run.py -a')
            sys.exit()
        elif (opt == '-u' and len(argv) < 3):
            print('run.py -u <full|compact|fastfix|slowfix|slowfix_missing> <nasdaq100|tsxci|sp100|eei> <ticker>')
            sys.exit()
        elif (opt == '-a' and len(argv) < 3):
            print('run.py -a <daily|full> <st1(License Issued)|st49(Drilling Activity)|st97(Facility Approval)>')
            sys.exit()
        elif opt in ("-u", "--update"):
            if(arg == 'full'):
                index_name = argv[2]
                type = arg
                today_only = False
                update(type, today_only, index_name)  # Full update
            elif(arg == 'compact'):
                index_name = argv[2]
                type = arg
                today_only = True
                update(type, today_only, index_name)  # Compact update for today
            elif(arg == 'slowfix'):
                index_name = argv[2]
                type = 'full' # fixing requires full data
                today_only = False
                update(type, today_only, index_name, fix='slowfix')  # Compact update for today
            elif(arg == 'slowfix_missing'):
                index_name = argv[2]
                type = 'full' # fixing requires full data
                today_only = False
                update(type, today_only, index_name, fix='slowfix_missing')  # Compact update for today
            elif(arg == 'fastfix'):
                index_name = argv[2]
                type = 'full' # fixing requires full data
                today_only = False
                update(type, today_only, index_name, fix='fastfix', ticker=argv[3])  # Compact update for today
        elif opt in ("-r", "--report"):  # Report
            index_name = argv[1]
            analyze(index_name)
        elif opt in ("-s", "--simulate"): # Simulate
            index_name = argv[1]
            simulate(index_name)
        elif opt in ("-e", "--emailing"): # Emailing
            emailing()
        elif opt in ("-a", "--aer"): # Alberta Enenergy Regulator Reports
            mode = argv[1]
            if(mode == 'daily'):
                aer(mode, report_type=argv[2])
            elif(mode == 'full'):
                aer(mode, report_type=argv[2])

    elapsed = math.ceil((time.time() - time_start)/60)
    logger.info("%s took %d minutes to run" % ( (',').join(argv), elapsed ) )


def update(type, today_only, index_name, fix=False, ticker=None):
    logger.info('Run Task:[%s %s UPDATE]' % (index_name, type))
    Config.DB_NAME=index_name
    db = Db(Config)
    s = db.session()
    e = db.get_engine()
    # Create table based on Models
    # db.create_all()
    if has_index(s) == None:
        # Fetch/Mapping/Write Index
        bulk_save(s, map_index(index_name))
    tickerL = read_ticker(s)

   # --------------------------------------- CHECK POINT
    if (fix == 'slowfix_missing'):
        tickerL = missing_ticker(index_name)
    elif (fix == 'fastfix'):
        tickerL = [ticker]

    for ticker in tickerL:
    # for ticker in tickerL[tickerL.index('UNH'):]: # Fast fix a ticker  ---------- CHECK POint
    # for ticker in ['D']: #---------- CHECK POint
        try:

            if (fix == 'fastfix'): # Fast Update, bulk
                # df = get_daily_adjusted(Config,ticker,type,today_only,index_name)
                if index_name == 'tsxci':
                    df = get_yahoo_finance_price_all(ticker+'.TO')
                else:
                    df = get_yahoo_finance_price_all(ticker)
                model_list = []
                for index, row in df.iterrows():
                    model = map_fix_quote(row, ticker)
                    model_list.append(model)
                logger.info("--> %s" % ticker)
                bulk_save(s, model_list)
            elif (fix == 'slowfix' or fix == 'slowfix_missing' ): # Slow Update, one by one based on log.log
                # df = get_daily_adjusted(Config,ticker,type,today_only,index_name)
                if index_name == 'tsxci':
                    df = get_yahoo_finance_price_all(ticker+'.TO')
                else:
                    df = get_yahoo_finance_price_all(ticker)
                model_list = []
                if df is not None:
                    for index, row in df.iterrows():
                        model = map_fix_quote(row, ticker)
                        model_list.append(model)
                    logger.info("--> %s" % ticker)
                    insert_onebyone(s, model_list)
                else:
                    logger.info("--> (%s, not exist)" % ticker)
            else: # Compact Update
                # Extra Exchange Index
                if index_name == 'eei' and type == 'compact':
                    try:
                        df = get_yahoo_finance_price(ticker)
                        model_list = map_quote(df, ticker)
                        bulk_save(s, model_list)
                        logger.info("--> %s" % ticker)
                    except:
                        df = get_stockcharts_price(ticker)
                        model_list = map_quote(df, ticker)
                        bulk_save(s, model_list)
                        logger.info("2--> %s" % ticker)


        except writeError as e:
            logger.error("%s - (%s,%s)" % (e.value, index_name, ticker))
        except foundDup as e:
            logger.error("%s - (%s,%s)" % (e.value, index_name, ticker))
        except fetchError as e:
            logger.error("%s - (%s,%s)" % (e.value, index_name, ticker))
        except:
            logger.error("Updating failed - (index_name,%s)" % (index_name,ticker))

    s.close()


def analyze(index_name):
    logger.info('Run Task: [Reporting]')
    Config.DB_NAME=index_name
    db = Db(Config)
    s = db.session()
    e = db.get_engine()
    # Create table based on Models
    # db.create_all()
    df = report(s)
    model_list = map_report(Config,df)  ####CHECKPOINT
    try:
        insert_onebyone(s, model_list)
    except:
        pass
    # bulk_save(s, model_list)  ####CHECKPOINT

    # # Proceed with Optimization if index=TSXCI
    # if(index_name == 'tsxci'):
    #     optimize(s)

    s.close()


def simulate(index_name):
    logger.info('Run Task: [Simulation]')
    Config.DB_NAME=index_name
    db = Db(Config)
    s = db.session()
    e = db.get_engine()
    # Create table based on Models
    # db.create_all()
    simulator(s)
    s.close()


def emailing():
    logger.info('Run Task: [Emailing]')
    Config.DB_NAME='nasdaq100'
    s_nasdaq = Db(Config).session()
    Config.DB_NAME='tsxci'
    s_tsxci = Db(Config).session()
    Config.DB_NAME='sp100'
    s_sp100 = Db(Config).session()
    Config.DB_NAME='csi300'
    s_csi300 = Db(Config).session()
    sendMail(Config, s_nasdaq, s_tsxci, s_sp100, s_csi300)
    s_nasdaq.close()
    s_tsxci.close()
    s_sp100.close()


def aer(mode, report_type):
    logger.info('Run Task: [AER Data]')
    Config.DB_NAME='learning'
    db = Db(Config)
    s_learning = db.session()
    # Create table based on Models
    # db.create_all()
    try:
        fetch_aer(mode, report_type, s_learning)
        s_learning.close()
    except writeError as e:
        logger.error("%s - (Table: %s, Mode: %s)" % (e.value, report_type, mode))
        s_learning.close()
    except foundDup as e:
        logger.error("%s - (Table: %s, Mode: %s)" % (e.value, report_type, mode))
        s_learning.close()
    except:
        s_learning.close()
        pass
    # fetch_aer(mode, report_type, s_learning)
    # s_learning.close()
