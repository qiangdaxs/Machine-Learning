#!/usr/bin/env python2.7
'''simulate.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-27 12:57:17 -0400'


import pandas as pd
import matplotlib.pyplot as plt
import logging
import numpy as np
import argparse
import sys


logging.basicConfig(level=logging.DEBUG)
PRICES_FILE = 'data/sp500.h5'
ORDER_FILE = 'data/orders.txt'
RESULTS_FILE = 'data/results.txt'
COMMITION_RATE = 0.001


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


def do_transaction(t, symbol, amount, prices):
    '''timestamp, str, float, dataframe -> transaction

    return the transaction for given order, None for no transaction

    '''
    t0 = t.replace(second=0)
    #tt = t0 if t0 in self._trading_time_index else None
    #if tt:
    #if t0:
        #price = self.prices.loc[tt, symbol]
    try:
        price = prices.at[t0, symbol]
        if np.isnan(price):
            return None
        #return (tt, symbol, amount, price)
        return (t0, symbol, amount, price)
    except KeyError:
        return None


def get_trades(orders, price_minute):
    '''given trade orders, query price data to produce trades'''
    transactions = []
    #trading_time_index = price_minute.index

    for i, row in enumerate(orders.iterrows()):
        if i % 10000 == 0:
            print >>sys.stderr, 'trading...', i, '\r',
        t, v = row
        # t: time
        # v: [symbol, amount]
        # query trading price
        transaction = do_transaction(t, v['symbol'], v['amount'], price_minute)
        if transaction:
            #print transaction[0]
            transactions.append(transaction)
    trades = pd.DataFrame(transactions, columns=['T', 'symbol', 'amount', 'price'])
    trades.set_index('T', inplace=True)
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


def get_trans(trades, rate, inplace=True):
    '''given trades and commission rate, produce transaction'''
    trans = trades if inplace else trades[:]
    trans.eval('cash = -amount * price')
    trans['commission'] = trans.cash.abs() * rate
    return trans


# EOD positions
def get_trans_eod(trans):
    '''given excuted transactions, produce EOD transactions'''
    trans_eod = trans.groupby('symbol').resample('D', how={'amount': sum, 'cash': sum, 'commission': sum})
    return trans_eod


def get_pos_eod(trans_eod):
    '''given EOD transactions, produce EOD stock and cash positions'''
    d_pos = trans_eod.unstack('symbol').dropna(how='all')
    d_pos[d_pos.isnull()] = 0
    pos = d_pos.cumsum()
    stockpos = pos.amount
    cashpos = pos.cash.sum(axis=1)
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


def get_values(stock_total_values, cashpos, costs):
    '''pd.Series, pd.Series, pd.Series -> pd.Series
    given EOD total stock values and cash account values'''
    return stock_total_values + cashpos - costs


def main():
    # parse command line arguments
    argp = argparse.ArgumentParser(
        description='Market simulator, provide order file or trade file, simulate market performance.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    #argp.add_argument('-i', '--investment', type=float, default=INVEST, help='initial investment')
    argp.add_argument('-c', '--commission', type=float, default=COMMITION_RATE, help='commition rate')
    argp.add_argument('-pf', '--price-file', default=PRICES_FILE, help='price file in hdf5 format')
    argp.add_argument('-of', '--order-file', default=ORDER_FILE, help='order file')
    argp.add_argument('-tf', '--trade-file', default=None, help='trade file, if provided, skipping query price')
    argp.add_argument('-tz', '--time-zone', default='UTC', help='input file time zone, ex. US/Eastern')
    argp.add_argument('-v', '--verbose', default=False, help='output detailed information')
    #argp.add_argument('-s', '--start-day', default=None, help='simulation start day')
    #argp.add_argument('-e', '--end-day', default=None, help='simulation end day')
    #argp.add_argument('-rf', '--result-file', default=RESULTS_FILE, help='result file')
    args = argp.parse_args()

    logging.debug('load daily data')
    price_daily = load_daily_price(args.price_file)
 
    if not args.trade_file:
        logging.debug('load minute data from {}'.format(args.price_file))
        price_minute = load_minute_price(args.price_file)

        logging.debug('load orders from {}'.format(args.order_file))
        orders = load_order(args.order_file, timezone=args.time_zone)
        logging.debug('read {} orders'.format(len(orders)))
        if args.verbose:
            print orders
        #orders = load_order(args.order_file).iloc[100000:150000]

        #trades = get_trades(orders, price_minute)
        trades = get_trades_fast(orders, price_minute)
        logging.debug('get {} trades'.format(len(trades)))
        if args.verbose:
            print trades
    else:
        trades = load_trades(args.trade_file, timezone=args.time_zone)
        logging.debug('read {} trades'.format(len(trades)))

    trans = get_trans(trades, args.commission)

    # EOD processes begin
    logging.info('begin EOD calculation...')
    trans_eod = get_trans_eod(trans)
    stockpos, cashpos, costs = get_pos_eod(trans_eod)
    logging.debug('get {} EOD positions'.format(len(stockpos)))
    if args.verbose:
        print stockpos
    stock_values = get_stock_value(stockpos, price_daily)
    stock_total_values = get_stock_total_values(stock_values)
    values = get_values(stock_total_values, cashpos, costs)
    logging.info('calculation EOD finished')
    values.plot()
    plt.show()


if __name__ == "__main__":
    main()


#def test():
    #import doctest
    #doctest.testmod()
    ##sig = pd.read_hdf('data/sp500-smaller-signal.h5', '/signal')['2012-9':]
    ##sample_trades = sig.iloc[:, 0:3]
    ##sample_trades.columns = ['symbol', 'amount', 'price']
    ##sample_trades.dropna(inplace=True)
    ##sample_trades['tot'] = sample_trades.amount * sample_trades.price
    ###sample_trades = pd.read_csv(trade_csv, index_col=0, parse_dates=True)
    ##tm = sample_trades.groupby('symbol').resample('D', how='sum')
    ###print sample_trades.price * sample_trades.amount
    ##tm.unstack('symbol')

