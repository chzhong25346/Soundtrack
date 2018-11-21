import logging
logger = logging.getLogger('main.trigger')


def bull_hivolume_uptrend(df):
    '''
    high volume and up trend
    return tickers
    '''
    try:
        return df[((df['high_volume']>0) | (df['support']>0)) & (df['uptrend']>0)].index.tolist()
    except Exception as e:
        logger.debug('bull_hivolume_uptrend: Missing Field in Report for Calculation!')
        pass


def bull_oneyrlow_doji_hivolume(df):
    '''
    52week low and has any doji and high_volume
    return tickers
    '''
    try:
        return df[(df['yr_low']>0) & (df['pattern'].str.contains("engulfing") | df['pattern'].str.contains("harami")) & (df['high_volume'] > 0) ].index.tolist()
    except Exception as e:
        logger.debug('bull_oneyrlow_doji_hivolume: Missing Field in Report for Calculation!')
        pass

####################


def bear_hivolume_downtrend(df):
    '''
    high volume and down trend
    return tickers
    '''
    try:
        return df[(df['downtrend']>0) & (df['high_volume']>0)].index.tolist()
    except Exception as e:
        logger.debug('bear_hivolume_downtrend: Missing Field in Report for Calculation!')
        pass


def bear_oneyrhigh_doji_downtrend(df):
    '''
    52week high and has any doji and down trend
    return tickers
    '''
    try:
        return df[(df['yr_high']>0) & (df['pattern'].str.contains("doji")) ].index.tolist()
    except Exception as e:
        logger.debug('bear_oneyrhigh_doji_downtrend: Missing Field in Report for Calculation!')
        pass
