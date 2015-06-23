import numpy as np
import pytz
import pandas as pd
from datetime import timedelta

def initialize(context):
    set_symbol_lookup_date('2015-04-01')
    context.stocks=symbols('EBAY','GS')
    set_benchmark(symbol('SPY'))
    
    set_commission(commission.PerShare(cost=0.014, min_trade_cost=1.0))
    
    set_slippage(slippage.FixedSlippage(spread=0))
    
    '''schedule_function(long_bulls_short_bears,
                      date_rules.every_day(),
                      time_rules.market_open())'''
    schedule_function(close_all_positions,
                      date_rules.week_end(),
                      time_rules.market_close())
    fetch_csv("https://dl.dropboxusercontent.com/u/405620095/3Companies_V_GS_EBAY.csv",
              pre_func = change_dates, 
              date_column ='start_date',
              date_format ='%m/%-d/%Y %H:%M')
    
    context.upper_bound = 0.35
    context.lower_bound = -0.35
    #Impact Score
    context.impact_bound = 80
    #Source Rank Score
    context.rank_bound=7
    # Will be called on every trade event for the securities you specify. 
    context.old_as = 0

def change_dates(fetcher_data):
    fetcher_data['start_date'] = pd.to_datetime(fetcher_data['start_date'], pytz.timezone('US/Eastern')) + timedelta(days=6)
    #fetcher_data['start_date'] = pd.to_datetime(fetcher_data['start_date'], utc=True).tz_convert('US/Eastern') + timedelta(days=1)
   
    fetcher_data['enter_date'] = fetcher_data['start_date']
    
    return fetcher_data    
    
def handle_data(context, data):
    
   
    context.exchange_time = pd.Timestamp(get_datetime()).tz_convert('US/Eastern')
    for stock in context.stocks:
        if buy_signal(context,data,stock):
            order_target_percent(stock,1)
            record(ebay_buy=data[symbol('EBAY')].price)
          
       # log.info("buy Stock {0:s} to amount {1:,d}".format(stock.symbol,context.portfolio.positions[stock.sid].amount))
        if sell_signal(context,data,stock):
            order_target_percent(stock,-1)
           
        record(ebay=data[symbol('EBAY')].price)
        
        
        
    
    
        #log.info("sell Stock {0:s} to amount {1:,d}".format(stock.symbol,context.portfolio.positions[stock.sid].amount))
             

           
            
            
           

def buy_signal(context,data,stock):
    time=get_datetime()
    if time == data[stock].datetime:
        if ('article_sentiment' and 'event_impact_score_entity_1' and 'overall_source_rank') in data[stock]:
            if (data[stock]['article_sentiment'] > context.upper_bound) and (data[stock]['event_impact_score_entity_1'] > context.impact_bound) and (data[stock]['overall_source_rank'] > context.rank_bound):
                #log.info(data[stock]['article_sentiment'])
                if data[stock]['article_sentiment'] != context.old_as:
                    context.old_as = data[stock]['article_sentiment']
                    # order something
                    return True
                    
                      
        
                   
def sell_signal(context,data,stock):
    time=get_datetime()
    if ('article_sentiment' and 'event_impact_score_entity_1' and 'overall_source_rank') in data[stock]:
        if (data[stock]['article_sentiment'] < context.lower_bound) and (data[stock]['event_impact_score_entity_1'] > context.impact_bound) and (data[stock]['overall_source_rank'] > context.rank_bound):
            if data[stock]['article_sentiment'] != context.old_as:
                    context.old_as = data[stock]['article_sentiment']
                    # order something
                    return True
                
                


def close_all_positions(context, data):
    for stock in data:
        if context.portfolio.positions[stock.sid].amount != 0:
            order_target_percent(stock, 0)
    
            
            
         
