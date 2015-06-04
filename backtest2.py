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
from datetime import datetime, timedelta
from zipline.utils.factory import load_bars_from_yahoo
import functools
import logging


# setup logging
logging.basicConfig(level=logging.DEBUG)


# Override load market data from yahoo
def local_market_data(bm_symbol='GSPC'):
    '''return market data from local dataset
    '''
    import pickle
    try:
        tbill_file = 'data/tbill.pickle'
        gspc_file = 'data/gspc.pickle'
        tbill = pickle.load(open(tbill_file))
        gspc = pickle.load(open(gspc_file))
    except:
        gspc, tbill = zipline.data.loader.load_market_data()
        pickle.dump(gspc, open(gspc_file, 'wb'))
        pickle.dump(tbill, open(tbill_file, 'wb'))
    return gspc, tbill
zipline.data.loader.load_market_data = local_market_data
reload(zipline.finance.trading)


MINUTE_TEST = True


def load_bars_from_file(stock, start=None, end=None):
    '''load pricing data from single file
    str, str, str -> pd.DataFrame
    
    '''
    path = 'data/1M_SP500/{}.csv'.format(stock)
    logging.debug('load stock from {}'.format(path))
    prices = pd.read_csv(path, parse_dates=[['Date', 'Time']], index_col='Date_Time')
    prices.index = prices.index.tz_localize('US/Eastern').tz_convert('UTC')
    if start is not None:
        prices = prices[start:end]
    prices.columns=['symbol', 'open', 'high', 'low', 'close', 'volume']
    prices['price'] = prices['close']
    return prices


def load_bars(stocks, start, end, fillna=True):
    '''load pricing data from file, default fill NaN
    [str], str, str -> pd.Panel
    
    data is Panel(stocks x time x bars)'''
    stock2price_dic = {stock: load_bars_from_file(stock, start, end) for stock in stocks}
    data = pd.Panel(stock2price_dic)
    if fillna:
        data = data.fillna(method='ffill', axis=2)
        data = data.fillna(method='bfill', axis=2)
    return data


def initialize_template(context, parameters, stocks, start):
    context.stocks = stocks
    context.last_ind_time = start
    context.parameters = parameters


if MINUTE_TEST:
    NEXT_DELTA = timedelta(minutes=1)
else:
    NEXT_DELTA = timedelta(days=1)

def handle_data(context, data):
    nlong = 0
    nshort = 0
    #global nlong
    #global nshort
    now = get_datetime()
    now_next = now + NEXT_DELTA
    #now_minute = get_datetime().strftime('%F %R')
    #for i, v in ind_data[(context.last_ind_time <= ind_data.index) & (ind_data.index < now_next)].iterrows():
    for i, v in ind_data[(now <= ind_data.index) & (ind_data.index < now_next)].iterrows():
        # iter through all the indicators from last unprocessed indicator to the end of this minute
        # load stock ticker
        try:
            stock = v['entities_ticker_1']
        except:
            import warnings
            warnings.warn('column name "symbol" used instead of "entities_ticker_1" in indicator csv')
            stock = v['symbol']

        if stock in context.stocks:
            # select stocks in the context
            #print i, stock, v['article_sentiment']
            if (v['article_perception'] > context.parameters['article_perception_upper']) and (v['impact'] > context.parameters['impact_upper']) and (v['sourcerank'] > context.parameters['sourcerank_upper']):
            #if (v['article_sentiment'] > context.parameters['article_sentiment_upper']):
                price = data[stock].price
                logging.debug('[{}] trigger long {}@{} as={}'.format(i, stock, price, v['article_sentiment']))
                order_target_percent(stock, 1.)
                nlong += 1
            elif (v['article_perception'] < context.parameters['article_perception_lower']) and (v['impact'] > context.parameters['impact_lower']) and (v['sourcerank'] > context.parameters['sourcerank_lower']):
            #elif (v['article_sentiment'] < context.parameters['article_sentiment_lower']):
                price = data[stock].price
                logging.debug('[{}] trigger short {}@{} as={}'.format(i, stock, price, v['article_sentiment']))
                #logging.debug('[{}] @{} as={} '.format(now_minute, stock, v['article_sentiment']))
                order_target_percent(stock, -1.)
                nshort += -1

    context.last_ind_time = now_next

    record(long=nlong, short=nshort)


