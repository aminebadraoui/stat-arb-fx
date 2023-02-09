import MetaTrader5 as mt5
import setup.config as config


def initialize():
    # connect to MetaTrader 5
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        return False
    else:
        print("MT5 Initialized")
        
    # Ask for credentials
    account = input("Enter account number:")
    password = input("Enter account password:")
    server = input("Enter server:")
 
    # now connect to another trading account specifying the password
    authorized = mt5.login(int(account),
                           password=password,
                           server=server
                           )
    if authorized:
        print("Connected!")
        return True
    else:
        print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))
        return False
