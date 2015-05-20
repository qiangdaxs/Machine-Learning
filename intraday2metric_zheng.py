import numpy as np
import pandas as pd
from datetime import timedelta
import pytz

def initialize(context):
    set_symbol_lookup_date('2015-04-01')
    
    context.stocks = symbols('FOXA','ATVI','ADBE','AKAM','ALXN','ALTR','AMGN','ADI','AMAT','ADSK','ADP','AVGO','BIDU','BBBY','BIIB','BRCM','CHRW','CA','CTRX','CELG','CERN','CHTR','CHKP','CSCO','CTXS','CTSH','COST','DTV','DISH','DLTR','EBAY','EQIX','EXPE','EXPD','ESRX','FFIV','FAST','FISV','GRMN','GILD','HSIC','ILMN','INTC','INTU','ISRG','KLAC','GMCR','KRFT','LMCK','LMCA','LLTC','MAR','MAT','MXIM','MU','MDLZ','MNST','MYL','NTAP','NFLX','NVDA','NXPI','ORLY','PCAR','PAYX','QCOM','REGN','ROST','SNDK','SBAC','STX','SIAL','SIRI','SPLS','SBUX','SRCL','SYMC','TSLA','TXN','PCLN','TSCO','TRIP','VRSK','VRTX','VIAB','VIP','VOD','WDC','WFM','WYNN','XLNX')
    
    set_benchmark(symbol('SPY'))
    
    
    set_commission(commission.PerShare(cost=0.014, min_trade_cost=1.4))
    
   
    set_slippage(slippage.FixedSlippage(spread=0))
    fetch_csv("https://dl.dropboxusercontent.com/u/70792051/Accern%20Backtest/NASDAQ100_MarketNeutral.csv",
              pre_func = change_dates,
              date_column ='start_date',
              date_format ='%m/%-d/%Y %H:%M' )
        
    
    schedule_function(long_bulls_short_bears,
                      date_rules.every_day(),
                      time_rules.market_open())

    schedule_function(close_all_positions,
                      date_rules.every_day(),
                      time_rules.market_close(minutes=5))
    
    
    
    context.upper_bound = 0.35
    context.lower_bound = -0.35
    #Impact Score
    context.upper_bound_a = 88
    context.lower_bound_a = 88
    #Source Rank
    context.upper_bound_c = 7
    context.lower_bound_c = 7
    
def change_dates(fetcher_data):
    fetcher_data['start_date'] = pd.to_datetime(fetcher_data['start_date'], pytz.timezone('US/Eastern')) + timedelta(days=1)
    #fetcher_data['start_date'] = pd.to_datetime(fetcher_data['start_date'], utc=True).tz_convert('US/Eastern') + timedelta(days=1)
   
    fetcher_data['enter_date'] = fetcher_data['start_date']
    return fetcher_data
    
        
    
def long_bulls_short_bears(context, data):
    
   
    bulls = []
    bears = []
    
    for stock in context.stocks:
        if ('article_sentiment' and 'event_impact_score_entity_1' and 'overall_source_rank') in data[stock]:
            today = get_datetime()
            if data[stock]['enter_date'].month == today.month and data[stock]['enter_date'].year == today.year and data[stock]['enter_date'].day == today.day:
                if (data[stock]['article_sentiment'] > context.upper_bound) and (data[stock]['overall_source_rank'] > context.upper_bound_a):
                    bulls.append(stock)
                 
                
                elif (data[stock]['article_sentiment'] < context.lower_bound) and (data[stock]['overall_source_rank'] > context.lower_bound_a):
                    bears.append(stock)
               

    for stock in bulls:
        order_target_percent(stock, 1.0/len(bulls))
       
        
    for stock in bears:
        order_target_percent(stock, -1.0/len(bears))
        
       
    
    
    #: Record our positions
    record(longs=len(bulls))
    record(shorts=len(bears))
    
def close_all_positions(context, data):
    for stock in data:
        if context.portfolio.positions[stock.sid].amount != 0:
            order_target_percent(stock, 0)
    
def handle_data(context, data):
    pass
