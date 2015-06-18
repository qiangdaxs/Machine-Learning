#!/usr/bin/env python2.7
'''prepare_data.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-26 14:59:39 -0400'


import sys
from backtest import load_bars_from_file
import pandas as pd
import os


ORIGION_FILE = 'data/sp500-all-close.h5'
H5FILE = 'data/sp500.h5'
CSVFILE = 'data/sp500-close.csv'
DAILY_CSVFILE = 'data/sp500-close-daily.csv'
RETURN_FILE = 'data/sp500_r.h5'
START = '2012-1-1'
END = '2015-5-1'


def main():
    # load close prices of stocks
    if os.path.exists(ORIGION_FILE):
        prices_df = pd.read_hdf(ORIGION_FILE, 'minute/close')
        prices_df = prices_df[(prices_df.index <= END) & (prices_df.index >= START)]
    else:
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

    # do return file
    returns = prices_df.pct_change()
    returns.to_hdf(RETURN_FILE, 'minute/return')
    returns_daily = prices_daily.pct_change()
    returns_daily.to_hdf(RETURN_FILE, 'daily/return')

    # load & export prices of index
    print 'processing index files'
    spx = load_bars_from_file('SPX', start=START, end=END, path='data/1M_SP500/INDX/SPX.csv')['close']
    spy = load_bars_from_file('SPY', start=START, end=END, path='data/1M_SP500/INDX/SPY.csv')['close']
    djia = load_bars_from_file('DJIA', start=START, end=END, path='data/1M_SP500/INDX/DJIA.csv')['close']
    prices = dict(SPX=spx, SPY=spy, DJIA=djia)
    prices_idx_df = pd.DataFrame(prices)
    prices_idx_df.to_hdf(H5FILE, '/minute/close/index', if_exists='replace')
    prices_idx_daily = prices_idx_df.resample('D', how='last').dropna(how='all')
    prices_idx_daily.to_hdf(H5FILE, '/daily/close/index', if_exists='replace')
    market_returns = prices_idx_df.pct_change()
    market_returns_daily = prices_idx_daily.pct_change()
    market_returns.to_hdf(RETURN_FILE, 'minute/return/index')
    market_returns_daily.to_hdf(RETURN_FILE, 'daily/return/index')


if __name__ == "__main__":
    main()