def analyze(context, perf, plot_stock=False):
    fig_num = 4 if plot_stock else 3
    # Make a subplot for portfolio value.
    pyplot.subplot(fig_num, 1, 1)
    perf.portfolio_value.plot(figsize=(16, 12))
    pyplot.ylabel('portfolio value in $')
    pyplot.xlim([START, END])

    # Make another subplot of signal
    pyplot.subplot(fig_num, 1, 2)
    ind_data['article_perception'].plot()
    pyplot.axhline(context.parameters['article_perception_upper'], color='k')
    pyplot.axhline(context.parameters['article_perception_lower'])
    pyplot.ylabel('indicator')
    pyplot.legend(loc=0)
    pyplot.xlim([START, END])

    # subplot of positions
    pyplot.subplot(fig_num, 1, 3)
    perf['long'].plot()
    #pyplot.twinx()
    perf['short'].plot()
    pyplot.ylabel('position change')
    pyplot.xlim([START, END])

    # plot stock price if needed
    if plot_stock:
        ax = pyplot.subplot(fig_num, 1, 4)
        data.transpose(2, 1, 0).price.plot(ax=ax)
        perf_trans = perf[[t != [] for t in perf.transactions]]
        buys = perf_trans[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
        sells = perf_trans[[t[0]['amount'] < 0 for t in perf_trans.transactions]]

        # Add buy/sell markers to the second plot
        pyplot.plot(buys.index, [x['transactions'][0]['price'] for i, x in buys.iterrows()], '^', markersize=10, color='m')
        pyplot.plot(sells.index, [x['transactions'][0]['price'] for i, x in sells.iterrows()], 'v', markersize=10, color='k')
        #pyplot.plot(buys.index, perf.portfolio_value.ix[buys.index], '^', markersize=10, color='m')
        #pyplot.plot(sells.index, perf.portfolio_value.ix[sells.index], 'v', markersize=10, color='k')
        pyplot.xlim([START, END])
        pyplot.ylabel('stock quote')
        
    pyplot.savefig('backtest.png')
    pyplot.show()
    

def main():
    # used by all
    global ind_data

    # used by analysis
    global data
    global START
    global END

    START = '2012-8-25'
    #START = '2012-9-14'
    END = '2015-5-1'
    #END = '2012-09-19'
    #STOCKS = ['DLTR', 'GOOGL']
    #STOCKS = ['DLTR']
    #STOCKS = ['AAPL', 'DLTR']
    #STOCKS = list(pd.read_csv('data/sp500.csv', header=None).iloc[:, 0])
    #STOCKS = open('data/sp500.csv').read().splitlines()
    #STOCKS = list(pd.read_csv('data/stocklist.csv', header=None).iloc[:, 0])
    STOCKS = ['AVP']

    parameters = dict(
        article_perception_upper = 60, 
        article_perception_lower = -60, 
        impact_upper = 70,
        impact_lower = 70,
        sourcerank_upper = 5, 
        sourcerank_lower = 5, 
        #article_sentiment_upper = 0.53,
        #article_sentiment_lower = -0.47
    )
    initialize = functools.partial(initialize_template, parameters=parameters, stocks=STOCKS, start=START)

    #ind_data = pd.read_csv('data/TSLA_Backtest (1).csv', index_col = 'start_date', parse_dates=True)
    #ind_data = pd.read_csv('data/DLTR_ind.csv', index_col='harvested_at', parse_dates=True)
    ind_data = pd.read_csv('data/perception_full_AVP.csv', index_col='harvested_at', parse_dates=True)
    #ind_data = pd.read_csv('data/NASDAQ100_MarketNeutral.csv', index_col='start_date', parse_dates=True)
    #ind_data = pd.read_csv('data/NASDAQ100_MarketNeutral.csv', index_col='start_date', parse_dates=True)
    #START = datetime.strptime(START, '%Y-%m-%d')
    #END = datetime.strptime(END, '%Y-%m-%d')
    if MINUTE_TEST:
        data = load_bars(stocks=STOCKS, start=START, end=END)
    else:
        data = load_bars_from_yahoo(stocks=STOCKS, start=START, end=END)

    # Run algorithm
    algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    algo_obj._analyze = functools.partial(analyze, plot_stock=True)
    algo_obj.run(data)


if __name__ == "__main__":
    main()
