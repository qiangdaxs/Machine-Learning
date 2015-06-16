#!/usr/bin/env python2.7
'''prepare_sp500_returns.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-26 14:59:39 -0400'


import sys
from backtest import load_bars_from_file
import pandas as pd

prices = pd.read_hdf('data/sp500.h5', 'minute/close')
returns = prices.pct_change()
returns.to_hdf('data/sp500_r.h5', 'minute/return/close')
