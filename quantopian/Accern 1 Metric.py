# Sentiment Fetch for Kumesh - Fetch example with sentiment trading
# Derek M Tishler <dmtishler@gmail.com>

import numpy as np
import pandas as pd

def initialize(context):
    #Use file from dropbox to assign sid's and sentiment values to trade on.
    
    # Universe is set daily by inputs from the cvs fetch. But we will set a benchmark for comparison.
    #context.stocks = symbols('LULU')
    set_benchmark(symbol('TSLA'))
    
    # set a more realistic commission for IB, remove both this and slippage when live trading in IB
    set_commission(commission.PerShare(cost=0.014, min_trade_cost=1.4))
    
    # Default slippage values, but here to mess with for fun.
    set_slippage(slippage.VolumeShareSlippage(volume_limit=0.25, price_impact=0.1))
    
    #Only needed in testing/debugging to ensure orders are closed like in IB
    schedule_function(end_of_day, date_rules.every_day(), time_rules.market_close(minutes=1))
    
    fetch_csv("https://dl.dropboxusercontent.com/u/70792051/Accern%20Backtest/TSLA_Backtest%20(1).csv",
              date_column ='start_date',
              date_format = '%m-%d-%Y %H:%M')
    
    # Bounds of the sentiment bands
    context.upper_bound =  0.53
    context.lower_bound = -0.47

# Will be called on every trade event for the securities you specify. 
def handle_data(context, data):
    #Get EST Time
    context.exchange_time = pd.Timestamp(get_datetime()).tz_convert('US/Eastern')
    
    #Check that our portfolio does not  contain any invalid/external positions/securities
    check_invalid_positions(context, data)
    
    for stock in data:
        
        if 'article_sentiment' in data[stock]:
            record(Accern_Sentiment = data[stock]['article_sentiment'], upperBound = context.upper_bound, lowerBound = context.lower_bound)
            
            # We will not place orders if a stock is already in the process of handeling an order(fill time)
            if check_if_no_conflicting_orders(stock):
                
                # Go Long(buy), or exit and then buy(since minute mode so this condition will be valid all day
                if data[stock]['article_sentiment']   >= context.upper_bound:
                    # If we hav no positions, then we are good to buy
                    if context.portfolio.positions[stock.sid].amount == 0:
                        buy_position(context, data, stock)
                    # We have some positions, if they are short, then exit that position so we can go long.
                    else:
                        if context.portfolio.positions[stock.sid].amount < 0:
                            exit_position(context, data, stock)

                # Go short(sell), or exit and then short(since minute mode so this condition will be valid all day
                elif data[stock]['article_sentiment'] <= context.lower_bound:
                    # If we have no positions, then we are good to buy
                    if context.portfolio.positions[stock.sid].amount == 0:
                        short_position(context, data, stock)
                    # We have some positions, if they are long, then exit that position so we can go short.                        
                    else:
                        if context.portfolio.positions[stock.sid].amount > 0:
                            exit_position(context, data, stock)
                
def buy_position(context, data, stock):

    # Place an order, and store the ID to fetch order info
    orderId    = order_target_percent(stock, 1.0)
    # How many shares did we just order, since we used target percent of availible cash to place order not share count.
    shareCount = get_order(orderId).amount

    # We need to calculate our own inter cycle portfolio snapshot as its not updated till next cycle.
    value_of_open_orders(context, data)
    availibleCash = context.portfolio.cash-context.cashCommitedToBuy-context.cashCommitedToSell

    log.info("+ BUY {0:,d} of {1:s} at ${2:,.2f} for ${3:,.2f} / ${4:,.2f} @ {5:d}:{6:d}"\
             .format(shareCount,
                     stock.symbol,data[stock]['price'],
                     data[stock]['price']*shareCount, 
                     availibleCash,
                     context.exchange_time.hour,
                     context.exchange_time.minute))

