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
import logging
import functools


start = '2012-8-25'
end = '2015-2-19'
#stocks = ['DLTR', 'GOOGL', 'SPY']
stocks = ['DLTR']
logging.basicConfig(level=logging.DEBUG)


#ind_data = pd.read_csv('data/NASDAQ100_MarketNeutral.csv', index_col = 'start_date', parse_dates=True)
ind_data = pd.read_csv('data/DLTR.csv', index_col = 'harvested_at', parse_dates=True)
start = datetime.strptime(start, '%Y-%m-%d')
end = datetime.strptime(end, '%Y-%m-%d')
data = load_bars_from_yahoo(stocks=stocks, start=start, end=end)

data = data.fillna(method='ffill', axis=2)
data = data.fillna(method='bfill', axis=2)

def initialize(context):
    context.stocks = stocks
    context.upper_bound = 0.30
    context.lower_bound = -0.30


def handle_data(context, data):
    ################# daily / minute switch ###################################
    now_minute = get_datetime().strftime('%Y-%m-%d')
    #now_minute = get_datetime().strftime('%Y-%m-%d %H:%M')
    ###########################################################################
    for i, v in ind_data[now_minute].iterrows():
        # iter through all the indicators in this minute
        stock = v['entities_ticker_1']
        nlong = 0
        nshort = 0
        if stock in context.stocks:
            # select stocks in the context

            # trade
            if (v['article_sentiment'] > context.upper_bound):
                #price = data[stock].price
                #logging.debug('[{}] trigger buy as={}'.format(i, v['article_sentiment']))
                #logging.debug('[{}] order_target_percent {} {} @{}'.format(i, stock, 0.1, price))
                order_target_percent(stock, 0.1)
                nlong += 1
            elif (v['article_sentiment'] < context.lower_bound):
                #price = data[stock].price
                #logging.debug('[{}] trigger sell as={}'.format(i, v['article_sentiment']))
                #logging.debug('[{}] order_target_percent {} {} @{}'.format(i, stock, -0.1, price))
                order_target_percent(stock, -0.1)
                nshort += -1
        record(long=nlong, short=nshort)


def analyze(context, perf, fig=3):
    # Make a subplot for portfolio value.
    pyplot.subplot(fig, 1, 1)
    perf.portfolio_value.plot(figsize=(16, 12))
    pyplot.ylabel('portfolio value in $')

    # Make another subplot of signal
    pyplot.subplot(fig, 1, 2)
    ind_data['article_sentiment'].plot()
    pyplot.axhline(context.upper_bound, color='k')
    pyplot.axhline(context.lower_bound)
    pyplot.ylabel('indicator')
    pyplot.legend(loc=0)

    # subplot of positions
    pyplot.subplot(fig, 1, 3)
    #pyplot.twinx()
    perf['long'].plot()
    perf['short'].plot()

    # plot stock price if needed
    if fig > 3:
        ax = pyplot.subplot(fig, 1, 4)
        data.transpose(2, 1, 0).price.plot(ax=ax)
        perf_trans = perf[[t != [] for t in perf.transactions]]
        buys = perf_trans[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
        sells = perf_trans[[t[0]['amount'] < 0 for t in perf_trans.transactions]]

        #import interact; interact.run(local=dict(locals(), **globals()))
        # Add buy/sell markers to the second plot
        pyplot.plot(buys.index, [x['transactions'][0]['price'] for i, x in buys.iterrows()], '^', markersize=10, color='m')
        pyplot.plot(sells.index, [x['transactions'][0]['price'] for i, x in sells.iterrows()], 'v', markersize=10, color='k')
        #pyplot.plot(buys.index, perf.portfolio_value.ix[buys.index], '^', markersize=10, color='m')
        #pyplot.plot(sells.index, perf.portfolio_value.ix[sells.index], 'v', markersize=10, color='k')

        
    pyplot.show()
    

# Run algorithm
algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
algo_obj._analyze = functools.partial(analyze, fig=4)
algo_obj.run(data)
