from execution.check_signal import perform_signal_check
from execution.place_orders import place_order
from strategy.cointegration.zscore import get_latest_zscore
from execution.check_signal import Signal
from execution.close_orders import close_order
from execution.check_latest_rsi import get_latest_rsi
import MetaTrader5 as mt5
from copula.copula_analysis import perform_copula_analysis


def scan(latest_cointegrated_pairs):
    for index, pair in enumerate(latest_cointegrated_pairs):
        print(f"pair index {index }")
        sym_0 = pair["sym_0"]
        sym_1 = pair["sym_1"]

        print("**********")
        print(f"{sym_0} / {sym_1} ")
        
        signal = perform_copula_analysis(sym_0=sym_0, sym_1=sym_1)
        
        if signal == Signal.TRADE_LONG:
            place_order(buy_symbol=sym_0, sell_symbol=sym_1)
        elif signal == Signal.TRADE_SHORT:
            place_order(buy_symbol=sym_1, sell_symbol=sym_0)
            
            
        
        
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