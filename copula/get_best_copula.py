import scipy.stats as st
from copulae import archimedean, GaussianCopula, StudentCopula
import numpy as np
import pandas as pd

def get_best_copula(ticker0_u, ticker0_v, ticker1_u, ticker1_v):
    # Define candidate copulas
    copulas = [ 
               archimedean.ClaytonCopula, 
               archimedean.GumbelCopula,
              archimedean.FrankCopula,
              StudentCopula]
    
    # Fit copulas and evaluate goodness of fit
    results = []
    for copula in copulas:
        # Fit copula
        copula = copula(theta=1, dim=2)
        try:
            copula.fit([ticker0_u, ticker1_u], [ticker0_v, ticker1_v])
            # Calculate AICc
            aicc = copula.aicc([ticker0_u, ticker1_u], [ticker0_v, ticker1_v])
            # Store results
            results.append({'Copula': copula.name, 
                            'AICc': aicc})
        except:
            pass

    # Print results
    results_df = pd.DataFrame(results)
    print(results_df)

     # Select best fitting copula
    best_copula = copulas[results_df['AICc'].idxmin()]

    print('\nBest fitting copula:', best_copula.family)

    return best_copula
