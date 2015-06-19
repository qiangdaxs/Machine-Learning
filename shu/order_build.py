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
#stock=['FOXA','ATVI','ADBE','AKAM','ALXN','ALTR','AMZN','AMGN','ADI','AAPL','AMAT','ADSK','ADP','AVGO','BIDU','BBBY','BIIB','BRCM','CHRW','CA','CTRX','CELG','CERN','CHTR','CHKP','CSCO','CTXS','CTSH','COST','DTV','DISH','DLTR','EBAY','EQIX','EXPE','EXPD','ESRX','FFIV','FB','FAST','FISV','GRMN','GILD','GOOG','HSIC','ILMN','INTC','INTU','ISRG','KLAC','GMCR','KRFT','LMCK','LMCA','LLTC','MAR','MAT','MXIM','MU','MSFT','MDLZ','MNST','MYL','NTAP','NFLX','NVDA','NXPI','ORLY','PCAR','PAYX','QCOM','REGN','ROST','SNDK','SBAC','STX','SIAL','SIRI','SPLS','SBUX','SRCL','SYMC','TSLA','TXN','PCLN','TSCO','TRIP','VRSK','VRTX','VIAB','VIP','VOD','WDC','WFM','WYNN','XLNX','YHOO']
stock=['A','AA','AAPL','ABBV','ABC','ABT','ACE','ACN','ACT','ADBE','ADI','ADM','ADP','ADS','ADSK','ADT','AEE','AEP','AES',
'AET','AFL','AGN','AIG','AIV','AIZ','AKAM','ALL','ALLE','ALTR','ALXN','AMAT','AME','AMG','AMGN','AMP','AMT','AMZN','AN',
'ANTM','AON','APA','APC','APD','APH','ARG','ATI','AVB','AVGO','AVP','AVY','AXP','AZO','BA','BAC','BAX','BBBY','BBT',
'BBY','BCR','BDX','BEN','BHI','BIIB','BK','BLK','BLL','BMS','BMY','BRCM','BSX','BTU','BWA','BXP','C','CA','CAG',
'CAH','CAM','CAT','CB','CBG','CBS','CCE','CCI','CCL','CELG','CERN','CF','CFN','CHK','CHRW','CI','CINF','CL','CLX','CMA',
'CMCSA','CME','CMG','CMI','CMS','CNP','CNX','COF','COG','COH','COL','COP','COST','COV','CPB','CRM','CSC','CSCO','CSX','CTAS',
'CTL','CTSH','CTXS','CVC','CVS','CVX','D','DAL','DD','DE','DFS','DG','DGX','DHI','DHR','DIS','DISCA','DISCK','DLPH','DLTR',
'DNB','DNR','DO','DOV','DOW','DPS','DRI','DTE','DTV','DUK','DVA','DVN','EA','EBAY','ECL','ED','EFX','EIX','EL','EMC','EMN',
'EMR','EOG','EQR','EQT','ESRX','ESS','ESV','ETFC','ETN','ETR','EW','EXC','EXPD','EXPE','F','FAST','FB','FCX','FDO','FDX','FE',
'FFIV','FIS','FISV','FITB','FLIR','FLR','FLS','FMC','FOSL','FOXA','FSLR','FTI','FTR','GAS','GCI','GD','GE','GGP','GHC','GILD',
'GIS','GLW','GM','GMCR','GME','GNW','GOOG','GOOGL','GPC','GPS','GRMN','GS','GT','GWW','HAL','HAR','HAS','HBAN','HCBK','HCN',
'HCP','HD','HES','HIG','HOG','HON','HOT','HP','HPQ','HRB','HRL','HRS','HSP','HST','HSY','HUM','IBM','ICE','IFF','INTC',
'INTU','IP','IPG','IR','IRM','ISRG','ITW','IVZ','JBL','JCI','JEC','JNJ','JNPR','JOY','JPM','JWN','K','KEY','KIM','KLAC','KMB'
,'KMI','KMX','KO','KORS','KR','KRFT','KSS','KSU','L','LB','LEG','LEN','LH','LLL','LLTC','LLY','LM','LMT','LNC','LO','LOW','LRCX',
'LUK','LUV','LVLT','LYB','M','MA','MAC','MAR','MAS','MAT','MCD','MCHP','MCK','MCO','MDLZ','MDT','MET','MHFI','MHK','MJN','MKC',
'MLM','MMC','MMM','MNK','MNST','MO','MON','MOS','MPC','MRK','MRO','MS','MSFT','MSI','MTB','MU','MUR','MWV','MYL','NAVI','NBL',
'NBR','NDAQ','NE','NEE','NEM','NFLX','NFX','NI','NKE','NLSN','NOC','NOV','NRG','NSC','NTAP','NTRS','NU','NUE','NVDA','NWL',
'NWSA','OI','OKE','OMC','ORCL','ORLY','OXY','PAYX','PBCT','PBI','PCAR','PCG','PCL','PCLN','PCP','PDCO','PEG','PEP','PETM',
'PFE','PFG','PG','PGR','PH','PHM','PKI','PLD','PLL','PM','PNC','PNR','PNW','POM','PPG','PPL','PRGO','PRU','PSA','PSX',
'PVH','PWR','PX','PXD','QCOM','QEP','R','RAI','RCL','RDC','REGN','RF','RHI','RHT','RIG','RL','ROK','ROP','ROST','RRC','RSG',
'RTN','SBUX','SCG','SCHW','SE','SEE','SHW','SIAL','SJM','SLB','SNA','SNDK','SNI','SO','SPG','SPLS','SRCL','SRE','STI','STJ',
'STT','STX','STZ','SWK','SWN','SWY','SYK','SYMC','SYY','T','TAP','TDC','TE','TEG','TEL','TGT','THC','TIF','TJX','TMK','TMO',
'TRIP','TROW','TRV','TSCO','TSN','TSO','TSS','TWC','TWX','TXN','TXT','TYC','UA','UHS','UNH','UNM','UNP','UPS','URBN','URI','USB','UTX',
'V','VAR','VFC','VIAB','VLO','VMC','VNO','VRSN','VRTX','VTR','VZ','WAT','WBA','WDC','WEC','WFC','WFM','WHR','WIN','WM','WMB','WMT',
'WU','WY','WYN','WYNN','XEC','XEL','XL','XLNX','XOM','XRAY','XRX','XYL','YHOO','YUM','ZION','ZMH','ZTS']


