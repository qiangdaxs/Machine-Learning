#!/usr/bin/env python2.7
'''eventstudy.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-06-05 10:18:32 -0400'


import pandas as pd
import simulate
import matplotlib.pyplot as plt
import numpy as np
import sys
import argparse
import logging

#import multiprocessing as mp
logging.basicConfig(level=logging.DEBUG)
BOUND = -0.2
PRICES_FILE = 'data/sp500.h5'
RETURNS_FILE = 'data/sp500_r.h5'
EVENT_FILE = 'data/event.csv'
RESULTS_FILE = 'data/eventstudy.txt'


#Signal is pd.DataFrame
SIGNAL_COLUMNS = ['symbol', 'article_sentiment', 'article_perception', 'overall_source_rank', 'event_impact_score']


def main():
    # handle command line
    argp = argparse.ArgumentParser(
        description='Event Study, provide order file or trade file, study price response.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    argp.add_argument('-pf', '--price-file', default=PRICES_FILE, help='price file in hdf5 format')
    argp.add_argument('-rf', '--return-file', default=EVENT_FILE, help='return file')
    argp.add_argument('-if', '--input-file', default=RETURNS_FILE, help='event file, two columns, [T, symbol]')
    #argp.add_argument('-s', '--start-day', default=None, help='simulation start day')
    #argp.add_argument('-e', '--end-day', default=None, help='simulation end day')
    argp.add_argument('-of', '--out-file', default=RESULTS_FILE, help='result file')
    args = argp.parse_args()

    # schedule calculation
    # load price file
    price_minute = simulate.load_minute_price(simulate.PRICES_FILE)
    return_data = pd.read_hdf(args.return_file, 'minute/return')
    price_daily = simulate.load_daily_price(simulate.PRICES_FILE)

    # load events
    events = pd.read_csv()

    # excute calculation
    study = event_study(events, price_minute, return_data, market_return_data, beta_data)

    # store results
    np.savetxt('study_as{}.txt'.format(BOUND), study)
    plt.plot(study)
    plt.savefig('study_as{}.png'.format(BOUND))
    plt.show()


def query_table(table, indexes, columns):
    '''Table, [index], [column] -> [value]

    query table and return table value fast
    
    >>> query_table(BETA_DATA, TIMES, SYMBOLS)
    array([ 1. , -0.2, -0.3])
    '''
    assert table.index.is_monotonic
    assert table.columns.is_monotonic
    row_numbers = table.index.values.searchsorted(indexes)
    col_numbers = table.columns.values.searchsorted(columns)
    return table.values[row_numbers, col_numbers]


def query_table_range(table, indexes, columns, lookback, lookforward):
    '''Table, [index], [column], int[0, +inf), int[0, +inf) -> values[(-lookback, lookforward) x columns]
    
    query table return nearby values
    
    >>> query_table_range(RETURN_DATA, pd.DatetimeIndex(['2012-9-12T14:11Z', '2012-9-12T14:12Z']), ['AAPL', 'GOOG'], lookback=1, lookforward=1)
    array([[ 1.  ,  1.01,  0.9 ],
           [ 0.92,  0.91,  0.8 ]])
    
    '''
    assert table.index.is_monotonic
    assert table.columns.is_monotonic
    row_numbers = table.index.values.searchsorted(indexes)
    col_numbers = table.columns.values.searchsorted(columns)
    values = table.values
    results = np.array([values[(i-lookback):(i+lookforward+1), j] for i, j in zip(row_numbers, col_numbers)])
    return results


def query_list_range(l, indexes, lookback, lookforward):
    '''Series, [index], int[0, +inf), int[0, +inf) -> values[(-lookback, lookforward) x indexes]
    
    query series of returns nearby values
    
    >>> query_list_range(MARKET_RETURNS, pd.DatetimeIndex(['2012-9-12T14:11Z', '2012-9-12T14:12Z']), lookback=1, lookforward=1)
    array([[ 0.1 , -0.1 ,  0.09],
           [-0.1 ,  0.09, -0.08]])
    
    '''
    assert l.index.is_monotonic
    row_numbers = l.index.values.searchsorted(indexes)
    values = l.values
    results = np.array([values[(i-lookback):(i+lookforward+1)] for i in row_numbers])
    return results


def event_study(events, price_minute, return_data, market_return_data, beta_data, n=5000, lookback=20, lookforward=20):
    '''

    '''

    betas = query_table(beta_data, events.index, events.columns)  # betas is DataFrame(time# x event#)
    market_returns = query_list_range(market_return_data, events.index, events.columns, lookback, lookforward)  # market_returns is DataFrame(time# x event#)
    actual_returns = query_table_range(return_data, events.index, events.columns, lookback, lookforward)
    expected_returns = betas * market_returns
    abnormal_returns = actual_returns - expected_returns

    # cumulative abnormal returns
    
    # calculate mean, std returns
    #study = np.zeros(n)
    #nsig = 0
    ##p = mp.Pool(8)
    #for i, v in enumerate(events.iteritems()):
        #t, s = v
        #if i % 10000 == 0:
            #print >> sys.stderr, i, '\r',
        #if t in price_minute.index:
            ##print t
            #p = price_minute.loc[t:, s].head(n).values
            #dp = p - p[0]
            #dp[np.isnan(dp)] = 0
            #try:
                #study = study + dp
            #except ValueError:
                #break
            #nsig += 1
    ##pp = np.array(study)
    ##pp = np.nansum(pp, axis=0)
    #print 'nsig=', nsig
    #return study / (nsig / 100)



if __name__ == "__main__":
    import doctest
    from test_libeventstudy import *
    doctest.testmod()

    #main()
