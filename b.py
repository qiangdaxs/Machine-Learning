#!/usr/bin/env python2.7
'''a.py

'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-15 16:00:29 -0400'

# Import Zipline, the open source backester, and a few other libraries that we will use
import zipline
from zipline.api import order_target_percent, record, symbol, history, add_history, get_datetime
from zipline import TradingAlgorithm

import pytz
from datetime import datetime
import matplotlib.pyplot as pyplot
import numpy as np
# Load data from get_trades for AAPL
import pandas as pd


ind_data = local_csv('DLTR.csv', date_column = 'harvested_at', use_date_column_as_index = True)
#ind_data = pd.read_csv('DLTR.csv', index_col = 'harvested_at', parse_dates=True)
stocks = ['DLTR', 'GOOG_L', 'SPY']


def initialize(context):
    context.stocks = symbols(stocks)
    context.upper_bound = 0.35
    context.lower_bound = -0.35


def handle_data(context, data):
    #now_minute = get_datetime().strftime('%Y-%m-%d %H:%M')
    now_minute = get_datetime().strftime('%Y-%m-%d')
    #print(now_minute)
    #for i, v in ind['2012-12-12'].iterrows():
    #print(ind_data[now_minute])
    #for i, v in ind_data[now_minute].iterrows():
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


#start = datetime(2012, 8, 25, 0, 0, 0, 0, pytz.utc)
#end = datetime(2015, 2, 19, 0, 0, 0, 0, pytz.utc)
start = '2012-8-25'
end = '2015-2-19'
#from zipline.utils.factory import load_bars_from_yahoo
#data = load_bars_from_yahoo(stocks=['DLTR', 'GOOGL'], start=start, end=end)
data = get_pricing(
    stocks,
    frequency='daily',
    start_date=start,
    end_date=end
)
algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)

    # Run algorithm
    #data = get_pricing(
        #['DLTR', 'GOOG_L', 'SPY'],
        #start_date='2012-08-25',
        #end_date = '2015-02-19',
        #frequency='minute'
    #)
    #data.price.plot()
