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

    rates = mt5.copy_rates_from_pos(symbol, config.atr_timeframe, 0, 30)
    rates_dict = pd.DataFrame(rates).to_dict()

    close_list = rates_dict["close"]
    high_list = rates_dict["high"]
    low_list = rates_dict["low"]

    atr_data = {
        "close": close_list,
        "high": high_list,
        "low": low_list
    }

    df = pd.DataFrame(atr_data)

    high_low = df["high"] - df["low"]
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)

    atr = (true_range.rolling(config.atr_period).sum()/config.atr_period).to_list()
    max_high = max(high_list)
    min_low = min(low_list)

    return atr, max_high, min_low