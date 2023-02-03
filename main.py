import MetaTrader5 as mt5

import state
from setup.initialize import initialize
import risk_management.config as risk_conf

from strategy.cointegration.cointegration import get_cointegrated_tickers
from strategy.cointegration.zscore import get_latest_zscore

from execution.check_signal import Signal
from execution.trade_direction import Trade
from execution.place_orders import place_buy_order, place_sell_order
from execution.close_orders import close_orders
from execution.check_signal import perform_signal_check

from utils.plotter import save_report

from time import sleep
import json
from datetime import datetime, timedelta
import pytz

has_reached_target = False
allow_scan = True

def update_cointegrated_pairs():
    state.latest_cointegrated_pairs = get_cointegrated_tickers()
    save_report(state.latest_cointegrated_pairs)
    
    json_file = open("trading_day_record.json")
    trading_record_dict = json.load(json_file)
    
    trading_record_dict["latest_cointegrated_pairs"] = state.latest_cointegrated_pairs
    
    # with open("trading_day_record.json", "w") as outfile:
    #     json.dump(trading_record_dict, outfile, indent=4)


def can_trade():
    tradeable_amount = risk_conf.set_tradeable_capital()
    if round(tradeable_amount) > 0:
        return True
    else:
        return False

def get_latest_prices(pair):
    sym_0_info = mt5.symbol_info_tick(pair["sym_0"])
    sym_1_info = mt5.symbol_info_tick(pair["sym_1"])
 
    latest_price_0 = (sym_0_info.bid + sym_0_info.ask)  / 2
    latest_price_1 = (sym_1_info.bid + sym_1_info.ask)  / 2

    return latest_price_0, latest_price_1

def reset_tradeable_capital_if_needed():
    tz = pytz.timezone("CET") # FTMO timezone
    current_trading_day = datetime.now(tz).date()
    previous_trading_day = current_trading_day - timedelta(days=1)

    current_trading_day_str = f"{current_trading_day}"
    previous_trading_day_str = f"{previous_trading_day}"

    risk_conf.current_date = current_trading_day_str

    json_file = open("trading_day_record.json")
    trading_record_dict = json.load(json_file)

    if not (current_trading_day_str in trading_record_dict.keys()):
        global has_reached_target
        
        tradeable_capital = risk_conf.set_tradeable_capital()
        previous_total_risk = 0
        has_reached_target = False

        if previous_trading_day_str in trading_record_dict.keys():
            previous_total_risk = trading_record_dict[previous_trading_day_str]["total_risk"]
            tradeable_capital -= previous_total_risk

        trading_record_dict[current_trading_day_str] = {
            "tradeable_capital": tradeable_capital,
            "total_risk": previous_total_risk
        }

    # save
    risk_conf.trading_record = trading_record_dict

     # persist
    with open("trading_day_record.json", "w") as outfile:
        json.dump(trading_record_dict, outfile, indent=4)

def close_all_positions():
    print("Closing all positions")

    positions=mt5.positions_get()

    while len(positions) > 0:
        for position in positions:
            close_order(position)

def check_profit():
    account_info_dict = mt5.account_info()._asdict()

    equity = account_info_dict["equity"]
    balance = account_info_dict["balance"]

    floating_pnl = equity - balance
    target = 1000 if balance > 200000 else 1000 + (200000-balance)

    if floating_pnl >= target:
        print("Target reached!")

        close_all_positions()
        return True

    return False

