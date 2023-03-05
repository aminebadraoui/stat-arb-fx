import numpy as np
import pandas as pd
import scipy.stats as stats
from copula.distribution_fit import get_best_fitting_distribution
from copulas.bivariate import select_copula
from copula.get_best_copula import get_best_copula
from execution.check_signal import Signal
from scipy.stats import norm
import MetaTrader5 as mt5

from setup import config

# Create a callable function for the best copula
def best_copula_func(copula, u):
    return copula.cumulative_distribution(u)

def perform_copula_analysis(sym_0, sym_1):
    # Load data into a pandas DataFrame
    rates_0 = mt5.copy_rates_from_pos(sym_0, config.timeframe, 0, config.period)
    rates_1 = mt5.copy_rates_from_pos(sym_1, config.timeframe, 0, config.period)
    
    close_prices_0 = []
    close_prices_1 = []
            
    for rate in rates_0:
        close_prices_0.append(rate[4]) # index 4 is close price
            
    for rate in rates_1:
        close_prices_1.append(rate[4])
    
    data = pd.DataFrame(list(zip(close_prices_0, close_prices_1)),
               columns =['SYM_0', 'SYM_1'])
    
    # Calculate log cumulative returns for each ticker
    ticker0_returns = np.log(data['SYM_0'] / data['SYM_0'].shift(1))
    ticker1_returns = np.log(data['SYM_1'] / data['SYM_1'].shift(1))
    
    # Remove missing values
    ticker0_returns = ticker0_returns.dropna()
    ticker1_returns = ticker1_returns.dropna()
    
    get_best_fitting_distribution(ticker0_returns, ticker1_returns)
    
    return Signal.WAIT
   



    
    
    