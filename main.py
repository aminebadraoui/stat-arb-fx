import MetaTrader5 as mt5
from setup.initialize import initialize
import risk_management.config as risk_conf
from strategy.cointegration.cointegration import get_cointegrated_tickers
from execution.close_orders import close_all_positions
from execution.check_profit import check_profit
from execution.scanner import scan
from execution.place_orders import compute_sl

import pytz
import sys

import json
from datetime import datetime, timedelta

def update_cointegrated_pairs():
    # *UK100*, *GER40*, *US100*, *US500*, *US30*, *AMZN*, *BABA*, *BAC*, *FB*, *GOOG*, *MSFT*, *NFLX*, *AAPL*, *NVDA*, *META*, *PFE*, *RACE*, *WMT*, 
    currency_group = "*GBPUSD*, *USDCHF*, *USDJPY*, *USDCAD*, *AUDUSD*, *AUDNZD*, *AUDCAD*, *AUDCHF*, *AUDJPY*, *CHFJPY*, *EURGBP*, *EURAUD*, *EURJPY*, *NZDUSD*, *EURNZD*, *EURCAD*, *GBPCHF*, *GBPJPY*, *CADCHF*, *CADJPY*, *GBPAUD*, *GBPCAD*, *GBPNZD*, *NZDCAD*, *NZDCHF*, *NZDJPY* "
    commodities_group = "*XAGEUR*, *XAGUSD*, *XAUAUD*, *XAGAUD*, *XAUEUR*, *XPTUSD*, *XAUUSD*, *XPDUSD*"
    indices_group = "*UK100.cash*, *GER40.cash*, *US100.cash*, *US500.cash*, *US30.cash*"
    symbols = mt5.symbols_get(group=",".join([currency_group, commodities_group, indices_group]))
    # for symbol in symbols:
    #     print(symbol.name)
    return get_cointegrated_tickers(symbols)

if __name__ == "__main__":
    has_reached_target = False
    allow_scan = True
    tz = pytz.timezone("CET") # FTMO timezone
    latest_cointegrated_pairs = []
    trading_record_dict = {}
    
    if not initialize():
        sys.exit()
        
    while True:
         # Get current date
        current_trading_day = datetime.now(tz).date()
        
        current_trading_day_str = f"{current_trading_day}"
    
        try:
            with open("trading_day_record.json") as json_file:
                trading_record_dict = json.load(json_file)
        except IOError:
            print('Creating new.')
            
    
        if not(current_trading_day_str in trading_record_dict.keys()):
            trading_record_dict[current_trading_day_str] = {}
            has_reached_target = False
            latest_cointegrated_pairs = []
        
        latest_cointegrated_pairs = update_cointegrated_pairs()
        trading_record_dict[current_trading_day_str]["latest_cointegrated_pairs"] = latest_cointegrated_pairs
        trading_record_dict[current_trading_day_str]["has_reached_target"] = has_reached_target
        trading_record_dict[current_trading_day_str]["balance"] = mt5.account_info().balance
            
        if len(mt5.positions_get()) > 0: 
            if check_profit(mt5.account_info().balance):
                    print("Target Reached!")
                    
                    close_all_positions()
                    has_reached_target = True
                    trading_record_dict[current_trading_day_str]["has_reached_target"] = has_reached_target
                    
                    print("All positions closed.")
 
        # if not(has_reached_target):
        scan(latest_cointegrated_pairs)
        trading_record_dict[current_trading_day_str]["last_scan_time"] = f"{datetime.now(tz)}"
                        
        # Record Risk
        trading_record_dict[current_trading_day_str]["total_risk"] = risk_conf.get_current_total_risk()
        
        with open("trading_day_record.json", "w") as outfile:
                json.dump(trading_record_dict, outfile, indent=4)
        





