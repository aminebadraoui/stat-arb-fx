import decimal
from utils.indicators.atr import get_atr
import risk_management.config as risk_config
import setup.config as config
from mt_helpers.get_symbols_data import get_symbol_rates
import MetaTrader5 as mt5
import json
from execution.check_latest_rsi import get_latest_rsi
def place_order(buy_symbol, sell_symbol):
    # buy first symbol
    selected=mt5.symbol_select(buy_symbol,True)
    if not selected:
        print(f"Failed to select {buy_symbol}")
    
   
    
    latest_rsi_buy = get_latest_rsi(buy_symbol)
    positions = mt5.positions_get(symbol=buy_symbol)
    if positions == () and get_latest_rsi(buy_symbol) < 30:
        print(f"No position for { buy_symbol }, adding new position")
        place_buy_order(buy_symbol)
    else:
        for position in positions:
            if position.type == 0 and get_latest_rsi(buy_symbol) < 30 :
                print(f"position for { buy_symbol } profitable and rsi {latest_rsi_buy} is oversold, adding new position")
                place_buy_order(buy_symbol)
                                                    
    # sell second symbol
    
    selected=mt5.symbol_select(sell_symbol,True)
    if not selected:
        print(f"Failed to select {sell_symbol}")
        
    positions = mt5.positions_get(symbol=sell_symbol)
    
    latest_rsi_sell = get_latest_rsi(sell_symbol)
                            
    if positions == () and get_latest_rsi(sell_symbol) > 65:
        print(f"No position for { sell_symbol }")
        place_sell_order(sell_symbol)
    else:
        for position in positions:
            if position.type == 1 and get_latest_rsi(sell_symbol) > 65:
                print(f"position for { sell_symbol } profitable and latest rsi {latest_rsi_sell} is overbought , adding new position")
                place_sell_order(sell_symbol)
                                            
def get_rounding(value):
    decimal_price = decimal.Decimal(f"{value}")
    price_rounding_value = len(str(decimal_price).split(".")[1])

    return price_rounding_value

def compute_sl(symbol, trade_type):
    price = mt5.symbol_info_tick(symbol).ask
    price_rounding_value = get_rounding(price)
    
    atr, max_high, min_low = get_atr(symbol)

    latest_atr = round(atr[-1], price_rounding_value)
    
    sl = config.atr_multiplier*latest_atr
 
    return round(sl, price_rounding_value)

def place_buy_order(ticker_symbol):
    selected = mt5.symbol_select(ticker_symbol, True)
    if not selected:
        print(f"Failed to select {ticker_symbol}")
        mt5.shutdown()
        quit()

    symbol_info = mt5.symbol_info(ticker_symbol)
    symbol = symbol_info.name
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    lot_step = symbol_info.volume_step
    max_lot_size = symbol_info.volume_max
    lot_step_rounding_value = get_rounding(lot_step)
    
    price = mt5.symbol_info_tick(symbol).ask
    price_rounding_value = get_rounding(price)
    
    tradeable_capital = risk_config.get_tradeable_capital()
    trade_capital = risk_config.kelly_risk * tradeable_capital

    entry_price = mt5.symbol_info_tick(ticker_symbol).ask

    sl = entry_price - round(compute_sl(symbol=ticker_symbol, trade_type="buy"), price_rounding_value)
    
    if sl > entry_price:
        print("Invalid stop loss")
        return 
    
    tp = round(entry_price + risk_config.rr_ratio*(abs(entry_price-sl)), price_rounding_value)
    
    sl_pips = abs(entry_price-sl)/tick_size
    tp_pips = abs(entry_price-tp)/tick_size
    
    print(f"entry_price {entry_price}")
    print(f"sl {sl}")
    print(f"abs diff price-sl {abs(entry_price-sl)}")
    print(f"rr*diff {risk_config.rr_ratio*abs(entry_price-sl)}")
    print(f"tp {entry_price + (risk_config.rr_ratio*abs(entry_price-sl))}")
    
    if not(sl_pips > 0) or not(tick_value > 0):
        return 
    
    potential_position_size = round(trade_capital / (sl_pips * tick_value), lot_step_rounding_value)
    position_size = min(potential_position_size, max_lot_size)
    
    risk = round(sl_pips * tick_value * position_size, price_rounding_value)
    potential_profit = round(tp_pips * tick_value * position_size, price_rounding_value)

    print(f"place buy order for {ticker_symbol} at {entry_price} with sl at {sl} (sl delta pips: {sl_pips})")

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

    spread = abs(entry_price - mt5.symbol_info(ticker_symbol).bid)
    spread_pips = spread/tick_size
    spread_value = spread_pips*tick_value*position_size
    
    print(f"Spread value is: { spread_value } ")
    # send a trading request
    if spread_value < 20:
        result = mt5.order_send(request)
        print(result)
    else:
        print(f"buy order for {ticker_symbol} not executed because spread { spread_value } too high")

def place_sell_order(ticker_symbol):
    selected = mt5.symbol_select(ticker_symbol, True)
    if not selected:
        print(f"Failed to select {ticker_symbol}")
        mt5.shutdown()
        quit()

    symbol_info = mt5.symbol_info(ticker_symbol)
    symbol = symbol_info.name
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    lot_step = symbol_info.volume_step
    max_lot_size = symbol_info.volume_max
    lot_step_rounding_value = get_rounding(lot_step)
    
    price = mt5.symbol_info_tick(symbol).ask
    price_rounding_value = get_rounding(price)
    
    tradeable_capital = risk_config.get_tradeable_capital()
    trade_capital = risk_config.kelly_risk * tradeable_capital

    entry_price = mt5.symbol_info_tick(ticker_symbol).bid

    sl = entry_price + compute_sl(symbol=ticker_symbol, trade_type="sell")
    
    if sl < entry_price:
        print("Invalid stop loss")
        return 
    
    tp = round(entry_price - ( risk_config.rr_ratio*abs(entry_price-sl) ), price_rounding_value)
    
    print(f"entry_price {entry_price}")
    print(f"sl {sl}")
    print(f"abs diff price-sl {abs(entry_price-sl)}")
    print(f"rr*diff {risk_config.rr_ratio*abs(entry_price-sl)}")
    print(f"tp {entry_price - (risk_config.rr_ratio*abs(entry_price-sl))}")
    
    sl_pips = abs(entry_price-sl)/tick_size
    tp_pips = abs(entry_price-tp)/tick_size
    
    if not(sl_pips > 0) or not(tick_value > 0):
        return 
    
    potential_position_size = round(trade_capital / (sl_pips * tick_value), lot_step_rounding_value)
    position_size = min(potential_position_size, max_lot_size)
    
    risk = round(sl_pips * tick_value * position_size, price_rounding_value)
    potential_profit = round(tp_pips * tick_value * position_size, price_rounding_value)
    
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

    spread = abs(entry_price - mt5.symbol_info(ticker_symbol).ask)
    spread_pips = spread/tick_size
    spread_value = spread_pips*tick_value*position_size
    
    print(f"Spread value is: { spread_value } ")
    
    # send a trading request
    if spread_value < 20:
        result = mt5.order_send(request)
        print(result)
    else:
        print(f"sell for {ticker_symbol} not taken because spread { spread_value } too high")




            


        
            



    
