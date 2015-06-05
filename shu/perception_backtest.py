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
logging.basicConfig(level=logging.DEBUG)

#=====Function Used to Load Data from Local File=======================================
def load_bars_from_file(stock, start=None, end=None):
    
    '''load pricing data from single file
    str, str, str -> pd.DataFrame'''

    path = '1M_SP500/{}.csv'.format(stock)
    logging.debug('load stock from {}'.format(path))
    prices = pd.read_csv(path, parse_dates=[['Date', 'Time']], index_col='Date_Time')
    prices.index = prices.index.tz_localize('US/Eastern').tz_convert('UTC')
    if start is not None:
        prices = prices[start:end]
    prices.columns=['symbol', 'open', 'high', 'low', 'close', 'volume']
    prices['price'] = prices['close']
    return prices

def load_bars(stocks, start, end, fillna=True):
    '''load pricing data from file, default fill NaN
    [str], str, str -> pd.Panel
    data is Panel(stocks x time x bars)'''
    stock2price_dic = {stock: load_bars_from_file(stock, start, end) for stock in stocks}
    data = pd.Panel(stock2price_dic)
    if fillna:
        data = data.fillna(method='ffill', axis=2)
        data = data.fillna(method='bfill', axis=2)
    return data

#================Set Start and End Time=================================================
start = '2013-2-11'
end = '2013-5-10'
#===========sub list of 10 stocks in SP500==============================================
stocks = ['SBUX','NFLX','EBAY','CSCO','CA','BIIB','BBBY','ADP']

nsdq=['SYMC', 'WDC','NFLX', 'AVP'] 

ss=['CERN','WFM','ALXN', 'GRMN', 'SRCL', 'BIIB', 'REGN', 'AMAT', 'COST', 'FISV', 'NVDA', 'ADBE', 
'WYNN','DTV', 'PCAR', 'SBUX', 'AVGO', 'INTC', 'MNST', 'DLTR', 'SNDK', 'FAST', 'ADSK', 'VRTX', 'SPLS', 'MYL', 'BBBY', 'KRFT', 
'CTXS', 'SIAL', 'AKAM', 'CELG', 'EXPE', 'PCLN', 'CTSH', 'ISRG', 'PAYX', 'LLTC', 'ADP', 'TXN', 'GILD', 'CA', 'FFIV', 'ORLY', 'AMGN', 
'INTU', 'QCOM', 'ESRX', 'XLNX', 'STX', 'TRIP', 'ADI', 'CHRW', 'TSCO', 'MAR', 'MAT', 'VIAB', 'NTAP', 'FOXA', 'CSCO', 'EBAY', 'MU', 
'MDLZ', 'BRCM', 'GMCR', 'ROST', 'EXPD', 'ALTR', 'KLAC']

