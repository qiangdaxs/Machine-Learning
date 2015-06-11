import zipline
from zipline.api import *
from zipline import TradingAlgorithm
from zipline.utils.tradingcalendar import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as pyplot
import pytz
from datetime import datetime
from zipline.utils.factory import load_bars_from_yahoo
import functools
import logging
from datetime import timedelta
from zipline.utils.tradingcalendar_bmf import *
logging.basicConfig(level=logging.DEBUG)

#========Global Variables====================================================
stock=['FOXA','ATVI','ADBE','AKAM','ALXN','ALTR','AMZN','AMGN','ADI','AAPL','AMAT','ADSK','ADP','AVGO','BIDU','BBBY','BIIB','BRCM','CHRW','CA','CTRX','CELG','CERN','CHTR','CHKP','CSCO','CTXS','CTSH','COST','DTV','DISH','DLTR','EBAY','EQIX','EXPE','EXPD','ESRX','FFIV','FB','FAST','FISV','GRMN','GILD','GOOG','HSIC','ILMN','INTC','INTU','ISRG','KLAC','GMCR','KRFT','LMCK','LMCA','LLTC','MAR','MAT','MXIM','MU','MSFT','MDLZ','MNST','MYL','NTAP','NFLX','NVDA','NXPI','ORLY','PCAR','PAYX','QCOM','REGN','ROST','SNDK','SBAC','STX','SIAL','SIRI','SPLS','SBUX','SRCL','SYMC','TSLA','TXN','PCLN','TSCO','TRIP','VRSK','VRTX','VIAB','VIP','VOD','WDC','WFM','WYNN','XLNX','YHOO']

position=np.zeros(97)
order_target_percent=np.zeros(97)+0.05
start=pd.Timestamp('2012-8-15')
end =pd.Timestamp('2015-2-19')
data=pd.read_csv('daily_signal.csv',index_col='T',parse_dates=True)
#The 'daily_signal.csv' is the final signal file to get order_file

trading_start=' 09:30'
trading_end = ' 16:00'


#=======Function to calculate Trading Days====================================
def Trading_days():
    days=[]
    for date in get_trading_days(start,end):
        date=date.tz_convert(None)
        days.append(date)
    return days
#=======Function to load origin signal file===================================


def load_signal():
    i=0
    signal_data=pd.read_hdf('sp500_signal.h5','signal')
    signal_frame=pd.DataFrame(columns=['T','Symbol','Sentiment','Rank','Impact'])
    logging.debug('Data Loaded done!')
    for line in signal_data.iterrows():
        if line[1]['article_sentiment'] > 0.35 and line[1]['event_source_rank_1'] > 7 and line[1]['event_impact_score_entity_1']>70:
            temp_df = pd.DataFrame([[line[0],line[1]['entities_ticker_1'],line[1]['article_sentiment'],line[1]['event_source_rank_1'],line[1]['event_impact_score_entity_1']]],columns=['T','Symbol','Sentiment','Rank','Impact'])
            signal_frame=signal_frame.append(temp_df)

        if line[1]['article_sentiment'] < -0.35 and line[1]['event_source_rank_1'] > 7 and line[1]['event_impact_score_entity_1']>70:
            temp_df = pd.DataFrame([[line[0],line[1]['entities_ticker_1'],line[1]['article_sentiment'],line[1]['event_source_rank_1'],line[1]['event_impact_score_entity_1']]],columns=['T','Symbol','Sentiment','Rank','Impact'])
            signal_frame=signal_frame.append(temp_df)

    return signal_frame

#=======Function to covert TimeZone and only include interested stocks=======

def load_effect_signal():
    effect_signal = pd.read_csv('effective_signal.csv',index_col='T',parse_dates=True)
    effect_signal.index.tz='US/Eastern'
    effect_signal=effect_signal[effect_signal['Symbol'].isin(stock)]
    return effect_signal
#=======Function to only include the signals during the trading time=========

def data_process():
    pd.order=pd.DataFrame()
    for date in Trading_days():
        date=date.strftime('%Y-%m-%d')
        pd.temp=data[date+trading_start:date+trading_end]
        pd.order=pd.order.append(pd.temp)
    return pd.order





def main():

#    for date in Trading_days():
    count=1
    orders=pd.DataFrame()
    for sid in stock:
        tick=data['Symbol']==sid
        temp=pd.DataFrame(index=data[tick].index,columns=['Symbol','Amount'])
        temp['Symbol']=sid
        l=len(data[tick].index)
       # import pdb;pdb.set_trace()
        for i in range(0,l):
            if data[tick]['Sentiment'][i]>0:
                temp['Amount'][i]=1

            if data[tick]['Sentiment'][i]<0:
                temp['Amount'][i]=-1

        orders=orders.append(temp)
        count=count+1
        '''for i in range(0,l):
            if data[tick]['Sentiment'][i]>0 and data[tick]['Sentiment'][i+1]>0:
                #if this are both greater than 0, i+1 should keep the same target percent

            if data[tick]['Sentiment'][i]>0 and data[tick]['Sentiment'][i+1]<0:
                #if this,

            if data[tick]['Sentiment'][i]<0 and data[tick]['Sentiment'][i+1]<0:

            if data[tick]['Sentiment'][i]<0 and data[tick]['Sentiment'][i+1]>0:'''

    import pdb;pdb.set_trace()



if __name__=="__main__":
    main()





























