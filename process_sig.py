#!/usr/bin/env python2.7
'''process_sig.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-06-15 16:29:22 -0400'


import pandas as pd
#import argparse as ap
<<<<<<< HEAD
import sys


def main():
    START = '8/25/2012'
    END = '12/31/2012'
    #END = '5/25/2015'
    START = sys.argv[1]
    END = sys.argv[2]
    print START, END
    #symbols = open('data/NASDAQ100CompanyList.txt').read().splitlines()
    symbols = open('data/SP500Tickers.txt').read().splitlines()
    print 'read {} symbols'.format(len(symbols))
    df = pd.read_csv('data/Complete_backtest.csv.gz', nrows=100, index_col='harvested_at', parse_dates=True)
=======


START = '8/25/2012'
END = '12/31/2012'
SIGFILE = 'data/Complete_backtest.csv.gz'
SYMBOL_FILE = 


def main():
    #END = '5/25/2015'
    #symbols = open('data/NASDAQ100CompanyList.txt').read().splitlines()
    symbols = open('data/SP500Tickers.txt').read().splitlines()
    print 'read {} symbols'.format(len(symbols))
    df = pd.read_csv(, nrows=100, index_col='harvested_at', parse_dates=True)
>>>>>>> 79d3d0a6fbd64d88dc210e7721d8c701f642141d
    df = pd.read_csv('data/Complete_backtest.csv.gz', index_col='harvested_at', parse_dates=True, dtype=df.dtypes)
    print 'read {} lines from csv'.format(len(df))
    df_limit = df[(df.index >= START) & (df.index <= END) & (df.entities_ticker_1.isin(symbols))]
    print 'output {} lines from csv'.format(len(df_limit))
<<<<<<< HEAD
    df_limit.to_csv('sp500-signal-{}-{}.csv'.format(START, END))
=======
    df_limit.to_csv('2012sp500-signal.csv')
>>>>>>> 79d3d0a6fbd64d88dc210e7721d8c701f642141d


if __name__ == "__main__":
    main()


