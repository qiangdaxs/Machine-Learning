#!/usr/bin/env python2.7
'''backtest1.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-15 16:00:29 -0400'


import zipline
from zipline.api import order_target_percent, record, get_datetime
from zipline import TradingAlgorithm

import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
import pytz
from datetime import datetime
from zipline.utils.factory import load_bars_from_yahoo


start = '2012-8-25'
end = '2015-2-19'
stocks = ['DLTR', 'GOOGL', 'SPY']


ind_data = pd.read_csv('DLTR.csv', index_col = 'harvested_at', parse_dates=True)
start = datetime.strptime(start, '%Y-%m-%d')
end = datetime.strptime(end, '%Y-%m-%d')
data = load_bars_from_yahoo(stocks=stocks, start=start, end=end)
data.dropna(axis=1, inplace=True)


def initialize(context):
    context.stocks = stocks
    context.upper_bound = 0.30
    context.lower_bound = -0.30


def handle_data(context, data):
    #now_minute = get_datetime().strftime('%Y-%m-%d')
    now_minute = get_datetime().strftime('%Y-%m-%d %H:%M')
    for i, v in ind_data[now_minute].iterrows():
        # iter through all the indicators in this minute
        #print(i)
        stock = v['entities_ticker_1']
        nlong = 0
        nshort = 0
        if stock in context.stocks:
            # select stocks in the context

            # trade
            if (v['article_sentiment'] > context.upper_bound):
                order_target_percent(stock, 0.1)
                nlong += 1
            elif (v['article_sentiment'] < context.lower_bound):
                order_target_percent(stock, -0.1)
                nshort += -1
        record(long=nlong, short=nshort)


def analyze(context, perf):
    fig = pyplot.figure()
    
    # Make a subplot for portfolio value.
    ax1 = fig.add_subplot(211)
    perf.portfolio_value.plot(ax=ax1, figsize=(16, 12))
    ax1.set_ylabel('portfolio value in $')

    # Make another subplot showing our trades.
    ax2 = fig.add_subplot(212)
    ind_data['article_sentiment'].plot(ax=ax2)
    pyplot.twinx()
    perf['long'].plot(ax=ax2)
    perf['short'].plot(ax=ax2)

    perf_trans = perf.ix[[t != [] for t in perf.transactions]]
    buys = perf_trans.ix[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
    sells = perf_trans.ix[
        [t[0]['amount'] < 0 for t in perf_trans.transactions]]

    # Add buy/sell markers to the second plot
    ax1.plot(buys.index, perf.portfolio_value.ix[buys.index], '^', markersize=10, color='m')
    ax1.plot(sells.index, perf.portfolio_value.ix[sells.index], 'v', markersize=10, color='k')
    
    # Set figure metadata
    ax2.set_ylabel('indicator')
    pyplot.legend(loc=0)
    pyplot.show()
    

# Run algorithm
algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
algo_obj._analyze = analyze
algo_obj.run(data)
