import MetaTrader5 as mt5

safety_margin = 10000
account_size = 200000 - safety_margin
daily_dd_limit = 0.05
total_dd_limit = 0.1

# Risk per cpaital
win_prob = 0.2  # need backtest

rr_ratio = 6

kelly_risk = (win_prob - (1-win_prob)/rr_ratio)/2

current_date = ""

trading_record = {}

def set_tradeable_capital():
    account_daily_dd = account_size * daily_dd_limit
    account_info_dict = mt5.account_info()._asdict()

    equity = account_info_dict["equity"] - safety_margin

    daily_tradeable_capital = account_daily_dd + (equity - account_size)  
   
    return daily_tradeable_capital

    



