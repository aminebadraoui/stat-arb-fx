import risk_management.config as risk_config
import MetaTrader5 as mt5

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
    else:
        print(f"position { position_id } for { symbol } failed to close!")
        print(result)
        
def close_all_positions():
    print("Closing all positions")

    positions=mt5.positions_get()

    if len(positions) > 0:
        for position in positions:
            close_order(position)

