import logging
from .rules import *
logger = logging.getLogger('main.pattern')


def find_pattern(ticker, df):
    '''
    find pattern according pattern rules
    and return dict to report.py
    '''
    if (fallingThreeMethods(df)):
        return {'ticker':ticker,'pattern':'Falling Three Methods'}
    elif (eveningDojiStar(df)):
        return {'ticker':ticker,'pattern':'evening doji star'}
    elif (eveningStar(df)):
        return {'ticker':ticker,'pattern':'evening star'}
    elif (abandonedBaby(df)):
        return {'ticker':ticker,'pattern':'abandoned baby'}
    elif (darkCloudCover(df)):
        return {'ticker':ticker,'pattern':'dark cloud cover'}
    elif (downsideTasukiGap(df)):
        return {'ticker':ticker,'pattern':'downside tasuki gap'}
    elif(longLeggedDoji(df)):
        return {'ticker':ticker,'pattern':'long legged doji'}
    elif(gravestoneDoji(df)):
        return {'ticker':ticker,'pattern':'gravestone doji'}
    elif(dragonflyDoji(df)):
        return {'ticker':ticker,'pattern':'dragonfly doji'}
    elif (doji(df)):
        return {'ticker':ticker,'pattern':'doji'}
    elif (engulfing(df)):
        return {'ticker':ticker,'pattern':'engulfing'}
    elif (hammer(df)):
        return {'ticker':ticker,'pattern':'hammer'}
    elif (invertedHammer(df)):
        return {'ticker':ticker,'pattern':'inverted hammer'}
    elif (haramiCross(df)):
        return {'ticker':ticker,'pattern':'harami cross'}
    elif (harami(df)):
        return {'ticker':ticker,'pattern':'harami'}
    elif (longBody(df)):
        return {'ticker':ticker,'pattern':'long body'}
    elif (marubozu(df)):
        return {'ticker':ticker,'pattern':'marubozu'}
