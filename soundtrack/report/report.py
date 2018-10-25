import logging
import pandas as pd
from .ema import trend_potential
from .volume import unusual_volume
from .fiftytwoWeek import fiftytwo_week
from .pattern import find_pattern
from ..db.read import read_ticker
from ..models import Index, Quote, Report
import logging
logger = logging.getLogger('main.report')


def report(s, e):
    tickerL = read_ticker(s)
    # temp df for report with predefined columns
    columns=['symbol','yr_high','yr_low','downtrend','uptrend','pattern','high_volume','low_volume']
    dtypes =['str','int','int','int','int','str','int','int']
    report_df = df_empty(columns, dtypes)

    for ticker in tickerL:
        # read daily db return df
        # df = read_table_df_Engine(ticker_to,engine_dailydb)
        df = pd.read_sql(s.query(Quote).filter(Quote.symbol == ticker).statement, s.bind)
        print(df)
    #     # unusual volume stickers append to df
    #     report_df = report_df.append(unusual_volume(ticker,df),ignore_index=True)
    #     # unusual trend stickers append to df
    #     report_df = report_df.append(trend_potential(ticker,df),ignore_index=True)
    #     # 52w high/low/trending append to df
    #     report_df = report_df.append(fiftytwo_week(ticker,df),ignore_index=True)
    #     # decide if known pattern append to df
    #     report_df = report_df.append(find_pattern(ticker,df),ignore_index=True)
    #     # added industry name to each ticker, if ticker in index otherwise not add industry
    #     if not report_df.empty:
    #         if (equity in report_df['ticker'].unique()):
    #             report_df = report_df.append(ind_df,ignore_index=True)
    # # grouby using first() and NaN to Zero
    # report_df = groupby_na_to_zero(report_df, 'ticker')
    # # write df into db
    # report_df_to_sql(tname,report_df,engine_report)
#
#
#
#
def df_empty(columns, dtypes, index=None):
    assert len(columns)==len(dtypes)
    df = pd.DataFrame(index=index)
    for c,d in zip(columns, dtypes):
        df[c] = pd.Series(dtype=d)
    return df
