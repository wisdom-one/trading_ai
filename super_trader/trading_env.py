import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional
from .indicators import Indicators

class TradingEnv(gym.Env):
    """
    Environnement Gym personnalisé pour simuler le trading d'actifs financiers.
    
    Suit les spécifications de Gymnasium. Cet environnement est utilisé par l'agent RL
    pour s'entraîner (modèle PPO de Stable-Baselines3).
    """
    
    metadata = {'render_modes': ['human'], 'render_fps': 30}

    def __init__(self, df: pd.DataFrame, window_size: int = 50):
        """
        Initialise l'environnement de trading avec des données historiques.
        
        Args:
            df: DataFrame contenant les colonnes 'open', 'high', 'low', 'close', 'volume'.
            window_size: Taille minimale de l'historique requis pour le calcul des indicateurs (défaut: 50).
        """
        super().__init__()
        self.df = df.copy()  # Utiliser une copie pour éviter de modifier le DataFrame original
        self.window_size = window_size
        self.current_step = window_size

        # Calculer les indicateurs techniques sur l'ensemble du DataFrame
        self.indicators_calculator = Indicators()
        self.df['rsi'] = self.indicators_calculator.calculate_rsi(self.df)
        
        macd, signal = self.indicators_calculator.calculate_macd(self.df)
        self.df['macd'] = macd
        self.df['macd_signal'] = signal
        
        upper_band, lower_band = self.indicators_calculator.calculate_bollinger_bands(self.df)
        self.df['upper_band'] = upper_band
        self.df['lower_band'] = lower_band
        self.df['atr'] = self.indicators_calculator.calculate_atr(self.df)
        
        # Correction du bug de fuite de données : calcul vectorisé sur toute la série
        self.df['regime'] = self.indicators_calculator.calculate_market_regime_series(self.df)

        # Nettoyer les lignes NaN issues du calcul des indicateurs
        self.df.dropna(inplace=True)
        self.df.reset_index(drop=True, inplace=True)

        # Espace d'actions : 0 = HOLD, 1 = BUY, 2 = SELL
        self.action_space = spaces.Discrete(3)

        # Espace d'observations : [RSI, MACD, ATR, Close, Regime]
        self.n_features = 5
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf,
            shape=(self.n_features,),
            dtype=np.float32
        )

        # Paramètres financiers du portefeuille simulé
        self.initial_balance = 10000.0
        self.balance = self.initial_balance
        self.shares = 0.0
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance

    def _get_obs(self) -> np.ndarray:
        """
        Génère l'observation pour l'étape actuelle.
        
        Returns:
            np.ndarray: Vecteur d'observation [rsi, macd, atr, close, regime]
        """
        current_row = self.df.iloc[self.current_step]
        obs = np.array([
            current_row['rsi'],
            current_row['macd'],
            current_row['atr'],
            current_row['close'],
            current_row['regime']
        ], dtype=np.float32)
        return obs

    def _get_info(self) -> Dict[str, Any]:
        """
        Retourne des informations supplémentaires sur l'état du portefeuille.
        
        Returns:
            Dict: Dictionnaire contenant la balance, les actions détenues et la valeur nette.
        """
        return {
            "balance": self.balance,
            "shares": self.shares,
            "net_worth": self.net_worth,
        }

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Réinitialise l'environnement pour un nouvel épisode.
        
        Args:
            seed: Graine aléatoire optionnelle.
            options: Options de réinitialisation.
            
        Returns:
            Tuple: (première observation, informations additionnelles)
        """
        super().reset(seed=seed)
        self.balance = self.initial_balance
        self.shares = 0.0
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance
        self.current_step = self.window_size

        observation = self._get_obs()
        info = self._get_info()
        return observation, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Exécute un pas d'action dans l'environnement.
        
        Args:
            action: Action sélectionnée (0=HOLD, 1=BUY, 2=SELL).
            
        Returns:
            Tuple: (observation suivante, récompense, terminé, tronqué, info)
        """
        self.current_step += 1

        if self.current_step > len(self.df) - 1:
            self.current_step = self.window_size  # Réinitialiser si nécessaire
            terminated = True
            truncated = False
            reward = 0.0
            observation = self._get_obs()
            info = self._get_info()
            return observation, reward, terminated, truncated, info

        current_price = float(self.df['close'].values[self.current_step])
        previous_net_worth = self.net_worth

        # Exécuter l'action demandée
        if action == 1:  # BUY
            if self.balance >= current_price:
                self.shares += 1.0
                self.balance -= current_price
        elif action == 2:  # SELL
            if self.shares > 0:
                self.shares -= 1.0
                self.balance += current_price

        # Mettre à jour la valeur nette du portefeuille
        self.net_worth = self.balance + (self.shares * current_price)

        # Récompense : variation de la valeur nette du portefeuille
        reward = float(self.net_worth - previous_net_worth)

        terminated = False
        truncated = False

        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, terminated, truncated, info

    def render(self) -> None:
        """Rendu de l'environnement (non implémenté)."""
        pass

    def close(self) -> None:
        """Nettoyage lors de la fermeture de l'environnement."""
        pass

