#!/usr/bin/env python2.7
'''prepare_data.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-26 14:59:39 -0400'


from backtest import load_bars_from_file, load_bars
import pandas as pd


def main():
    START = '2012-8-1'
    END = '2015-3-1'
    stocks = open('data/sp500.csv').read().splitlines()

    prices = {}
    data = load_bars(stocks, start=START, end=END)
#    for i, stock in enumerate(stocks):
#        df = load_bars_from_file(stock, start=START, end=END)
#        close = df['close']
#        prices[stock] = close

#    prices_df = pd.DataFrame(prices)
#    prices_df.to_csv('sp500_all.csv')
    #prices_df.to_hdf('data/sp500_close.h5')
    data.to_hdf('data/sp500-all.h5', '/minute/all')


if __name__ == "__main__":
    main()


