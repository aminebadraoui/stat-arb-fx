import MetaTrader5 as mt5

safety_margin = 10000
account_size = 200000 - safety_margin
daily_dd_limit = 0.05
total_dd_limit = 0.1

# Risk per cpaital
win_prob = 0.2  # need backtest

rr_ratio = 6

kelly_risk = (win_prob - (1-win_prob)/rr_ratio)/2

def get_current_total_risk():
    positions=mt5.positions_get()
   
    total_risk = 0
    if len(positions) > 0:
        for position in positions:
            symbol = position.symbol
            price_open = position.price_open
            volume = position.volume
            sl = position.sl
            tick_size = mt5.symbol_info(symbol).trade_tick_size 
            tick_value = mt5.symbol_info(symbol).trade_tick_value
            
            # compute risk
            risk = (abs(price_open-sl)/tick_size)*tick_value*volume
        
            total_risk += risk
    
    return total_risk
        
def get_tradeable_capital():
    account_daily_dd = account_size * daily_dd_limit
    account_info = mt5.account_info()

    balance = account_info.balance - safety_margin
    
    current_total_risk = get_current_total_risk()
    
    print(f" account_daily_dd : { account_daily_dd }")
    print(f" balance : { balance }")
    print(f" current_total_risk : { current_total_risk }")
    
    daily_tradeable_capital = account_daily_dd - current_total_risk
   
    return daily_tradeable_capital

    



