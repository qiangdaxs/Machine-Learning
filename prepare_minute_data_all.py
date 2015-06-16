#!/usr/bin/env python2.7
'''prepare_data.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-26 14:59:39 -0400'


import sys
from backtest import load_bars_from_file
import pandas as pd


def main():
    #START = '2010-1-1' END = '2015-5-1'
    START = END = None
    stocks = open('data/sp500.txt').read().splitlines()
    nstocks = len(stocks)

    prices = {}
    for i, stock in enumerate(stocks):
        print >>sys.stderr, '\r {}/{} '.format(i, nstocks),
        df = load_bars_from_file(stock, start=START, end=END)
        close = df['close']
        prices[stock] = close

    prices_df = pd.DataFrame(prices)
    print 'output to csv...'
    prices_df.to_csv('sp500_close.csv.gz')
    #print 'output to hdf...'
    #prices_df.to_hdf('data/sp500_close.h5', 'minute/close')


if __name__ == "__main__":
    main()


