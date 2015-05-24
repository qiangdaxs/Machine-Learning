#!/usr/bin/env python2.7
''' do some optimization
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-18 11:44:53 -0400'


import zipline
from zipline.api import order_target_percent, record, get_datetime
from zipline import TradingAlgorithm

import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
import pytz
from datetime import datetime
from zipline.utils.factory import load_bars_from_yahoo
from functools import partial
import backtest
from backtest import initialize_template, handle_data, load_bars
import logging


# setup logging
logging.basicConfig(level=logging.DEBUG)


def para2sharpe(para, data):
    initialize = partial(initialize_template, parameters=para, start=START, stocks=STOCKS)
    algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    result = algo_obj.run(data)
    score = result2sharpe(result)
    return score


def result2sharpe(result):
    '''extract performance from backtest result'''
    sharpe = (result.returns.mean()*252) / (result.returns.std() * np.sqrt(252))
    return sharpe


def main():
    global START
    global STOCKS
    START = '2014-1-4'
    END = '2015-2-19'
    #END = '2015-2-18'
    #STOCKS = ['DLTR', 'GOOGL', 'SPY']
    logging.debug('load stock list')
    #STOCKS = pd.read_csv('data/stocklist.csv', header=None).iloc[:, 0]
    STOCKS = pd.read_csv('data/sp500.csv', header=None).iloc[:, 0][1:4]
    #print STOCKS
    #uppers = np.linspace(0, 1, 11)
    #lowers = -uppers
    uppers = [0.35, 0.53]
    lowers = [-0.35, -0.47]

    # load data
    #ind_data = pd.read_csv('DLTR.csv', index_col = 'harvested_at', parse_dates=True)
    logging.debug('load indicator data')
    ind_data = pd.read_csv('data/NASDAQ100_MarketNeutral.csv', index_col = 'start_date', parse_dates=True)
    logging.debug('load stock prices')
    data = load_bars(STOCKS, START, END)
    backtest.ind_data = ind_data

    # Create a dictionary to hold all the results of our algorithm run
    all_sharpes = {}
    for upper, lower in zip(uppers, lowers):
        print upper, lower
        parameters = {
            'article_sentiment_upper': upper,
            'article_sentiment_lower': lower,
        }
        sharpe = para2sharpe(parameters, data)
        all_sharpes[upper] = sharpe

    #all_sharpes = pd.DataFrame(all_sharpes)
    #all_sharpes.index.name = "article sentiment upper"
    #all_sharpes.columns.name = "AAPL Weight"
    print all_sharpes


if __name__ == "__main__":
    main()
