from enum import Enum
import setup.config as config

class Signal(Enum):
    WAIT = 0
    TRADE = 1
    CLOSE = 2

def perform_signal_check(z_score, max_zscore, avg_zscore, mode_zscore):
    z_score_thresh = round(0.8*max_zscore,1)
    # print(f"Z-score thresh for pair is {z_score_thresh}")
    # print(f"Avg Z-score for pair is {avg_zscore}")
    # print(f"Most common Z-score for pair is {mode_zscore}")
    # print(f"Max Z-score for pair is {max_zscore}")
    # print(f"Current Z-score for pair is {z_score}")
    
    
    if z_score == None:
        return Signal.WAIT

    if abs(z_score) > abs(z_score_thresh):
        return Signal.TRADE
    elif abs(z_score) < abs(z_score_thresh) and round(abs(z_score), 2) > 0.05:
        return Signal.WAIT
    else:
        return Signal.CLOSE