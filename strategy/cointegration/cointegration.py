from utils.pair_uid import uid as get_uid
from strategy.cointegration.spread import  calculate_spread
from strategy.cointegration.zscore import  get_zscores

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from utils.indicators.atr import get_atr

from utils.indicators.rsi import RSI

from setup import config

import MetaTrader5 as mt5

def check_cointegration(close_series_0, close_series_1):
    is_cointegrated = False

    coint_res = coint(close_series_0, close_series_1)

    t_value = coint_res[0]
    p_value = coint_res[1]
    c_value = coint_res[2][1]

    if p_value < 0.05 and t_value < c_value:
        is_cointegrated = True

    return is_cointegrated

def normalize(atr):
    latest_atr = atr[-1]
    atr_min = min(atr)
    atr_max = max(atr)
    
    normalized_atr = (latest_atr-atr_min)/(atr_max-atr_min)
    
    return normalized_atr

def setup_cointegrated_pair(sym_0, sym_1, close_prices_0, close_prices_1):
    close_series_0 = pd.Series(close_prices_0)
    close_series_1 = pd.Series(close_prices_1)

    model = sm.OLS(close_series_0, close_series_1).fit()
    hedge_ratio = model.params[0]  # coeff

    spreads = calculate_spread(close_series_0, close_series_1, hedge_ratio)
    z_score_list, max_zscore, avg_zscore, mode_zscore, latest_zscore = get_zscores(spreads)
    
    
    rsi_0 = RSI(close_series_0, 14)
    latest_rsi_0 = rsi_0[-1]
    
    rsi_1 = RSI(close_series_1, 14)
    latest_rsi_1 = rsi_1[-1]
    
    zero_crossings = len(np.where(np.diff(np.sign(spreads)))[0])
    uid = get_uid(sym_0, sym_1)
    
    return {"uid": uid,
            "sym_0": sym_0,
            "sym_1": sym_1,
            "zero_crossings": zero_crossings,
            "max_z_score": max_zscore,
            "avg_z_score": avg_zscore,
            "mode_z_score": mode_zscore,
            "latest_zscore": latest_zscore,
            f"rsi_{sym_0}": latest_rsi_0,
            f"rsi_{sym_1}": latest_rsi_1,
            }

def get_cointegrated_tickers(symbols):
    cointegrated_pairs = []
    uid_list = []

    for symbol_0 in symbols:
        for symbol_1 in symbols:
            uid = get_uid(symbol_0.name, symbol_1.name)
            if symbol_0.name == symbol_1.name:
                continue

            if uid in uid_list:
                continue

            uid_list.append(uid)
            sym_0 = symbol_0.name
            sym_1 = symbol_1.name
            
            rates_0 = mt5.copy_rates_from_pos(sym_0, config.timeframe, 0, config.period)
            rates_1 = mt5.copy_rates_from_pos(sym_1, config.timeframe, 0, config.period)
            
            close_prices_0 = []
            close_prices_1 = []
            
            for rate in rates_0:
                close_prices_0.append(rate[4]) # index 4 is close price
            
            for rate in rates_1:
                close_prices_1.append(rate[4])
                
            close_series_0 = pd.Series(close_prices_0)
            close_series_1 = pd.Series(close_prices_1)

            is_pair_cointegrated = check_cointegration(close_series_0,close_series_1)

            if is_pair_cointegrated:
                pair = setup_cointegrated_pair(sym_0, sym_1, close_prices_0, close_prices_1)
                cointegrated_pairs.append(pair)

    #sort the cointegrated pairs by zero crossings
    sorted_cointegrated_pairs = sorted(cointegrated_pairs, key=lambda i: i['zero_crossings'])

    # return cointegrated pairs
    return sorted_cointegrated_pairs