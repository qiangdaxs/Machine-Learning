#!/usr/bin/env python2.7
'''eventstudy.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-06-05 10:18:32 -0400'


import pandas as pd
import simulate
import matplotlib.pyplot as plt
import numpy as np
import sys
#import multiprocessing as mp
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


def event_study(events, price_minute, n=5000):
    study = np.zeros(n)
    nsig = 0
    #p = mp.Pool(8)
    for i, v in enumerate(events.iteritems()):
        t, s = v
        if i % 10000 == 0:
            print >> sys.stderr, i, '\r',
        if t in price_minute.index:
            #print t
            p = price_minute.loc[t:, s].head(n).values
            dp = p - p[0]
            dp[np.isnan(dp)] = 0
            try:
                study = study + dp
            except ValueError:
                break
            nsig += 1
    #pp = np.array(study)
    #pp = np.nansum(pp, axis=0)
    print 'nsig=', nsig
    return study / (nsig / 100)



if __name__ == "__main__":
    main()
