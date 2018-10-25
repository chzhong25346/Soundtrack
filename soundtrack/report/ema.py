import logging
logger = logging.getLogger('main.ema')


def trend_potential(ticker, df):
    '''
    require df
    return up,down,crossover lists
    return dic
    '''
    ema21 = ema(df,21)
    ema5 = ema(df,5)
    today = df.iloc()[-1]
    range = (ema5/ema21)-1
    if (-0.005<=range<=0 and today['close']>=ema5):
        return {'ticker':ticker,'uptrend':True}
    elif (0.005>=range>=0 and today['close']<=ema5):
        return {'ticker':ticker,'downtrend':True}


def ema(df, span):
    '''
    pick 3M data for analysis and calculate ewm
    return today's ema
    '''
    df = df.sort_index(ascending=True).last("3M")
    df = df['adjusted close'].ewm(span=span, adjust=False).mean()

    return df.loc[df.index.max()]
