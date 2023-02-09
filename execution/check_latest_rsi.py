import MetaTrader5 as mt5
from setup import config
from utils.indicators.rsi import RSI
import pandas as pd


def get_latest_rsi(symbol):
    sym_0_info = mt5.symbol_info_tick(symbol)

    latest_price = (sym_0_info.bid + sym_0_info.ask)  / 2
    
    rates = mt5.copy_rates_from_pos(symbol, config.timeframe, 0, config.period)

    close_prices = []
            
    for rate in rates:
        close_prices.append(rate[4])
            
    # close_prices.pop(0)
    # close_prices.append(latest_price)
    
    close_series = pd.Series(close_prices)
    
    rsi = RSI(close_series, n=14)
    
    if len(rsi) > 0:
        return rsi[-1]
    else:
        return -1
    
    
    
    
    