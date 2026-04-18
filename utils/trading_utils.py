"""
Trading utility functions
"""

from datetime import datetime
import pandas as pd
import numpy as np


def setup_market_data(system_wrapper, data_point):
    """
    Setup market data from a data point.

    Args:
        system_wrapper: SystemWrapper instance
        data_point: Dictionary with market data

    Returns:
        dict: Processed market data row
    """
    if system_wrapper.data_mode == 'HISTORICAL':
        current_price = float(data_point['close'])
        new_row = data_point
    else:
        # Simulation mode
        last_price = float(system_wrapper.market_history.iloc[-1]['close'])
        current_price = last_price * (1 + np.random.uniform(-0.001, 0.001))
        new_row = {
            'timestamp': datetime.now(),
            'open': current_price,
            'high': current_price,
            'low': current_price,
            'close': current_price,
            'volume': 0.0
        }

    return new_row


def process_trading_action(system_wrapper, action, price):
    """
    Process trading action and update PnL.

    Args:
        system_wrapper: SystemWrapper instance
        action: Trading action (CALL, PUT, HOLD, WAIT)
        price: Current price

    Returns:
        float: Profit/loss from this action
    """
    profit = 0.0

    if action not in ["WAIT", "HOLD"]:
        is_win = np.random.random() > 0.45
        if is_win:
            profit = system_wrapper.trade_amount * 0.85
            system_wrapper.log(f"💰 WIN | {action} | Prix: {price:.2f} | PnL: +{profit:.2f}$")
        else:
            profit = -system_wrapper.trade_amount
            system_wrapper.log(f"🔻 LOSS | {action} | Prix: {price:.2f} | PnL: {profit:.2f}$")

    return profit


def check_risk_limits(system_wrapper):
    """
    Check if risk limits are reached.

    Args:
        system_wrapper: SystemWrapper instance

    Returns:
        tuple: (stop_reached: bool, reason: str)
    """
    if system_wrapper.daily_pnl <= -system_wrapper.stop_loss_limit:
        return True, "🛑 Stop Loss touché."

    if system_wrapper.daily_pnl >= system_wrapper.take_profit_limit:
        return True, "🥂 Take Profit touché."

    return False, ""
