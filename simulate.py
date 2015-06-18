#!/usr/bin/env python2.7
'''market simulator


Data Structure
---------------

trades is a DataFrame [T, symbol, weight, price]:
interp. one trade record per line

T   symbol  weight  price
..  AAPL    0.1     20.75
...


investment is a float [0, +inf)


commission_rate is a float [0, +inf)
    

stockpos is a DataFrame [T symbol1 symbol2 ...]
interp. the time series of amount of stock holding in portfolio

T AAPL GOOG ...
.. 2    -1  ...


cashpos is a Series[T float]
interp. the time series of cash left in pocket

T
.. 100001.32
...


costs is a Series[T float]
interp. the time series of cumulative commissions of trading
T
.. 2.34
...


portfolio is composite of
    - cash is float
    - stocks is dict(symbol -> share amount)
         

order is a DataFrame
interp. the time sorted orders to buy/sell some shares of stocks

T   symbol      amount
..  AAPL        4.2

weight based order is a DataFrame
interp. buy/sell stocks to specified target percentage of portfolio value

T   symbol      percent
..  GOOG        0.05

'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-27 12:57:17 -0400'


import os
import sys
import logging
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


logging.basicConfig(level=logging.DEBUG)


INVEST = 1e6
PRICES_FILE = 'data/sp500.h5'
ORDER_FILE = 'data/orders.txt'
RESULTS_FILE = 'data/simulate_results.txt'
FIGURE_FILE = 'pic/simulate.png'
COMMITION_RATE = 0.001
LOG_DIR = 'log'


def load_minute_price(filename, key='/minute/close'):
    return pd.read_hdf(filename, key)


def load_daily_price(filename, key='/daily/close'):
    return pd.read_hdf(filename, key)


def load_order(order_file=ORDER_FILE, timezone='UTC'):
    '''load trade data from csv'''
    orders = pd.read_csv(order_file, parse_dates=True, index_col=0)
    orders.index = orders.index.tz_localize(timezone).tz_convert('UTC')
    #orders.columns = ['symbol', 'amount']
    return orders


def load_trades(trade_file, timezone='UTC'):
    '''load trade file from csv'''
    trades = pd.read_csv(trade_file, parse_dates=True, index_col=0)
    trades.index = trades.index.tz_localize(timezone).tz_convert('UTC')
    return trades


def get_trades_fast(orders, price_minute):
    '''given trade orders, query price data to produce trades'''
    #trading_time_index = price_minute.index
    assert price_minute.index.is_monotonic
    assert price_minute.columns.is_monotonic

    # retrieve matrix form of orders and price_minute
    # set second to be zero for order time list
    order_timelist = [t.replace(second=0) for t in orders.index.to_pydatetime()]
    order_times = pd.to_datetime(order_timelist).values
    #((orders.index.values.astype(int) // 60e9)*60e9).astype('datetime64[ns]')
    order_symbols = orders.symbol.values
    price_times = price_minute.index.values
    price_symbols = price_minute.columns.values

    # only process times and symbols in price_minute data
    tradable_index = np.in1d(order_symbols, price_symbols) & np.in1d(order_times, price_times)

    # find prices of tradable orders
    rows = price_times.searchsorted(order_times[tradable_index])
    cols = price_symbols.searchsorted(order_symbols[tradable_index])
    prices = price_minute.values[rows, cols]
    # identify nan from the resulting prices
    notnan_index = ~ np.isnan(prices)
    # construct dataframe trade
    trades = orders[tradable_index][notnan_index]
    trades['price'] = prices[notnan_index]
    trades.index.name = 'T'

    return trades


def market_simulate_weight_based(trades_wt, price_minute, investment, commission_rate):
    '''trades_wt, price_daily, investment, commission -> trades

    excute market trades, produce transactions

    Precondition:
    trades should be time-ordered

    
    '''

    cash = investment
    stocks = np.zeros_like(price_minute.iloc[0])
    symbol_numbers = price_minute.columns.values.searchsorted(trades_wt['symbol'])
    records = []
    for i, row_sn in enumerate(zip(trades_wt.iterrows(), symbol_numbers)):
        if i % 1000 == 0:
            print >>sys.stderr, i, '\r',
        row, sn = row_sn
        t, v = row
        s, w, p = v
        portfolio_value = (stocks * price_minute.loc[t]).sum() + cash
        amount = w * portfolio_value / p
        d_amount = amount - stocks[sn]

        # update portfolio
        stocks[sn] = amount
        cash = cash - d_amount * p * (1 + commission_rate)

        # record result
        record = (t, s, d_amount, p)
        records.append(record)
        #print record
    trades = pd.DataFrame.from_records(records)
    trades.columns = ['T', 'symbol', 'amount', 'price']
    trades.set_index('T', inplace=True)
    return trades


def get_trans(trades, rate, inplace=True):
    '''given trades and commission rate, produce transaction'''
    trans = trades if inplace else trades[:]
    trans.eval('cashvalue = amount * price')
    trans['commission'] = trans.cashvalue.abs() * rate
    return trans


# EOD positions
def get_trans_eod(trans):
    '''given excuted transactions, produce EOD transactions'''
    d_pos = trans.groupby('symbol').resample('D', how={'amount': sum, 'cashvalue': sum, 'commission': sum})
    trans_eod = d_pos.unstack('symbol').dropna(how='all')
    return trans_eod


def get_pos_eod_daily(trans_eod, price_daily, init=INVEST):
    '''given EOD transactions, produce EOD stock and cash positions with total commissions, use price data as shape'''
    trans_eod.reindex(price_daily.index)
    trans_eod[trans_eod.isnull()] = 0
    pos = trans_eod.cumsum()
    stockpos = pos.amount
    cashpos = init - (pos.cashvalue + pos.commission).sum(axis=1)
    costs = pos.commission.sum(axis=1)
    return stockpos, cashpos, costs


def get_stock_value(stockpos, price_daily):
    '''given stock positions, produce EOD stock values'''
    matching_prices = price_daily.loc[stockpos.index, stockpos.columns]
    return stockpos * matching_prices


def get_stock_total_values(stock_values):
    '''given EOD stock values, produce EOD total stock account values'''
    #trades['tot'] = trades.amount * trades.price
    return stock_values.sum(axis=1)


def get_values(stock_total_values, cashpos):
    '''pd.Series, pd.Series, pd.Series -> pd.Series
    given EOD total stock values and cash account values'''
    return stock_total_values + cashpos


def main():
    # parse command line arguments
    argp = argparse.ArgumentParser(
        description='Market simulator, provide order file or trade file, simulate market performance.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    argp.add_argument('-wt', '--weight-based', action='store_true', help='order file will contain target weight')
    argp.add_argument('-i', '--investment', type=float, default=INVEST, help='initial investment')
    argp.add_argument('-c', '--commission', type=float, default=COMMITION_RATE, help='commition rate')
    argp.add_argument('-pf', '--price-file', default=PRICES_FILE, help='price file in hdf5 format')
    argp.add_argument('-of', '--order-file', default=ORDER_FILE, help='order file')
    argp.add_argument('-rf', '--result-file', default=RESULTS_FILE, help='result file')
    argp.add_argument('-ff', '--figure-file', default=FIGURE_FILE, help='figure file')
    argp.add_argument('-tf', '--trade-file', default=None, help='trade file, if provided, skipping query price')
    argp.add_argument('-tz', '--time-zone', default='UTC', help='input file time zone, ex. US/Eastern')
    #argp.add_argument('-s', '--start-day', default=None, help='simulation start day')
    #argp.add_argument('-e', '--end-day', default=None, help='simulation end day')

    argp.add_argument('-nos', '--no-show', action='store_true', help='do not show figure')
    argp.add_argument('-log', '--log', action='store_true', help='output detailed information')
    argp.add_argument('-debug', action='store_true', help='enter interactive mode after running')
    args = argp.parse_args()


    if args.log:
        # prepare log directory
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)


    logging.info('loading data...')
    logging.debug('load daily data')
    price_daily = load_daily_price(args.price_file)
 
    if not args.trade_file:
        logging.debug('load minute data from {}'.format(args.price_file))
        price_minute = load_minute_price(args.price_file)

        logging.debug('load orders from {}'.format(args.order_file))
        orders = load_order(args.order_file, timezone=args.time_zone)
        logging.debug('read {} orders'.format(len(orders)))
        if args.log:
            orders.to_csv(LOG_DIR + '/orders.log')
        #orders = load_order(args.order_file).iloc[100000:150000]

        #trades = get_trades(orders, price_minute)
        trades = get_trades_fast(orders, price_minute)
        logging.debug('get {} trades'.format(len(trades)))
        if args.log:
            trades.to_csv(LOG_DIR + '/trades.log')
    else:
        trades = load_trades(args.trade_file, timezone=args.time_zone)
        logging.debug('read {} trades'.format(len(trades)))

    if args.weight_based:
        logging.info('calculation running on weight based mode')
        trades = market_simulate_weight_based(trades, price_minute, args.investment, args.commission)
        if args.log:
            trades.to_csv(LOG_DIR + '/trades_wt.log')
    trans = get_trans(trades, args.commission)
    trans_eod = get_trans_eod(trans)
    logging.info('begin EOD calculation...')
    stockpos, cashpos, costs = get_pos_eod_daily(trans_eod, price_daily, args.investment)
    logging.debug('get {} EOD positions'.format(len(stockpos)))

    if args.log:
        stockpos.to_csv(LOG_DIR + '/stockpos.log')
        cashpos.to_csv(LOG_DIR + '/cashpos.log')
        costs.to_csv(LOG_DIR + '/costs.log')

    stock_values = get_stock_value(stockpos, price_daily)
    stock_total_values = get_stock_total_values(stock_values)
    values = get_values(stock_total_values, cashpos)
    logging.info('calculation EOD finished')
    if args.debug:
        import interact
        interact.run(local=dict(locals(), **globals()))


    logging.info('saving results...')
    logging.debug('save result to {}'.format(args.result_file))
    values.to_csv(args.result_file)
    values.plot()
    logging.debug('save figure to {}'.format(args.figure_file))
    plt.savefig(args.figure_file)
    if not args.no_show:
        logging.debug('showing figures')
        plt.show()


if __name__ == "__main__":
    main()
