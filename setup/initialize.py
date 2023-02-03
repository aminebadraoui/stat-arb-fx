import MetaTrader5 as mt5
import setup.config as config


def initialize():
    # connect to MetaTrader 5
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
    else:
        print("MT5 Initialized")

    # now connect to another trading account specifying the password
    account = 1051458803
    authorized = mt5.login(config.login,
                           password=config.password,
                           server="FTMO-Demo"
                           )
    if authorized:
        print("Connected!")
    else:
        print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))
