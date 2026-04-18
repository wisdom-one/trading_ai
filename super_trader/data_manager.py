import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self, filename="data.csv"):
        self.filename = filename
        self.columns = [
            "timestamp", "open", "high", "low", "close", "volume",
            "rsi", "macd", "macd_signal", "upper_band", "lower_band", "atr",
            "action", "reward", "pnl"
        ]
        self._initialize_file()

    def _initialize_file(self):
        if not os.path.exists(self.filename):
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(self.filename, index=False)

    def log_step(self, market_data, indicators, action, reward, pnl):
        """
        Logs a single step of the trading agent.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Construct row
        row = {
            "timestamp": timestamp,
            "open": market_data.get('open', 0),
            "high": market_data.get('high', 0),
            "low": market_data.get('low', 0),
            "close": market_data.get('close', 0),
            "volume": market_data.get('volume', 0),
            "rsi": indicators.get('rsi', 0),
            "macd": indicators.get('macd', 0),
            "macd_signal": indicators.get('macd_signal', 0),
            "upper_band": indicators.get('upper_band', 0),
            "lower_band": indicators.get('lower_band', 0),
            "atr": indicators.get('atr', 0),
            "action": action,
            "reward": reward,
            "pnl": pnl
        }
        
        df = pd.DataFrame([row])
        df.to_csv(self.filename, mode='a', header=False, index=False)

    def load_data(self):
        """Loads the training data for the RL agent."""
        if os.path.exists(self.filename):
            return pd.read_csv(self.filename, names=self.columns, skiprows=1)
        return pd.DataFrame(columns=self.columns)

    def clear_data(self):
        """Cleans the data.csv file to avoid redundant training data on next evolution."""
        df = pd.DataFrame(columns=self.columns)
        df.to_csv(self.filename, index=False)
