import numpy as np
import pandas as pd

import MetaTrader5 as mt5

import setup.config as config 

def get_atr(symbol):
    selected = mt5.symbol_select(symbol, True)
    if not selected:
        print(f"Failed to select {symbol}")
        mt5.shutdown()
        quit()

    rates = mt5.copy_rates_from_pos(symbol, config.atr_timeframe, 0, config.atr_period)
  

    df = pd.DataFrame(rates)

    high_low = df["high"] - df["low"]
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)

    atr = (true_range.rolling(config.atr_period).sum()/config.atr_period).dropna().tolist()
    print(atr)
    max_high = df["high"].max()
    min_low = df["low"].min()
    
    return atr, max_high, min_low