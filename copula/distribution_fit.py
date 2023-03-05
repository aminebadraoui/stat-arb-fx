import numpy as np
import pandas as pd
import scipy.stats as st
from distfit import distfit

from copulae import archimedean, GaussianCopula, StudentCopula

def get_best_fitting_distribution(ticker0_returns, ticker1_returns):
    
    dist_0 = distfit(distr=['norm','t', 'lognorm', "genlogistic", "genlogistic", "uniform"])
    dist_0.fit_transform(ticker0_returns,verbose=0)
    
    dist_1 = distfit(distr=['norm','t', 'lognorm', "genlogistic", "genlogistic", "uniform"])
    dist_1.fit_transform(ticker1_returns,verbose=0)
    
    dist_summary_0 = dist_0.summary
    dist_summary_1 = dist_1.summary
    
    dist_summary_0['score'] = dist_summary_0['score'].astype(float)
    min_score_row = dist_summary_0.loc[dist_summary_0['score'].idxmin()]
    ticker0_best_fit = min_score_row['name']
    
    dist_summary_1['score'] = dist_summary_1['score'].astype(float)
    min_score_row = dist_summary_1.loc[dist_summary_1['score'].idxmin()]
    ticker1_best_fit = min_score_row['name']
    
    if ticker0_best_fit == "t" and  ticker1_best_fit == "t":
        print("PAIR ELLIGIBLE OF T COPULA")
        
        df_0 = st.t.fit(ticker0_returns)[0]
        df_1 = st.t.fit(ticker1_returns)[0]
        
        u = np.sort(st.t.cdf(ticker0_returns, df_0))
        v = np.sort(st.t.cdf(ticker1_returns, df_1))
        
        
        len_u = len(u)
        len_v = len(v)
        print(f"len_u : { len_u }")
        print(f"len_v : { len_v }")
   
        
        data = np.hstack([u, v])
        
        # Fit a Gaussian copula to the joint distribution of u and v
        copula = StudentCopula()
     
        copula.fit(data)

        # Estimate joint and conditional densities
        pdf = copula.pdf(data)
        pu_given_v = copula.pdf(data) / pdf
        pv_given_u = copula.pdf(data) / pdf
        
        print(f"pu_given_v: { pu_given_v }")
        print(f"pv_given_u: { pv_given_u }")

        # Check if either of the conditional probabilities is close to 1
        if (pu_given_v > 0.95).any() and (pv_given_u < 0.05).any():
            # Open position
            print('Open position')
        
        elif (pu_given_v < 0.05).any() and (pv_given_u > 0.95).any():
            # Open position
            print('Open position')
        else:
            # Do not open position
            print('Do not open position')
        

    # # Define candidate distributions
    # distributions = [st.norm, st.lognorm, st.t, st.genextreme, st.genlogistic]

    # # Fit distributions and evaluate goodness of fit
    # results = []
    # for dist in distributions:
    #     # Fit distribution to ticker0
    #     params0 = dist.fit(ticker0_returns)
    #     # Calculate Kolmogorov-Smirnov test statistic and p-value for ticker1
    #     D0, p0 = st.kstest(ticker0_returns, dist.cdf, args=params0)
    #     # Fit distribution to ticker2
    #     params1 = dist.fit(ticker1_returns)
    #     # Calculate Kolmogorov-Smirnov test statistic and p-value for ticker2
    #     D1, p1 = st.kstest(ticker1_returns, dist.cdf, args=params1)
    #     # Store results
    #     results.append({'Distribution': dist.name, 
    #                     'Ticker0 D': D0, 
    #                     'Ticker0 p': p0, 
    #                     'Ticker1 D': D1, 
    #                     'Ticker1 p': p1,
    #                     'Ticker0 Fit': params0,
    #                     'Ticker1 fit': params1
    #                     })

    # # Print results
    # results_df = pd.DataFrame(results)
    # print(results_df)

    # # Select best fitting distribution for each ticker
    # ticker0_best_fit = results_df.loc[results_df['Ticker0 D'].idxmin(), 'Ticker0 Fit']
    # ticker1_best_fit = results_df.loc[results_df['Ticker1 D'].idxmin(), 'Ticker1 fit']
    
    # ticker0_best_fit_dist_name = results_df.loc[results_df['Ticker0 D'].idxmin(), 'Distribution']
    # ticker1_best_fit_dist_name = results_df.loc[results_df['Ticker1 D'].idxmin(), 'Distribution']
    
    # print('\nBest fitting distribution for Ticker0:', ticker0_best_fit_dist_name)
    # print('Best fitting distribution for Ticker1:', ticker1_best_fit_dist_name)
    
    # print('\nTicker 0 fit:', ticker0_best_fit)
    # print('Ticker 1 fit:', ticker1_best_fit)
    
    # if ticker0_best_fit_dist_name == "t" and ticker1_best_fit_dist_name == "t":
    #     u = st.t.cdf(ticker0_returns, ticker0_best_fit[0])
    #     v = st.t.cdf(ticker1_returns, ticker1_best_fit[0])
        
    #     print(f"u { u }")
    #     print(f"v { v }")
        
        # data = np.array()
        # studentCopula = StudentCopula()
        # studentCopula.fit(data)
        
    
    
    # data = np.vstack([np.vstack([ticker0_u, ticker0_v]).T, np.vstack([ticker1_u, ticker1_v]).T])
    
    # Remove the rows with NaN values by selecting only the rows where no NaN values exist
    
    
    # studentCopula = StudentCopula()
    # studentCopula.fit(data)
    # log_lik_student = studentCopula.log_lik(data)
    
    # print(f"log_lik_student {log_lik_student}")
    
    # frankCopula = archimedean.FrankCopula()
    # frankCopula.fit(data)
    # log_lik_frank = frankCopula.log_lik(data)
    
    # print(f"log_lik_frank {log_lik_frank}")
    
    # gumbelCopula = archimedean.GumbelCopula()
    # gumbelCopula.fit(data)
    # log_like_gumbel = gumbelCopula.log_lik(data)
    
    # print(f"log_like_gumbel {log_like_gumbel}")
    
    # claytonCopula = archimedean.ClaytonCopula()
    # claytonCopula.fit(data)
    # log_lik_clayton = claytonCopula.log_lik(data)
    
    # print(f"log_lik_clayton {log_lik_clayton}")
    
    # Fit copula to data
    
    # # Calculate conditional probability functions
    # pdf = copula.pdf(data)
    # pu_given_v = copula.pdf(np.vstack([ticker0_u, ticker0_v]).T) / pdf
    # pv_given_u = copula.pdf(np.vstack([ticker1_u, ticker1_v]).T) / pdf    

    # # Check if either of the conditional probabilities is close to 1
    # if (pu_given_v > 0.95).any() and (pv_given_u < 0.05).any():
    #     # Open position
    #     print('Open position')
    # elif (pu_given_v < 0.05).any() and (pv_given_u > 0.95).any():
    #     # Open position
    #     print('Open position')
    # else:
    #     # Do not open position
    #     print('Do not open position')
        
    