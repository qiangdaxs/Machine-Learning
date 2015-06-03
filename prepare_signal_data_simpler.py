#!/usr/bin/env python2.7
'''prepare_signal_data_simpler.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-29 16:53:54 -0400'


import pandas as pd


def main():
    df = pd.read_hdf('data/sp500_signal.h5', '/signal')
    df2 = df[~ df['entities_ticker_1'].isin(['GOOG', 'AMZN', 'AAPL', 'YHOO', 'MSFT', 'WMT'])]
    df2.to_hdf('sp500-smaller-signal.h5', '/signal')


if __name__ == "__main__":
    main()


