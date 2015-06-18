#!/usr/bin/env python2.7
'''process_quantopian_trade.py
'''


__author__ = 'fantasy <pkuqiuning@gmail.com>'
__created__ = '2015-06-10 16:00:50 -0400'


import pandas as pd


def main():
    tdf = pd.read_excel('transactionorder2.xlsx', 1)
    tdl = [i.tolist()[0] for i in tdf.values]
    tdc = [(i[:10], i[10:].split(', ')[0].partition('INFO')[2], i[10:].split(', ')[1:]) for i in tdl]
    print tdc[:80]
    tdd = [i for i in tdc]
    td = [' '.join([i[0], i[2][3]]) + ',' + ','.join([i[2][0], i[1], i[2][1]]) + '\n' for i in tdd if i[2]]
    print 'output to trades.txt'
    with open('trades.txt', 'w') as f:
        f.write('T,symbol,amount,price\n')
        f.writelines(td)


if __name__ == "__main__":
    main()


