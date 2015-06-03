#!/usr/bin/env python2.7
'''simulate.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-27 12:57:17 -0400'


import pandas as pd
import matplotlib.pyplot as plt
import logging
import numpy as np


logging.basicConfig(level=logging.DEBUG)
SP500_FILE = 'data/sp500.h5'
SIGNAL_FILE = 'data/sp500-smaller-signal.h5'


def test():
    import doctest
    doctest.testmod()
    #sig = pd.read_hdf('data/sp500-smaller-signal.h5', '/signal')['2012-9':]
    #sample_trades = sig.iloc[:, 0:3]
    #sample_trades.columns = ['symbol', 'amount', 'price']
    #sample_trades.dropna(inplace=True)
    #sample_trades['tot'] = sample_trades.amount * sample_trades.price
    ##sample_trades = pd.read_csv(trade_csv, index_col=0, parse_dates=True)
    #tm = sample_trades.groupby('symbol').resample('D', how='sum')
    ##print sample_trades.price * sample_trades.amount
    #tm.unstack('symbol')


def load_minute_price(filename, key='/minute/close'):
    return pd.read_hdf(filename, key)


def load_daily_price(filename, key='/daily/close'):
    return pd.read_hdf(filename, key)


def load_trade(signal_file=SIGNAL_FILE, key='/signal'):
    ##TODO: load real trades
    ### Simulated trades
    sig = pd.read_hdf(signal_file, key)
    sample_trades = sig.iloc[:, 0:2]
    
    sample_trades.columns = ['symbol', 'amount']
    return sample_trades


def do_transaction(t, symbol, amount, prices):
    '''return the transaction for given order, None for no transaction

    timestamp, str, float, dataframe -> transaction
    '''
    t0 = t.replace(second=0)
    #tt = t0 if t0 in self._trading_time_index else None
    #if tt:
    #if t0:
        #price = self.prices.loc[tt, symbol]
    try:
        price = prices.loc[t0, symbol]
        if np.isnan(price):
            print (t0, symbol, amount, price)
        #return (tt, symbol, amount, price)
        return (t0, symbol, amount, price)
    except KeyError:
        return None


def get_trans(trades, price_minute):
    '''process trade orders and produce transactions'''
    transactions = []
    #trading_time_index = price_minute.index

    for t, v in trades.iterrows():
        # t: time
        # v: [symbol, amount]
        # query trading price
        transaction = do_transaction(t, v['symbol'], v['amount'], price_minute)
        if transaction:
            #print transaction[0]
            transactions.append(transaction)
    trans = pd.DataFrame(transactions, columns=['T', 'symbol', 'amount', 'price'])
    trans.set_index('T', inplace=True)
    return trans


# EOD positions
def get_stockpos(trans):
    '''given excuted transactions, produce EOD stock positions'''
    ##TODO
    trans_eod = trans.groupby('symbol').resample('D', how={'amount': sum}).amount
    d_stockpos = trans_eod.unstack('symbol').dropna(how='all')
    d_stockpos[d_stockpos.isnull()] = 0
    stockpos = d_stockpos.cumsum()
    return stockpos


def get_cashpos(trans):
    pass


def get_stock_value(stockpos, price_daily):
    ##TODO
    matching_prices = price_daily.loc[stockpos.index]
    return stockpos * matching_prices


def get_stock_total_values(stock_values):
    ##TODO
    #trades['tot'] = trades.amount * trades.price
    pass


def get_values(stock_total_values, cashpos):
    ##TODO
    pass



def main():
    logging.info('loading...')
    logging.debug('load minute data')
    price_minute = load_minute_price(SP500_FILE)
    logging.debug('load daily data')
    price_daily = load_daily_price(SP500_FILE)
    logging.debug('load all the trades')
    ##TODO: use all data here
    #trades = load_trade()
    trades = load_trade().iloc[:50000]
    logging.info('loading finished')
    logging.info('begin calculation...')
    trans = get_trans(trades, price_minute)
    # EOD positions
    stockpos = get_stockpos(trans)
    cashpos = get_cashpos(trans)
    stock_values = get_stock_value(stockpos, price_daily)
    stock_total_values = get_stock_total_values(stock_values)
    values = get_values(stock_total_values, cashpos)
    logging.info('calculation finished')
    #values.plot()
    #plt.show()


if __name__ == "__main__":
    test()
    #main()
