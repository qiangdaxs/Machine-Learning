#!/usr/bin/env python2.7
'''gen-sig.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-06-11 18:48:44 -0400'


import pandas as pd
import numpy as np


SIGNAL_FILE = 'data/sp500_signal.h5'
SIGNAL_FILE_KEY = 'signal'
ORDER_FILE = 'data/gensig-orders.txt'


# Parameter is dict
# interp. the parameter for signal generating
PARA = dict(
    as_upper = 0.8,
    as_lower = -0.8,
)


# Signal is pd.DataFrame(time x [metrices])
# interp. one market news per line
from io import BytesIO
SIGNAL_DATA = pd.read_csv(BytesIO('''\
    harvested_at        entities_ticker_1   article_sentiment
2013-1-1T14:31:15Z      AAPL                0.1
2013-1-1T15:21:29Z      GOOG                0.2
2013-1-1T17:11:04Z      MSFT                -0.4
'''), sep='\s+', parse_dates=True, index_col='harvested_at')


ORDER_AAPL = pd.read_csv(BytesIO('''\

harvested_at            amount  symbol
2013-01-01T14:31:15Z     1       AAPL
'''), sep='\s+', parse_dates=True, index_col='harvested_at')


def main():
    # read signal file SIGNAL_FILE
    #lo = PARA['as_lower']
    #hi = PARA['as_upper']
    signal = pd.read_hdf(SIGNAL_FILE, SIGNAL_FILE_KEY)

    # run strategy and generate buy/sell signal
    orders = make_orders(1.0, 'article_sentiment > 0.94 and event_impact_score_entity_1 > 0.7', signal)
    orders2 = make_orders(-1.0, 'article_sentiment < -0.55 and event_impact_score_entity_1 > 0.7', signal)
    orders = pd.concat([orders, orders2]).sort()
    orders.to_csv('data/orders.csv')


def make_orders(amount, eval_string, signal):
    '''float, str, Signal -> Orders
    
    using eval_string to generate orders from signal

    #>>> signal = pd.read_hdf(SIGNAL_FILE, SIGNAL_FILE_KEY)
    >>> (make_orders(1.0, 'article_sentiment > -0.2 and article_sentiment < 0.2', SIGNAL_DATA) == ORDER_AAPL).all().all()
    True
    
    '''
    
    select = signal.eval(eval_string).values

    try:
        symbols = signal['entities_ticker_1']
    except KeyError:
        import warnings
        warnings.warn('no entities_ticker_1 column, use symbol column instead')
        symbols = signal['symbol']
    dates = signal.index
    orders = pd.DataFrame(dict(symbol=symbols[select], amount=amount), index=dates[select])
    return orders


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    main()
