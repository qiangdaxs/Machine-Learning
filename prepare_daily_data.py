#!/usr/bin/env python2.7
'''prepare_data.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-26 14:59:39 -0400'


from backtest import load_bars_from_file
import pandas as pd


def main():
    START = '2012-8-10'
    END = '2015-2-10'
    H5FILE = 'data/sp500.h5'
    stocks = open('data/sp500.csv').read().splitlines()

    prices_df = pd.read_csv('sp500_close.csv.gz', index_col='Date_Time', parse_dates=True)
    #prices = {}
    #for i, stock in enumerate(stocks):
        #df = load_bars_from_file(stock, start=START, end=END)
        #close = df['close']
        #prices[stock] = close

    #prices_df = pd.DataFrame(prices)
    #prices_df.to_csv('sp500_close.csv')
    

    pd.DataFrame(stocks).to_hdf(H5FILE, '/symbols', if_exists='replace')
    prices_df.to_hdf(H5FILE, '/minute/close', if_exists='replace')
    prices_daily = prices_df.resample('D', how='last').dropna(how='all')
    prices_daily.to_hdf(H5FILE, '/daily/close', if_exists='replace')

    daily = pd.read_hdf(H5FILE, '/daily/close')
    daily.to_csv('data/sp500_close_daily.csv')


if __name__ == "__main__":
    main()