path='/Users/qiangda/Documents/accern/backtest/data/'






position=np.zeros(97)
order_target_percent=np.zeros(97)+0.05
start=pd.Timestamp('2012-8-15')
end =pd.Timestamp('2015-2-19')
#data=pd.read_csv('daily_signal.csv',index_col='T',parse_dates=True)
#The 'daily_signal.csv' is the final signal file to get order_file

stock_ret=pd.read_hdf(path+'sp500_r.h5','daily/return')
bench_return=pd.read_hdf(path+'sp500_r.h5',key='daily/return/index')['SPX']
trading_start=' 09:32'
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

def data_process(data):
    pd.order=pd.DataFrame()
    for date in Trading_days():
        date=date.strftime('%Y-%m-%d')
        pd.temp=data[date+trading_start:date+trading_end]
        pd.order=pd.order.append(pd.temp)
    return pd.order

def beta_calculate(date,stock):

    #'date' is in format '%Y-%M-%d'


    stock_return=stock_ret[stock]
    position=stock_return.index.searchsorted(date)

    bench_position=bench_return.index.searchsorted(date)

    length=position-max(position-200,0)

    if position != 0:

        stock_list=stock_return[position-length:position].values
        stock_list=np.ma.array(stock_list,mask=np.isnan(stock_list))

        bench_list=bench_return[(bench_position-length):bench_position].values
        bench_list=np.ma.array(bench_list,mask=np.isnan(bench_list))
        import pdb;pdb.set_trace()
        beta=np.cov(stock_list,bench_list)[0,1]/np.cov(stock_list,bench_list)[1,1]



    else:
        beta=0

    return beta


