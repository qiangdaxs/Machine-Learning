#!/usr/bin/env python2.7
'''backtest1-online.py
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


start = '2012-8-25'
start = '2015-1-1'
#end = '2015-2-19'
end = '2015-2-18'
stocks = ['DLTR', 'SPY']


ind_data = local_csv('DLTR.csv', date_column = 'harvested_at', use_date_column_as_index = True)
#data = get_pricing(stocks, frequency='daily', start_date=start, end_date=end)
data = get_pricing(stocks, frequency='minute', start_date=start, end_date=end)
data.dropna(axis=1, inplace=True)


def initialize(context):
    context.stocks = symbols(stocks)
    context.upper_bound = 0.35
    context.lower_bound = -0.35


def handle_data(context, data):
    #now_minute = get_datetime().strftime('%Y-%m-%d')
    now_minute = get_datetime().strftime('%Y-%m-%d %H:%M')
    #print(now_minute)
    #for i, v in ind['2012-12-12'].iterrows():
    #print(ind_data[now_minute])
    for i, v in ind_data[now_minute].iterrows():
        #print(i)
        stock = v['entities_ticker_1']
        if stock in context.stocks:
            if (v['article_sentiment'] > context.upper_bound):
                order_target_percent(stock, 0.1)
                record(trade = 1)
            elif (v['article_sentiment'] < context.lower_bound):
                order_target_percent(stock, -0.1)
                record(trade = -1)


def analyze(context, perf):
    fig = pyplot.figure()
    
    # Make a subplot for portfolio value.
    ax1 = fig.add_subplot(211)
    perf.portfolio_value.plot(ax=ax1, figsize=(16, 12))
    ax1.set_ylabel('portfolio value in $')

    # Make another subplot showing our trades.
    ax2 = fig.add_subplot(212)
    perf['DLTR'].plot(ax=ax2, figsize=(16, 12))
    perf[['trade']].plot(ax=ax2)

    perf_trans = perf.ix[[t != [] for t in perf.transactions]]
    buys = perf_trans.ix[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
    sells = perf_trans.ix[
        [t[0]['amount'] < 0 for t in perf_trans.transactions]]

    # Add buy/sell markers to the second plot
    ax2.plot(buys.index, perf.short_mavg.ix[buys.index],
             '^', markersize=10, color='m')
    ax2.plot(sells.index, perf.short_mavg.ix[sells.index],
             'v', markersize=10, color='k')
    
    # Set figure metadata
    ax2.set_ylabel('price in $')
    pyplot.legend(loc=0)
    pyplot.show()
    

# Run algorithm
algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
algo_obj._analyze = analyze
algo_obj.run(data.transpose(2, 1, 0))
