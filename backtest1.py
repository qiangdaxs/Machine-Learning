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
import functools
import logging
logging.basicConfig(level=logging.DEBUG)


start = '2012-8-26'
end = '2015-2-19'
end = '2012-10-19'
#stocks = ['DLTR', 'GOOGL', 'SPY']
stocks = ['TSLA']

#df = pd.read_csv('data/1M_SP500/DLTR.csv', parse_dates=[['Date', 'Time']], index_col='Date_Time')
#df.index = df.index.tz_localize('US/Eastern').tz_convert('UTC')


ind_data = pd.read_csv('data/TSLA_Backtest (1).csv', index_col = 'start_date', parse_dates=True)
#ind_data = pd.read_csv('data/TSLA_Backtest (1).csv', index_col = 'harvested_at', parse_dates=True)
start = datetime.strptime(start, '%Y-%m-%d')
end = datetime.strptime(end, '%Y-%m-%d')
data = load_bars_from_yahoo(stocks=stocks, start=start, end=end)

data = data.fillna(method='ffill', axis=2)
data = data.fillna(method='bfill', axis=2)

def initialize(context):
    context.stocks = stocks
    context.upper_bound = 0.53
    context.lower_bound = -0.47


def handle_data(context, data):
    ################# daily / minute switch ###################################
    now_minute = get_datetime().strftime('%Y-%m-%d')
    #now_minute = get_datetime().strftime('%Y-%m-%d %H:%M')
    ###########################################################################
    nlong = 0
    nshort = 0
    for i, v in ind_data[now_minute].iterrows():
        # iter through all the indicators in this minute
        stock = v['symbol']
        #stock = v['entities_ticker_1']
        if stock in context.stocks:
            # select stocks in the context

            # trade
            if (v['article_sentiment'] > context.upper_bound):
                price = data[stock].price
                logging.debug('[{}] trigger buy {}@{} as={}'.format(i, stock, price, v['article_sentiment']))
                order_target_percent(stock, 1.)
                nlong += 1
                break
            elif (v['article_sentiment'] < context.lower_bound):
                price = data[stock].price
                logging.debug('[{}] trigger sell {}@{} as={}'.format(i, stock, price, v['article_sentiment']))
                order_target_percent(stock, 0.)
                nshort += -1
                logging.debug('[{}] @{} as={} '.format(now_minute, stock, v['article_sentiment']))
                break
    record(long=nlong, short=nshort)


def analyze(context, perf, fig=3):
    # Make a subplot for portfolio value.
    pyplot.subplot(fig, 1, 1)
    perf.portfolio_value.plot(figsize=(16, 12))
    pyplot.ylabel('portfolio value in $')
    pyplot.xlim([start, end])

    # Make another subplot of signal
    pyplot.subplot(fig, 1, 2)
    ind_data['article_sentiment'].plot()
    pyplot.axhline(context.upper_bound, color='k')
    pyplot.axhline(context.lower_bound)
    pyplot.ylabel('indicator')
    pyplot.legend(loc=0)
    pyplot.xlim([start, end])

    # subplot of positions
    pyplot.subplot(fig, 1, 3)
    perf['long'].plot()
    #pyplot.twinx()
    perf['short'].plot()
    pyplot.xlim([start, end])

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
        pyplot.xlim([start, end])

        
    pyplot.show()
    

# Run algorithm
algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
algo_obj._analyze = functools.partial(analyze, fig=4)
algo_obj.run(data)
#idd=pd.MultiIndex.from_tuples(zip(*[df.index, df.Symbol]))
#pdd.index=idd
#pdd.to_panel()