def ret_calculate():


    price_data = pd.read_hdf('/Users/qiangda/Documents/Accern/accern-backtest/data/sp500.h5','daily/close')
    ret=pd.DataFrame(columns=price_data.columns)
    for sid in stock:
        ret[sid]=np.diff(price_data[sid])/price_data[sid][:-1]


    return ret












def strategy(data):
    count=1
    orders=pd.DataFrame()
    for sid in stock:
        import pdb;pdb.set_trace()
        tick=data['Symbol']==sid
       # import pdb;pdb.set_trace()
        if len(data[tick]) != 0:
            temp=pd.DataFrame(index=data[tick].index,columns=['Symbol','Amount'])
            temp['Symbol']=sid
            l=len(data[tick].index)

           # import pdb;pdb.set_trace()
            '''for i in range(0,l):
                if data[tick]['Sentiment'][i]>0:
                    temp['Amount'][i]=1

                if data[tick]['Sentiment'][i]<0:
                    temp['Amount'][i]=-1

            orders=orders.append(temp)
            count=count+1'''
            #initiate the first trade
            if data[tick]['Sentiment'][0]>0:
                temp['Amount'][0]=0.05
            if data[tick]['Sentiment'][0]<0:
                temp['Amount'][0]=-0.05


            for i in range(1,l):
                if temp['Amount'][i-1]==0.05 and data[tick]['Sentiment'][i]>0 and data[tick]['Sentiment'][i-1]>0:
                    temp['Amount'][i]=0

                if temp['Amount'][i-1]==0 and data[tick]['Sentiment'][i]>0 and data[tick]['Sentiment'][i-1]>0:
                    temp['Amount'][i]=0

                if temp['Amount'][i-1]=='exit' and data[tick]['Sentiment'][i]>0:
                    temp['Amount'][i]=0.05

                if temp['Amount'][i-1]==0.05 and data[tick]['Sentiment'][i]<0 and data[tick]['Sentiment'][i-1]>0:
                    temp['Amount'][i]='exit'

                if temp['Amount'][i-1]==-0.05 and data[tick]['Sentiment'][i]>0 and data[tick]['Sentiment'][i-1]<0:
                    temp['Amount'][i]='exit'

                if temp['Amount'][i-1]==-0.05 and data[tick]['Sentiment'][i]<0 and data[tick]['Sentiment'][i-1]<0:
                    temp['Amount'][i]=0

                if temp['Amount'][i-1]==0 and data[tick]['Sentiment'][i]<0 and data[tick]['Sentiment'][i-1]<0:
                    temp['Amount'][i]=0

                if temp['Amount'][i-1]=='exit' and data[tick]['Sentiment'][i]<0:

                    temp['Amount'][i]=-0.05
                if temp['Amount'][i-1]==0 and data[tick]['Sentiment'][i]<0 and data[tick]['Sentiment'][i-1]>0:
                    temp['Amount'][i]='exit'


                if temp['Amount'][i-1]==0 and data[tick]['Sentiment'][i]>0 and data[tick]['Sentiment'][i-1]<0:
                    temp['Amount'][i]='exit'
             #   import pdb;pdb.set_trace()


            orders=orders.append(temp)
            count=count+1
            print count
    return orders





def main():

    i=0
    beta=pd.DataFrame(columns=stock,index=Trading_days())
    import pdb;pdb.set_trace()
    for sid in ['AAPL']:
        i+=1
        print i
        for date in Trading_days():
            date=date.strftime('%Y-%m-%d')
            beta[sid][date]=beta_calculate(date,sid)

    beta.to_hdf(path+'beta.h5','daily')


if __name__=="__main__":
    main()





























