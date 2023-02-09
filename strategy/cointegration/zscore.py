import MetaTrader5 as mt5
import pandas as pd
from strategy.cointegration.spread import calculate_spread
from setup import config
from statistics import mode
from utils.indicators.atr import get_atr
import statsmodels.api as sm

def get_zscores(spread):
    z_score_window = 21

    df = pd.DataFrame(spread)

    x = df.rolling(window=1).mean()
    mean = df.rolling(window=z_score_window).mean()
    std = df.rolling(window=z_score_window).std()

    df["Z-Score"] = round((x-mean)/std, 3)

    z_score_list = df["Z-Score"].dropna().astype(float).values
    
    abs_zscore_list = []
    
    for z_score in z_score_list:
        abs_zscore_list.append(abs(z_score))
    
    if len(abs_zscore_list) > 0:  
        max_z_score = max(abs_zscore_list)
        avg_z_score = round(sum(abs_zscore_list)/len(abs_zscore_list),3)
        mode_zscore = mode(abs_zscore_list)
        latest_zscore = z_score_list[-1]

        return (z_score_list, max_z_score, avg_z_score, mode_zscore, latest_zscore)
    else:
        return ()

def normalize(atr):
    latest_atr = atr[-1]
    atr_min = min(atr)
    atr_max = max(atr)
    
    normalized_atr = (latest_atr-atr_min)/(atr_max-atr_min)
    
    return normalized_atr

def get_latest_zscore(sym_0, sym_1):
    sym_0_info = mt5.symbol_info_tick(sym_0)
    sym_1_info = mt5.symbol_info_tick(sym_1)

    latest_price_0 = (sym_0_info.bid + sym_0_info.ask)  / 2
    latest_price_1 = (sym_1_info.bid + sym_1_info.ask)  / 2
    
    rates_0 = mt5.copy_rates_from_pos(sym_0, config.timeframe, 0, config.period)
    rates_1 = mt5.copy_rates_from_pos(sym_1, config.timeframe, 0, config.period)
    
    close_prices_0 = []
    close_prices_1 = []
            
    for rate in rates_0:
        close_prices_0.append(rate[4])
            
    for rate in rates_1:
        close_prices_1.append(rate[4])

    close_prices_0.pop(0)
    close_prices_1.pop(0)

    close_prices_0.append(latest_price_0)
    close_prices_1.append(latest_price_1)
    
    close_series_0 = pd.Series(close_prices_0)
    close_series_1 = pd.Series(close_prices_1)

    model = sm.OLS(close_series_0, close_series_1).fit()
    hedge_ratio = model.params[0]  # coeff

    spreads_list = calculate_spread(close_prices_0,close_prices_1, hedge_ratio)
    z_scores_list, max_z_score, avg_zscore, mode_zscore, latest_zscore = get_zscores(spreads_list)
    
    if len(z_scores_list) > 0:
        return (latest_zscore, max_z_score, avg_zscore, mode_zscore)
    else:
        return None


