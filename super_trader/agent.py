import numpy as np
import pandas as pd
from stable_baselines3 import PPO
import os
from .indicators import Indicators
from .data_manager import DataManager
from .trading_env import TradingEnv

class SuperTrader:
    def __init__(self):
        self.indicators = Indicators()
        self.data_manager = DataManager()
        self.model = None
        self.is_learning = True
        self.trade_history = []
        
        # Load or Create Model
        self.load_model()

    def load_model(self):
        if os.path.exists("super_trader_ppo.zip"):
            self.model = PPO.load("super_trader_ppo")
        else:
            # Initialize a dummy model if none exists (requires an environment)
            # For now, we will use a placeholder or handle the 'None' case in prediction
            self.model = None
            print("No existing model found. Model will be initialized upon first evolution.") 

    def analyze_market(self, market_data_history):
        """
        Analyzes market data using mathematical models.
        market_data_history: DataFrame with 'close', 'high', 'low' columns.
        """
        if len(market_data_history) < 50:
            return None # Not enough data

        # Calculate Indicators
        rsi = self.indicators.calculate_rsi(market_data_history).iloc[-1]
        macd, signal = self.indicators.calculate_macd(market_data_history)
        macd = macd.iloc[-1]
        signal = signal.iloc[-1]
        upper, lower = self.indicators.calculate_bollinger_bands(market_data_history)
        upper = upper.iloc[-1]
        lower = lower.iloc[-1]
        atr = self.indicators.calculate_atr(market_data_history).iloc[-1]
        
        regime = self.indicators.detect_market_regime(market_data_history)

        return {
            "rsi": rsi,
            "macd": macd,
            "macd_signal": signal,
            "upper_band": upper,
            "lower_band": lower,
            "atr": atr,
            "regime": regime
        }

    def predict_action(self, market_data, analysis):
        """
        Combines RL and Math to predict action.
        Action: 0 = HOLD, 1 = CALL (Buy), 2 = PUT (Sell)
        """
        # 1. Math/Rule-based Signal
        math_score = 0
        
        # RSI Logic
        if analysis['rsi'] < 30: math_score += 1 # Oversold -> Buy
        elif analysis['rsi'] > 70: math_score -= 1 # Overbought -> Sell
        
        # MACD Logic
        if analysis['macd'] > analysis['macd_signal']: math_score += 1
        elif analysis['macd'] < analysis['macd_signal']: math_score -= 1
        
        # Bollinger Logic
        price = market_data['close']
        if price < analysis['lower_band']: math_score += 1 # Bounce up
        elif price > analysis['upper_band']: math_score -= 1 # Bounce down

        # 2. RL Model Prediction
        rl_action = 0
        if self.model:
            # Create observation vector (simplified for this example)
            obs = np.array([
                analysis['rsi'], analysis['macd'], analysis['atr'], 
                market_data['close'], analysis['regime']
            ])
            rl_action, _ = self.model.predict(obs)
        
        # 3. Ensemble Decision
        # If RL and Math agree, strong signal. If not, weigh them.
        # For now, let's prioritize Math for safety if RL is untrained.
        
        final_action = "HOLD"
        
        # Map RL action (assuming discrete: 0=Hold, 1=Buy, 2=Sell)
        rl_vote = 0
        if rl_action == 1: rl_vote = 1
        elif rl_action == 2: rl_vote = -1
        
        # Combine
        total_score = math_score + rl_vote
        
        if total_score >= 2:
            final_action = "CALL"
        elif total_score <= -2:
            final_action = "PUT"
            
        return final_action

    def execute_step(self, market_data_history, current_price):
        """
        Main execution step called by the app.
        """
        # Prepare single row data
        current_data = {
            'close': current_price,
            'high': current_price, # Approximation for real-time tick
            'low': current_price,
            'open': current_price,
            'volume': 0
        }
        
        # Append to history for analysis
        # Note: In a real app, history should be maintained more robustly
        market_data_history = pd.concat([market_data_history, pd.DataFrame([current_data])], ignore_index=True)
        
        analysis = self.analyze_market(market_data_history)
        
        if not analysis:
            return "WAIT", {}, 0
            
        action = self.predict_action(current_data, analysis)
        
        return action, analysis, current_price

    def log_result(self, market_data, analysis, action, reward, pnl):
        self.data_manager.log_step(market_data, analysis, action, reward, pnl)

    def evolve(self):
        """
        Retrains the model using accumulated data.
        """
        data = self.data_manager.load_data()
        if len(data) < 100:
            return "Not enough data to evolve."
            
        # Créer l'environnement de trading avec les données de data.csv
        env = TradingEnv(df=data, window_size=50)
        
        # Initialiser le modèle PPO avec l'environnement personnalisé
        model = PPO(
            policy="MlpPolicy",
            env=env,
            verbose=1, # Activer les logs d'entraînement
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64
        )
        
        # Entraîner le modèle sur les données historiques
        print("Début de l'entraînement du modèle PPO avec les données de data.csv...")
        model.learn(total_timesteps=10000)
        
        # Sauvegarder le modèle entraîné
        model.save("super_trader_ppo")
        print("Modèle entraîné et sauvegardé sous 'super_trader_ppo.zip'")
        
        # Mettre à jour l'instance du modèle dans l'agent
        self.model = PPO.load("super_trader_ppo")
        
        # Effacer les données d'historique après que le modèle a évolué
        self.data_manager.clear_data()
        
        return "Evolution complète (Entraînement réel avec data.csv terminé, données nettoyées)"
