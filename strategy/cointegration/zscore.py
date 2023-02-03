import MetaTrader5 as mt5
import pandas as pd
from strategy.cointegration.spread import calculate_spread

def get_zscores(spread):
    z_score_window = 21

    df = pd.DataFrame(spread)

    x = df.rolling(window=1).mean()
    mean = df.rolling(window=z_score_window).mean()
    std = df.rolling(window=z_score_window).std()

    df["Z-Score"] = (x-mean)/std

    z_score_list = df["Z-Score"].astype(float).values

    return (z_score_list)

def get_latest_zscore(pair, latest_price_0, latest_price_1):
    close_prices_0 = pair["close_prices_0"]
    close_prices_1 = pair["close_prices_1"]

    close_prices_0.pop(0)
    close_prices_1.pop(0)

    close_prices_0[-1] = latest_price_0
  
    close_prices_1[-1] = latest_price_1

    hedge_ratio = pair["hedge_ratio"]

    spreads_list = calculate_spread(close_prices_0,close_prices_1, hedge_ratio)
    z_scores_list = get_zscores(spreads_list)

    return z_scores_list[-1]


