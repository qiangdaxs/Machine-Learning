#!/usr/bin/env python2.7
'''prepare_signal_data.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-27 03:33:45 -0400'


import pandas as pd


def main():
    print 'loading csv file...'

    #entities_ticker_1               object
    #article_sentiment              float64
    #event_source_rank_1              int64
    #event_impact_score_entity_1      int64

    df = pd.read_csv('data/sp500_cut1.csv', index_col=0, parse_dates=True, nrows=9)
    dtype = df.dtypes
    #df = pd.read_csv('data/sp500_cut1.csv', index_col=0, parse_dates=True, dtype=dtype)
    #print 'sort'
    #df.sort()
    #stocks = open('data/sp500.csv').read().splitlines()
    #print('filtering...')
    #df2 = df[df['entities_ticker_1'].isin(stocks)]
    #print('saving...')
    #df2.to_csv('sp500_signal.csv')
    df = pd.read_csv('data/sp500_signal.csv', index_col=0, parse_dates=True)
    df.iloc[:, 2] = df.iloc[:, 2].convert_objects(convert_numeric=True)
    df.to_hdf('sp500_signal.h5', '/signal')



if __name__ == "__main__":
    main()


