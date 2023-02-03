import MetaTrader5 as mt5
import pandas as pd
from setup import config
from utils.dump_json import  dump_json

def get_symbol_rates(symbol):
    name = symbol["name"]
    digits = symbol["digits"]
    tick_value = symbol["trade_tick_value"]
    tick_size = symbol["trade_tick_size"]
    volume_step = symbol["volume_step"]

    rates = mt5.copy_rates_from_pos(name, config.timeframe, 0, config.period)
    rates_dict = pd.DataFrame(rates).to_dict()

    symbol_data = {
        "name": name,
        "digits": digits,
        "tick_value": tick_value,
        "tick_size": tick_size,
        "volume_step": volume_step,
        "rates": rates_dict
    }

    return symbol_data


def get_all_symbols_data():
    price_data = []

    symbols_res = mt5.symbols_get(group="*USD")
    symbols = []

    for symbol in symbols_res:
        symbols.append(symbol._asdict())

    for symbol in symbols:
        symbol_data = get_symbol_rates(symbol)
        price_data.append(symbol_data)

    dump_json(price_data, "symbols")

    return price_data