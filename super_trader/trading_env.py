import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from .indicators import Indicators

class TradingEnv(gym.Env):
    metadata = {'render_modes': ['human'], 'render_fps': 30}

    def __init__(self, df, window_size=50):
        super().__init__()
        self.df = df.copy() # Use a copy to avoid modifying original DataFrame
        self.window_size = window_size
        self.current_step = window_size

        # Calculate indicators once for the entire DataFrame
        self.indicators_calculator = Indicators()
        self.df['rsi'] = self.indicators_calculator.calculate_rsi(self.df)
        macd, signal = self.indicators_calculator.calculate_macd(self.df)
        self.df['macd'] = macd
        self.df['macd_signal'] = signal
        upper_band, lower_band = self.indicators_calculator.calculate_bollinger_bands(self.df)
        self.df['upper_band'] = upper_band
        self.df['lower_band'] = lower_band
        self.df['atr'] = self.indicators_calculator.calculate_atr(self.df)
        self.df['regime'] = self.indicators_calculator.detect_market_regime(self.df)

        # Drop rows with NaN values resulting from indicator calculations
        self.df.dropna(inplace=True)
        # Reset index after dropping NaNs
        self.df.reset_index(drop=True, inplace=True)

        # Action space: 0 = HOLD, 1 = BUY, 2 = SELL
        self.action_space = spaces.Discrete(3)

        # Observation space: [rsi, macd, atr, close, regime]
        # Define the number of features in your observation
        self.n_features = 5 # rsi, macd, atr, close, regime
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf,
                                            shape=(self.n_features,),
                                            dtype=np.float32)

        self.initial_balance = 10000
        self.balance = self.initial_balance
        self.shares = 0
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance

    def _get_obs(self):
        # Return a window of relevant data for the current step
        current_row = self.df.iloc[self.current_step]
        obs = np.array([
            current_row['rsi'],
            current_row['macd'],
            current_row['atr'],
            current_row['close'],
            current_row['regime']
        ], dtype=np.float32)
        return obs

    def _get_info(self):
        return {
            "balance": self.balance,
            "shares": self.shares,
            "net_worth": self.net_worth,
        }

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.balance = self.initial_balance
        self.shares = 0
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance
        self.current_step = self.window_size

        observation = self._get_obs()
        info = self._get_info()
        return observation, info

    def step(self, action):
        self.current_step += 1

        if self.current_step > len(self.df) - 1: # End of data
            self.current_step = self.window_size # Reset for next episode if needed
            # Or handle episode termination
            terminated = True
            truncated = False
            reward = 0 # No reward for ending
            observation = self._get_obs()
            info = self._get_info()
            return observation, reward, terminated, truncated, info

        current_price = self.df['close'].values[self.current_step]
        previous_net_worth = self.net_worth

        if action == 1: # BUY
            if self.balance >= current_price:
                self.shares += 1
                self.balance -= current_price
        elif action == 2: # SELL
            if self.shares > 0:
                self.shares -= 1
                self.balance += current_price

        self.net_worth = self.balance + self.shares * current_price

        reward = self.net_worth - previous_net_worth # Simple reward: change in net worth

        terminated = False
        truncated = False

        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, terminated, truncated, info

    def render(self):
        pass

    def close(self):
        pass
