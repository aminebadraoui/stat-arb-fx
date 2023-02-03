import risk_management.config as risk_config
import MetaTrader5 as mt5
import json

def close_orders(symbol, pair_id):
    current_date = risk_config.current_date
    trading_record = risk_config.trading_record

    pair_orders = trading_record[current_date]["orders"][pair_id]

    successful_closes = []

    pair_risk = 0

    for order in pair_orders:
        symbol = order["symbol"]
        volume = order["lot"]
        type = mt5.ORDER_TYPE_SELL if order["direction"] == "buy" else mt5.ORDER_TYPE_BUY
        position_id = order["order_id"]
        deviation = 20
        price = mt5.symbol_info_tick(symbol).bid if order["direction"] == "buy" else mt5.symbol_info_tick(symbol).ask
        pair_risk += order["order_risk"]

        request={
         "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": type,
        "position": position_id,
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,}

        # send a trading request
        result=mt5.order_send(request)

        if result.retcode == 10009:
            successful_closes.append(True)

    save_risk_state(pair_risk, pair_id)


def save_risk_state(pair_risk, pair_id):
    current_date = risk_config.current_date
    trading_record = risk_config.trading_record

    tradeable_capital = trading_record[current_date]["tradeable_capital"]
    new_tradeable_capital = tradeable_capital + pair_risk

    trading_record[current_date]["tradeable_capital"] = new_tradeable_capital
 
    if pair_id in trading_record[current_date]["orders"].keys():
        del trading_record[current_date]["orders"][pair_id]
    
    total_risk = trading_record[current_date]["total_risk"]

    new_total_risk = total_risk - pair_risk

    trading_record[current_date]["total_risk"] = new_total_risk

    # save state
    risk_config.trading_record = trading_record

    # persist state
    with open("trading_day_record.json", "w") as outfile:
        json.dump(trading_record, outfile, indent=4)