def short_position(context, data, stock):
    
    #orderId    = order_target_percent(stock, -1.0/len(data))
    orderId    = order_target_percent(stock, -1.0)
    # How many shares did we just order, since we used target percent of availible cash to place order not share count.
    shareCount = get_order(orderId).amount

    # We need to calculate our own inter cycle portfolio snapshot as its not updated till next cycle.
    value_of_open_orders(context, data)
    availibleCash = context.portfolio.cash-context.cashCommitedToBuy+context.cashCommitedToSell

    log.info("- SHORT {0:,d} of {1:s} at ${2:,.2f} for ${3:,.2f} / ${4:,.2f} @ {5:d}:{6:d}"\
             .format(shareCount,
                     stock.symbol,data[stock]['price'],
                     data[stock]['price']*shareCount, 
                     availibleCash,
                     context.exchange_time.hour,
                     context.exchange_time.minute))

def exit_position(context, data, stock):
    order_target(stock, 0.0)
    value_of_open_orders(context, data)
    availibleCash = context.portfolio.cash-context.cashCommitedToBuy-context.cashCommitedToSell
    log.info("- Exit {0:,d} of {1:s} at ${2:,.2f} for ${3:,.2f} / ${4:,.2f} @ {5:d}:{6:d}"\
                 .format(int(context.portfolio.positions[stock.sid].amount),
                         stock.symbol,
                         data[stock]['price'],
                         data[stock]['price']*context.portfolio.positions[stock.sid].amount,
                         availibleCash,
                         context.exchange_time.hour,
                         context.exchange_time.minute))    
    
################################################################################

def check_if_no_conflicting_orders(stock):
    # Check that we are not already trying to move this stock
    open_orders = get_open_orders()
    safeToMove  = True
    if open_orders:
        for security, orders in open_orders.iteritems():
            for oo in orders:
                if oo.sid == stock.sid:
                    if oo.amount != 0:
                        safeToMove = False
    return safeToMove
    #

def check_invalid_positions(context, securities):
    # Check that the portfolio does not contain any broken positions
    # or external securities
    for sid, position in context.portfolio.positions.iteritems():
        if sid not in securities and position.amount != 0:
            errmsg = \
                "Invalid position found: {sid} amount = {amt} on {date}"\
                .format(sid=position.sid,
                        amt=position.amount,
                        date=get_datetime())
            raise Exception(errmsg)
            
def end_of_day(context, data):
    # cancle any order at the end of day. Do it ourselves so we can see slow moving stocks.
    open_orders = get_open_orders()
    
    if open_orders:# or context.portfolio.positions_value > 0.:
        #log.info("")
        log.info("*** EOD: Stoping Orders & Printing Held ***")

    # Print what positions we are holding overnight
    for stock in data:
        if context.portfolio.positions[stock.sid].amount != 0:
            log.info("{0:s} has remaining {1:,d} Positions worth ${2:,.2f}"\
                     .format(stock.symbol,
                             context.portfolio.positions[stock.sid].amount,
                             context.portfolio.positions[stock.sid].cost_basis\
                             *context.portfolio.positions[stock.sid].amount))
    # Cancle any open orders ourselves(In live trading this would be done for us, soon in backtest too)
    if open_orders:  
        # Cancle any open orders ourselves(In live trading this would be done for us, soon in backtest too)
        for security, orders in open_orders.iteritems():
            for oo in orders:
                log.info("X CANCLED {0:s} with {1:,d} / {2:,d} filled"\
                                     .format(security.symbol,
                                             oo.filled,
                                             oo.amount))
                cancel_order(oo)
    #
    log.info('') 
            
def value_of_open_orders(context, data):
    # Current cash commited to open orders, bit of an estimation for logging only
    context.currentCash = context.portfolio.cash
    open_orders = get_open_orders()
    context.cashCommitedToBuy  = 0.0
    context.cashCommitedToSell = 0.0
    if open_orders:
        for security, orders in open_orders.iteritems():
            for oo in orders:
                # Estimate value of existing order with current price, best to use order conditons?
                if(oo.amount>0):
                    context.cashCommitedToBuy  += oo.amount * data[oo.sid]['price']
                elif(oo.amount<0):
                    context.cashCommitedToSell += oo.amount * data[oo.sid]['price']
    #
