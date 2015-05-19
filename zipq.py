#!/usr/bin/env python2.7
'''zipq.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-05-15 10:54:49 -0400'


import zipline
import matplotlib.pyplot as pyplot
from collections import defaultdict

import numpy as np
import pandas as pd
import pytz
from datetime import datetime, timedelta
from zipline import TradingAlgorithm
from zipline.api import order_target, record, symbol, history, add_history

#: NOTICE HOW THIS IS OUTSIDE INITIALIZE, BECAUSE IT IS, WE CAN REDFINE IT EVERYTIME WE REDINE INITIALIZE
aapl_weights = .50
spy_weights = .50


if __name__ == "__main__":
    main()