SP_500=['A','AA','AAPL','ABBV','ABC','ABT','ACE','ACN','ACT','ADBE','ADI','ADM','ADP','ADS','ADSK','ADT','AEE','AEP','AES',
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

#==========================Read Signal Data==========================================================================================

#signal_data = pd.read_csv('sp500_signal.csv',index_col=0,parse_dates=True)
signal_data = pd.read_csv('perception_full.csv',index_col='harvested_at',parse_dates=True)
signal_data =signal_data.convert_objects(convert_numeric=True)
signal_data = signal_data[signal_data['companies.0'].isin(nsdq)]


#import pdb;pdb.set_trace()
#set start and end time for data. 
start = datetime.strptime(start, '%Y-%m-%d')
end = datetime.strptime(end, '%Y-%m-%d')
#data = load_bars_from_yahoo(stocks=stocks, start=start, end=end)

data = load_bars(stocks=nsdq, start=start, end=end)
#Fill the NA data using forward and backward dir.
data = data.fillna(method='ffill', axis=2)
data = data.fillna(method='bfill', axis=2)

#load from local CSV



def initialize(context):
    context.stocks = nsdq
    context.upper_bound = 60
    context.lower_bound = -60
    context.impact_bound=70
    context.rank_bound=5
    context.bulls=[]
    context.bears=[]
    context.pnl={}
    context.date=[]
    context.sell_time=''
    schedule_function(end_of_day,date_rules.every_day(),time_rules.market_close())

    schedule_function(exit_schedule,date_rules.every_day(),time_rules.market_close(minutes=15))

    schedule_function(long_bulls_short_bears,date_rules.every_day(),time_rules.market_open(minutes=30))
    

    #How to initialize data

def handle_data(context, data):
    ################# daily / minute switch ###################################
    
    build_list(context,data)
    print(get_datetime().strftime('%Y-%m-%d %H:%M'))


#===============intra-day long_shot strategy=========================================
#===========Not very effective in the 1 year backtest================================

def build_list(context,data):
    
    now_minute = get_datetime().strftime('%Y-%m-%d %H:%M')
    minute_symbol=signal_data[now_minute]    

    for stock in context.stocks:
        ticker=(minute_symbol['companies.0']==stock)
        content=minute_symbol[ticker]
        #=====article_sentiment is the average article sentiment at that time========
        article_perception=np.mean(content['article_perception'])
         
        #===== event_source_rank is the average  at that time========================
        event_source_rank=np.mean(content['overall_source_rank'])

        #===== event_impact_score is the average  at that time=======================
        event_impact_score=np.mean(content['event_impact_score.on_entities.0.on_entity'])
        
        if np.isnan(article_perception) == False and np.isnan(event_source_rank) == False and np.isnan(event_impact_score) == False:
            
            if article_perception > context.upper_bound and event_source_rank > context.rank_bound and event_impact_score > context.impact_bound:
                context.bulls.append(stock)

            if article_perception < context.lower_bound and event_source_rank > context.rank_bound and event_impact_score > context.impact_bound: 
                context.bears.append(stock)
    
    #==================Do the transaction 30 min before the market close=============
    
def long_bulls_short_bears(context,data):
    
    if context.portfolio.positions == {}:


        now = get_datetime().strftime('%Y-%m-%d')
        index = get_trading_days(start,end+timedelta(days=10)).get_loc(now)
        sell_time = get_trading_days(start,end+timedelta(days=10))[index+2]
        sell_time=sell_time.strftime('%Y-%m-%d')

        if len(context.bulls) != 0:
            
            context.sell_time = sell_time
            for stock in context.bulls:
                order_target_percent(stock,1.0/len(context.bulls))


        if len(context.bears) != 0:
            context.sell_time = sell_time
            for stock in context.bears:
                order_target_percent(stock,-1.0/len(context.bears))
        
        context.bears=[]
        context.bulls=[]


    #==============We are going to sell the stocks that bought after 2 days==========
def exit_schedule(context,data):

    if get_datetime().strftime('%Y-%m-%d') == context.sell_time:
        #import pdb;pdb.set_trace()
        context.sell_time=''
        for stock in context.stocks:
            order_target_percent(stock,0)



    '''if get_datetime().strftime('%H:%M') == '19:45':
        
        context.sell_time=0
        for stock in context.stocks:
            order_target_percent(stock,0)'''



    

def end_of_day(context,data):
    open_orders=get_open_orders()
    if open_orders:
        for security,order in open_orders:
            for oo in orders:
                cancel_order(oo) 


def analysis(context,perf):
    perf.portfolio_value.plot()
    import pdb;pdb.set_trace()
    pyplot.show()


def plot_image(context,per):
    
    pnl=pd.DataFrame(data=context.pnl.values(),index=context.date)

    pyplot.plot(pnl)
    pyplot.show()



def main():
    algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
#algo_obj._analyze = functools.partial(analyze, fig=4)
    algo_obj._analyze=analysis
    algo_obj.run(data)




if __name__ == "__main__":
    main()