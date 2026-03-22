# Risk Management Module for Algorithmic Trading Bot

def calculate_position_size(account_balance, risk_percentage, entry_price, stop_loss_distance):
    """Calculate the position size based on account balance, risk percentage, entry price, and stop loss distance."""
    risk_amount = account_balance * risk_percentage / 100
    position_size = risk_amount / stop_loss_distance
    return position_size


def calculate_stop_loss(entry_price, stop_loss_distance):
    """Calculate the stop loss price based on entry price and stop loss distance."""
    stop_loss_price = entry_price - stop_loss_distance
    return stop_loss_price


def calculate_take_profit(entry_price, take_profit_distance):
    """Calculate the take profit price based on entry price and take profit distance."""
    take_profit_price = entry_price + take_profit_distance
    return take_profit_price
