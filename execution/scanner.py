from execution.check_signal import perform_signal_check
from execution.place_orders import place_order
from strategy.cointegration.zscore import get_latest_zscore
from execution.check_signal import Signal
from execution.close_orders import close_order
from execution.check_latest_rsi import get_latest_rsi
import MetaTrader5 as mt5


def scan(latest_cointegrated_pairs):
    for index, pair in enumerate(latest_cointegrated_pairs):
        print(f"pair index {index }")
        sym_0 = pair["sym_0"]
        sym_1 = pair["sym_1"]

        print("**********")
        print(f"{sym_0} / {sym_1} ")
        
        latest_zscore, max_zscore, avg_zscore, mode_zscore = get_latest_zscore(sym_0, sym_1)
        signal = perform_signal_check(latest_zscore, max_zscore, avg_zscore, mode_zscore)
       
        if signal == Signal.TRADE:
            if latest_zscore < 0:
                if get_latest_rsi(sym_0) < 25 and get_latest_rsi(sym_1) > 75:
                    place_order(buy_symbol=sym_0, sell_symbol=sym_1)
            else:
                if get_latest_rsi(sym_1) < 25 and get_latest_rsi(sym_0) > 75:
                    place_order(buy_symbol=sym_1, sell_symbol=sym_0)
       
        if signal == Signal.WAIT:
            print(f"Waiting for signal...")
        if signal == Signal.CLOSE:
            print(f"Waiting for signal...")
        
        # RSI check
        # positions_0 = mt5.positions_get(symbol=sym_0)
            
        # if len(positions_0) > 0:
        #     for position in positions_0:
        #         rsi = get_latest_rsi(sym_0)
        #         print(f"latest RSI for {sym_0} is {rsi}")
        #         if position.type == 1 and rsi > 71:
        #             place_order(buy_symbol=sym_1, sell_symbol=sym_0)
            
        # positions_1 = mt5.positions_get(symbol=sym_1)
            
        # if len(positions_1) > 0:
        #     for position in positions_1:
        #         rsi = get_latest_rsi(sym_1)
        #         print(f"latest RSI for {sym_1} is {rsi}")
        #         if position.type == 1 and rsi > 71:
        #             place_order(buy_symbol=sym_0, sell_symbol=sym_1)
            

        print("**********")