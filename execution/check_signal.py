from enum import Enum
import state
import setup.config as config

class Signal(Enum):
    WAIT = 0
    TRADE = 1
    CLOSE = 2

def perform_signal_check(z_score):
    thresh = config.z_score_tresh

    if abs(z_score) > abs(thresh):
        return Signal.TRADE
    elif abs(z_score) < abs(thresh) and round(abs(z_score), 2) > 0.05:
        return Signal.WAIT
    else:
        return Signal.CLOSE