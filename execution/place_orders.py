import decimal
from utils.indicators.atr import get_atr
import risk_management.config as risk_config
import setup.config as config
from mt_helpers.get_symbols_data import get_symbol_rates
import MetaTrader5 as mt5
import json

def get_rounding(value):
    decimal_price = decimal.Decimal(f"{value}")
    price_rounding_value = len(str(decimal_price).split(".")[1])

    return price_rounding_value

def prepare_trade_order(symbol_info, trade_type):
    symbol = symbol_info.name
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    lot_step = symbol_info.volume_step
    max_lot_size = symbol_info.volume_max

    lot_step_rounding_value = get_rounding(lot_step)

    price = mt5.symbol_info_tick(symbol).ask

    price_rounding_value = get_rounding(price)

    atr, max_high, min_low = get_atr(symbol)

    latest_atr = round(atr[-1], price_rounding_value)

    sl_pips = 0

    if trade_type == "buy":
        sl_pips = (max_high - config.atr_multiplier*latest_atr)/tick_size
    else:
        sl_pips = (min_low + config.atr_multiplier*latest_atr)/tick_size
        
    tp_pips = risk_config.rr_ratio*sl_pips

    current_date = risk_config.current_date
    trading_record = risk_config.trading_record

    tradeable_capital = trading_record[current_date]["tradeable_capital"]

    trade_capital = risk_config.kelly_risk * tradeable_capital

    potential_position_size = round(trade_capital / (sl_pips * tick_value), lot_step_rounding_value)

    position_size = min(potential_position_size, max_lot_size)

    risk = round(sl_pips * tick_value * position_size, price_rounding_value)
    potential_profit = round(tp_pips * tick_value * position_size, price_rounding_value)

    return (sl_pips, tp_pips, position_size, trade_capital, risk, potential_profit)

def place_buy_order(ticker_symbol):
    selected = mt5.symbol_select(ticker_symbol, True)
    if not selected:
        print(f"Failed to select {ticker_symbol}")
        mt5.shutdown()
        quit()

    symbol_info = mt5.symbol_info(ticker_symbol)

    sl_pips, tp_pips, position_size, trade_capital, risk, potential_profit = prepare_trade_order(symbol_info, "buy")

    entry_price = mt5.symbol_info_tick(ticker_symbol).ask

    sl = entry_price - sl_pips*mt5.symbol_info(ticker_symbol).point
    tp = entry_price + tp_pips*mt5.symbol_info(ticker_symbol).point

    print(f"place sell order for {ticker_symbol} at {entry_price} with sl at {sl} (sl delta pips: {sl_pips})")

    print(f"trade capital before trade is {trade_capital}")
    print(f"position_size is {position_size}")
    print(f"risk is {risk}")
    print(f"potential profit is {potential_profit}")

    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": ticker_symbol,
        "volume": position_size,
        "type": mt5.ORDER_TYPE_BUY,
        "price": entry_price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # send a trading request
    result = mt5.order_send(request)
    print(result)

    # update margin if success
    if result.retcode == 10009:
        save_risk_state(risk)

def place_sell_order(ticker_symbol):
    selected = mt5.symbol_select(ticker_symbol, True)
    if not selected:
        print(f"Failed to select {ticker_symbol}")
        mt5.shutdown()
        quit()

    symbol_info = mt5.symbol_info(ticker_symbol)

    sl_pips, tp_pips, position_size, trade_capital, risk, potential_profit = prepare_trade_order(symbol_info, "sell")

    entry_price = mt5.symbol_info_tick(ticker_symbol).bid

    sl = entry_price + sl_pips*mt5.symbol_info(ticker_symbol).point
    tp = entry_price - tp_pips*mt5.symbol_info(ticker_symbol).point
    
    print(f"place sell order for {ticker_symbol} at {entry_price} with sl at {sl} (sl delta pips: {sl_pips})")

    print(f"trade capital before trade is {trade_capital}")
    print(f"position_size is {position_size}")
    print(f"risk is {risk}")
    print(f"potential profit is {potential_profit}")

    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": ticker_symbol,
        "volume": position_size,
        "type": mt5.ORDER_TYPE_SELL,
        "price": entry_price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # send a trading request
    result = mt5.order_send(request)
    print(result)

    # update margin if success
    if result.retcode == 10009:
        save_risk_state(risk)


def save_risk_state(order_risk):
    current_date = risk_config.current_date
    trading_record = risk_config.trading_record

    tradeable_capital = trading_record[current_date]["tradeable_capital"]
    new_tradeable_capital = tradeable_capital - order_risk
    
    total_risk = trading_record[current_date]["total_risk"]
    new_total_risk = total_risk + order_risk

    trading_record[current_date]["tradeable_capital"] = new_tradeable_capital
    trading_record[current_date]["total_risk"] = new_total_risk

    # save state
    risk_config.trading_record = trading_record

    # persist state
    with open("trading_day_record.json", "w") as outfile:
        json.dump(trading_record, outfile, indent=4)
    




            


        
            



    
