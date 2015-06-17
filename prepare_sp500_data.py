#!/usr/bin/env python2.7
'''prepare_data.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-26 14:59:39 -0400'


import sys
from backtest import load_bars_from_file
import pandas as pd


H5FILE = 'data/sp500.h5'
CSVFILE = 'data/sp500-close.csv'
DAILY_CSVFILE = 'data/sp500-close-daily.csv'
START = '2010-1-1'
END = '2015-5-1'


def main():
    # load stock list
    stocks = open('data/sp500.txt').read().splitlines()
    nstocks = len(stocks)
    
    # load only close prices
    prices = {}
    for i, stock in enumerate(stocks):
        print >>sys.stderr, '\r {}/{} '.format(i, nstocks),
        df = load_bars_from_file(stock, start=START, end=END)
        close = df['close']
        prices[stock] = close
    prices_df = pd.DataFrame(prices)

    # output
    print 'output to csv...'
    prices_df.to_csv(CSVFILE)
    print 'output to hdf...'
    pd.DataFrame(stocks).to_hdf(H5FILE, '/symbols', if_exists='replace')
    prices_df.to_hdf(H5FILE, '/minute/close', if_exists='replace')

    #prices_df = pd.read_csv('sp500_close.csv.gz', index_col='Date_Time', parse_dates=True)

    print 'saving daily data'
    prices_daily = prices_df.resample('D', how='last').dropna(how='all')
    prices_daily.to_hdf(H5FILE, '/daily/close', if_exists='replace')

    prices_daily.to_csv(DAILY_CSVFILE)


if __name__ == "__main__":
    main()


