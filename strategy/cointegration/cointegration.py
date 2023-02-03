from mt_helpers.get_symbols_data import get_all_symbols_data
from utils.pair_uid import uid as get_uid
from strategy.cointegration.spread import  calculate_spread
from strategy.cointegration.zscore import  get_zscores

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint

def check_cointegration(close_series_0, close_series_1):
    is_cointegrated = False

    coint_res = coint(close_series_0, close_series_1)

    t_value = coint_res[0]
    p_value = coint_res[1]
    c_value = coint_res[2][1]

    if p_value < 0.05 and t_value < c_value:
        is_cointegrated = True

    return is_cointegrated

def setup_cointegrated_pair(sym_0, sym_1, close_prices_0, close_prices_1):
    close_series_0 = pd.Series(close_prices_0)
    close_series_1 = pd.Series(close_prices_1)

    model = sm.OLS(close_series_0, close_series_1).fit()
    hedge_ratio = model.params[0]  # coeff

    spreads = calculate_spread(close_series_0, close_series_1, hedge_ratio)
    z_scores = get_zscores(spreads).tolist()
    zero_crossings = len(np.where(np.diff(np.sign(spreads)))[0])

    return {"uid": get_uid(sym_0, sym_1),
            "sym_0": sym_0,
            "sym_1": sym_1,
            "close_prices_0": close_prices_0,
            "close_prices_1": close_prices_1,
            "hedge_ratio": hedge_ratio,
            "spread_data": spreads,
            "zero_crossings": zero_crossings,
            "z_score_data": z_scores}

def get_cointegrated_tickers():
    cointegrated_pairs = []

    # get symbols with price data
    symbols = get_all_symbols_data()

    # compute cointegration
    uid_list = []
    figs = []
    for symbol_0 in symbols:
        for symbol_1 in symbols:
            uid = get_uid(symbol_0["name"], symbol_1["name"])
            if symbol_0["name"] == symbol_1["name"]:
                continue

            if uid in uid_list:
                continue

            uid_list.append(uid)
            sym_0 = symbol_0["name"]
            sym_1 = symbol_1["name"]

            close_prices_0 = list(symbol_0["rates"]["close"].values())
            close_prices_1 = list(symbol_1["rates"]["close"].values())

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