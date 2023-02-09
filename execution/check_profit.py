import MetaTrader5 as mt5

def check_profit(starting_balance):
    target = 1000 if starting_balance > 200000 else 1000 + (200000-starting_balance)
    

    if (mt5.account_info().equity - mt5.account_info().balance) >= target:
        return True
    
    if (mt5.account_info().equity - mt5.account_info().balance) + 200000 >= target + starting_balance:
        return True

    return False