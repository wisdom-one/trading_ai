import numpy as np
import pandas as pd

class Indicators:
    """
    Library of technical indicators and mathematical models for the Super Trader.
    """

    @staticmethod
    def calculate_rsi(data, window=14):
        """Relative Strength Index"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(data, slow=26, fast=12, signal=9):
        """Moving Average Convergence Divergence"""
        exp1 = data['close'].ewm(span=fast, adjust=False).mean()
        exp2 = data['close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line

    @staticmethod
    def calculate_bollinger_bands(data, window=20, num_std=2):
        """Bollinger Bands"""
        rolling_mean = data['close'].rolling(window=window).mean()
        rolling_std = data['close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band

    @staticmethod
    def calculate_atr(data, window=14):
        """Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(window=window).mean()

    @staticmethod
    def kelly_criterion(win_prob, win_loss_ratio):
        """
        Kelly Criterion for position sizing.
        f* = (bp - q) / b
        where:
        f* is the fraction of the current bankroll to wager,
        b is the net odds received on the wager (b to 1),
        p is the probability of winning,
        q is the probability of losing (1 - p).
        """
        if win_loss_ratio == 0:
            return 0
        return (win_prob * win_loss_ratio - (1 - win_prob)) / win_loss_ratio

    @staticmethod
    def detect_market_regime(data, window=50):
        """
        Simple regime detection:
        1 = Bullish (Price > SMA50)
        -1 = Bearish (Price < SMA50)
        0 = Sideways (Low volatility)
        """
        sma = data['close'].rolling(window=window).mean()
        price = data['close'].iloc[-1]
        
        # Volatility check
        std = data['close'].rolling(window=window).std().iloc[-1]
        mean_price = data['close'].mean()
        
        if std / mean_price < 0.005: # Very low volatility
            return 0
            
        if price > sma.iloc[-1]:
            return 1
        else:
            return -1
