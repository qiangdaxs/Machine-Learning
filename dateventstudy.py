#!/usr/bin/env python3.3
'''test_libeventstudy.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2013-06-23 21:10:42 -0400'


import pandas as pd
from StringIO import StringIO


# Data Structures


TIMES = pd.date_range('2012-9-12', periods=3, tz='UTC')
SYMBOLS = 'AAPL MSFT GOOG'.split(' ')


# BetaData is pd.DataFrame(time(daily) x symbol -> float)
# interp. daily updated beta of all the symbols

BETA_DATA = pd.read_table(
    StringIO('''\
        T   AAPL    GOOG    MSFT
2012-9-12   1.0     0.9     0.3
2012-9-13   0.3     -0.1    -0.2
2012-9-14   0.9     -0.3    -0.1
2012-9-15   0.2     0.8     -0.1
'''), parse_dates=True, sep='\s+', index_col=0)
BETA_DATA.index = BETA_DATA.index.tz_localize('UTC')


# Events is pd.DataFrame(time x symbol -> str)
# interp. event list specify event happening time and related symbol

EVENTS = pd.read_table(
    StringIO('''\
        T   symbol
2012-9-12   AAPL
2012-9-13   MSFT
2012-9-14   GOOG
'''), parse_dates=True, sep='\s+', index_col=0)


# ReturnData is pd.DataFrame(time(minute) x symbol -> float)
# interp. actual total returns for different stocks

RETURN_DATA = pd.read_table(
    StringIO('''\
            T   AAPL    GOOG    MSFT
2012-9-12T14:10Z  1.0     1.09    1.03
2012-9-12T14:11Z  1.01    0.92    1.09
2012-9-12T14:12Z  0.9     0.91    1.1
2012-9-12T14:13Z  0.8     0.8     1.1
'''), parse_dates=True, sep='\s+', index_col=0)


# Returns is pd.Series(time(minute) -> float)
# interp. market returns time series

MARKET_RETURNS = pd.read_table(
    StringIO('''\
            T      SPY
2012-9-12T14:10Z  0.1
2012-9-12T14:11Z  -0.1
2012-9-12T14:12Z  0.09
2012-9-12T14:13Z  -0.08
'''), parse_dates=True, sep='\s+', index_col=0).SPY
