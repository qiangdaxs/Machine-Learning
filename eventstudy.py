#!/usr/bin/env python2.7
'''eventstudy.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-06-05 10:18:32 -0400'


import sys
import pandas as pd
import numpy as np
#import multiprocessing as mp
import matplotlib.pyplot as plt
import simulate
from libeventstudy import event_study


BOUND = -0.2


def main():
    signal_file = 'data/sp500_signal.h5'
    signal = pd.read_hdf(signal_file, 'signal')
    events = signal[signal.article_sentiment < BOUND].iloc[:, 0]
    events.index = [i.replace(second=0) for i in events.index]
    price_minute = simulate.load_minute_price(simulate.PRICES_FILE)
    study = event_study(events, price_minute)
    np.savetxt('study_as{}.txt'.format(BOUND), study)
    plt.plot(study)
    plt.savefig('study_as{}.png'.format(BOUND))
    plt.show()
    #price_daily = simulate.load_daily_price(simulate.PRICES_FILE)




if __name__ == "__main__":
    main()
