from .utils.config import Config
from .db.db import Db
from .db.mapping import map_index, map_quote, map_report
from .db.write import bulk_save
from .db.read import read_ticker, has_index, read_exist
from .email.email import sendMail
from .report.report import report
from .report.optimize import optimize
from .simulation.simulator import simulator
import logging
import logging.config
import getopt
import time
import math
import os, sys
logging.config.fileConfig('soundtrack/log/logging.conf')
logger = logging.getLogger('main')


def main(argv):
    time_start = time.time()
    try:
        opts, args = getopt.getopt(argv,"u:rse",["update=", "report=", "simulate=", "emailing="])
    except getopt.GetoptError:
        print('run.py -u <full|compact|fix> <nasdaq100|tsxci|sp100>')
        print('run.py -r <nasdaq100|tsxci|sp100>')
        print('run.py -s <nasdaq100|tsxci|sp100>')
        print('run.py -e')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run.py -u <full|compact|fix>  <nasdaq100|tsxci|sp100>')
            print('run.py -r <nasdaq100|tsxci|sp100>')
            print('run.py -s <nasdaq100|tsxci|sp100>')
            print('run.py -e')
            sys.exit()
        elif (opt == '-u' and len(argv) != 3):
            print('run.py -u <full|compact|fix>  <nasdaq100|tsxci|sp100>')
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
            elif(arg == 'fix'):
                index_name = argv[2]
                type = 'compact'
                today_only = True
                update(type, today_only, index_name, fix=True)  # Compact update for today
        elif opt in ("-r", "--report"):  # Report
            index_name = argv[1]
            analyze(index_name)
        elif opt in ("-s", "--simulate"): # Simulate
            index_name = argv[1]
            simulate(index_name)
        elif opt in ("-e", "--emailing"): # Emailing
            emailing()
    elapsed = math.ceil((time.time() - time_start)/60)
    logger.info('Program took ' + str(elapsed) + ' minutes to run')


def update(type, today_only, index_name, fix=False):
    logger.info('Run Task:[%s %s UPDATE]' % (index_name, type))
    Config.DB_NAME=index_name
    db = Db(Config)
    s = db.session()
    e = db.get_engine()
    # Create table based on Models
    db.create_all()
    if has_index(s) == None:
        # Fetch/Mapping/Write Index
        bulk_save(s, map_index(index_name))
    tickerL = read_ticker(s)
    for ticker in tickerL:
        if (fix == True and read_exist(s, ticker) == False):
            try:
                logger.info('Fixing: %s' % (ticker))
                model_list = map_quote(Config,ticker,type,today_only,index_name)
                bulk_save(s, model_list)
            except:
                logger.error('Unable to fix: %s' % (ticker))
        elif(fix == False):
            try:
                logger.info('Processing: %s' % (ticker))
                model_list = map_quote(Config,ticker,type,today_only,index_name)
                bulk_save(s, model_list)
            except:
                logger.error('Unable to process: %s' % (ticker))
    s.close()


def analyze(index_name):
    logger.info('Run Task: [Reporting]')
    Config.DB_NAME=index_name
    db = Db(Config)
    s = db.session()
    e = db.get_engine()
    # Create table based on Models
    db.create_all()
    df = report(s)
    model_list = map_report(Config,df)
    bulk_save(s, model_list)

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
    db.create_all()
    simulator(s)
    s.close()


def emailing():
    logger.info('Run Task: [Emailing]')
    Config.DB_NAME='nasdaq100'
    db_nasdaq = Db(Config)
    s_nasdaq = db_nasdaq.session()
    Config.DB_NAME='tsxci'
    db_tsxci = Db(Config)
    s_tsxci = db_tsxci.session()
    Config.DB_NAME='sp100'
    db_sp100 = Db(Config)
    s_sp100 = db_sp100.session()
    sendMail(Config, s_nasdaq, s_tsxci, s_sp100)
    s_nasdaq.close()
    s_tsxci.close()
    s_sp100.close()