def close_order(position):
    symbol = position.symbol
    volume = position.volume
    type = 1 if position.type == 0 else 0
    price = mt5.symbol_info_tick(symbol).bid if type == 1 else mt5.symbol_info_tick(symbol).ask
    position_id = position.identifier
    
    request={
         "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": type,
        "position": position_id,
        "price": price,
        "deviation": 20,
        "magic": 234000,
        "comment": "python script close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,}

    # send a trading request
    result=mt5.order_send(request)

    if result.retcode == 10009:
        print(f"position { position_id } for { symbol } closed successfully!")

def scan():
    for index, pair in enumerate(state.latest_cointegrated_pairs):
            print(f"pair index {index }")
            pair_id = pair["uid"]
            sym_0 = pair["sym_0"]
            sym_1 = pair["sym_1"]

            print("**********")
            print(f"{sym_0} / {sym_1} ")
            latest_price_0, latest_price_1 = get_latest_prices(pair)
            latest_zscore = get_latest_zscore(pair, latest_price_0, latest_price_1)
            signal = perform_signal_check(latest_zscore)
            spread_0 = mt5.symbol_info(sym_0).spread
            spread_1 = mt5.symbol_info(sym_1).spread 
            
            print(f"spread for { sym_0} is {spread_0}")
            print(f"spread for { sym_1} is {spread_1}")

            if signal == Signal.TRADE:
                print(f"Z-score { latest_zscore } crossed threshold. Open Trade.")

                if latest_zscore < 0:
                    # buy first symbol
                    if spread_0 <= 15:
                        selected=mt5.symbol_select(sym_0,True)
                        if not selected:
                            print(f"Failed to select {sym_0}")
                        
                            positions=mt5.positions_get(symbol=sym_0)
                            if positions == ():
                                print(f"No position for { sym_0 }")
                                place_buy_order(sym_0)
                            else:
                                for position in positions:
                                    if position.type == 0:
                                        if position.profit > 50:
                                            print(f"position for { sym_0 } profitable, adding new position")
                                            place_buy_order(sym_0)
                    if spread_1 <= 15:    
                        # sell second symbol
                        selected=mt5.symbol_select(sym_1,True)
                        if not selected:
                            print(f"Failed to select {sym_1}")
                        
                        positions=mt5.positions_get(symbol=sym_1)
                        if positions == ():
                            print(f"No position for { sym_1 }")
                            place_sell_order(sym_1)
                        else:
                            for position in positions:
                                if position.type == 1:
                                    if position.profit > 50:
                                        print(f"position for { sym_1 } profitable, adding new position")
                                        place_sell_order(sym_1)
                               
                else:
                    # sell first symbol
                    if spread_0 <= 15:
                        selected=mt5.symbol_select(sym_0,True)
                        if not selected:
                            print(f"Failed to select {sym_0}")

                        positions=mt5.positions_get(symbol=sym_0)
                        if positions == ():
                            print(f"No position for { sym_0 }")
                        
                            place_sell_order(sym_0)
                        else:
                            for position in positions:
                                if position.type == 1:
                                    if position.profit > 50:
                                        print(f"position for { sym_0 } profitable, adding new position")
                                        place_sell_order(sym_0)
                              
                        
                    # buy second symbol
                    if spread_1 <= 15:
                        selected=mt5.symbol_select(sym_1,True)
                        if not selected:
                            print(f"Failed to select {sym_1}")

                        positions=mt5.positions_get(symbol=sym_1)
                        if positions == ():
                            print(f"No position for { sym_1 }")
                        
                            place_buy_order(sym_1)
                        else:
                            for position in positions:
                                if position.type == 0:
                                    if position.profit > 50:
                                        print(f"position for { sym_1 } profitable, adding new position")
                                        place_buy_order(sym_1)
                               

            if signal == Signal.WAIT:
                print(f"Waiting for Z-score { latest_zscore } to cross threshold.")
            if signal == Signal.CLOSE:
                print(f"Z-score { latest_zscore } is zero")
            
            if index == len(state.latest_cointegrated_pairs) - 1:
                last_scan_time_str = f"{datetime.now()}"

                trading_record = risk_conf.trading_record
                trading_record[risk_conf.current_date]["last_scan_time"] = last_scan_time_str

                risk_conf.trading_record = trading_record

                with open("trading_day_record.json", "w") as outfile:
                    json.dump(trading_record, outfile, indent=4)
                    
            print("**********")
            

if __name__ == "__main__":
    initialize()
    update_cointegrated_pairs()
    
    while True:
        reset_tradeable_capital_if_needed()
        
        # positions=mt5.positions_get()
        # if len(positions) == 0:
        #     update_cointegrated_pairs()
        # else:
        #     json_file = open("trading_day_record.json")
        #     trading_record_dict = json.load(json_file)
            
        #     if "latest_cointegrated_pairs" in trading_record_dict.keys():
        #         persisted_cointegrated_pairs = trading_record_dict["latest_cointegrated_pairs"]
                
        #         if len(persisted_cointegrated_pairs) > 0 :
        #             state.latest_cointegrated_pairs = persisted_cointegrated_pairs
        #         else:
        #             update_cointegrated_pairs()
        #     else:
        #         update_cointegrated_pairs()
                
        has_reached_target = check_profit()
        
        current_date = risk_conf.current_date
        trading_record = risk_conf.trading_record
        
        if "last_scan_time" in trading_record[current_date].keys():
                last_scan_time_json = risk_conf.trading_record[risk_conf.current_date]["last_scan_time"]
                last_scan_time = datetime.strptime(last_scan_time_json, '%Y-%m-%d %H:%M:%S.%f')

                if datetime.now() < last_scan_time + timedelta(minutes=5):
                    allow_scan = False
                else:
                    allow_scan = True
                    
        if allow_scan and not(has_reached_target):
            scan()
            
        
       
        

        