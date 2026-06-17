import numpy as np
import pandas as pd

class Indicators:
    """
    Bibliothèque d'indicateurs techniques et de modèles mathématiques pour Super Trader.
    
    Cette classe regroupe les calculs d'indicateurs financiers couramment utilisés.
    Elle suit le principe de Responsabilité Unique (Single Responsibility Principle) en
    contenant uniquement de la logique pure de calcul d'indicateurs techniques sur des
    données de marché, sans logique métier ou d'interface.
    """

    @staticmethod
    def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        Calcule le Relative Strength Index (RSI).
        
        Args:
            data: DataFrame contenant au moins la colonne 'close'.
            window: Période du RSI (défaut: 14).
            
        Returns:
            pd.Series: Les valeurs calculées du RSI.
        """
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(data: pd.DataFrame, slow: int = 26, fast: int = 12, signal: int = 9) -> tuple:
        """
        Calcule la Moving Average Convergence Divergence (MACD).
        
        Args:
            data: DataFrame contenant au moins la colonne 'close'.
            slow: Fenêtre lente (défaut: 26).
            fast: Fenêtre rapide (défaut: 12).
            signal: Fenêtre de signal (défaut: 9).
            
        Returns:
            tuple: (Série MACD, Série Ligne de Signal)
        """
        exp1 = data['close'].ewm(span=fast, adjust=False).mean()
        exp2 = data['close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line

    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> tuple:
        """
        Calcule les Bandes de Bollinger.
        
        Args:
            data: DataFrame contenant au moins la colonne 'close'.
            window: Période de la moyenne mobile (défaut: 20).
            num_std: Nombre d'écarts-types (défaut: 2).
            
        Returns:
            tuple: (Bande Supérieure, Bande Inférieure)
        """
        rolling_mean = data['close'].rolling(window=window).mean()
        rolling_std = data['close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band

    @staticmethod
    def calculate_atr(data: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        Calcule l'Average True Range (ATR) pour mesurer la volatilité.
        
        Args:
            data: DataFrame contenant au moins les colonnes 'high', 'low', 'close'.
            window: Période de l'ATR (défaut: 14).
            
        Returns:
            pd.Series: Les valeurs calculées de l'ATR.
        """
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(window=window).mean()

    @staticmethod
    def kelly_criterion(win_prob: float, win_loss_ratio: float) -> float:
        """
        Calcule la fraction de Kelly pour la gestion des tailles de positions.
        
        Formule : f* = (b * p - q) / b
        où :
        f* est la fraction du capital à engager.
        b correspond au ratio gain/perte net (win_loss_ratio).
        p est la probabilité de gain (win_prob).
        q est la probabilité de perte (1 - p).
        
        Args:
            win_prob: Probabilité estimée de gagner (entre 0 et 1).
            win_loss_ratio: Ratio de profit/perte net sur les trades gagnants.
            
        Returns:
            float: Fraction du capital conseillée (négatif ou zéro en cas de perte espérée).
        """
        if win_loss_ratio <= 0:
            return 0.0
        return (win_prob * win_loss_ratio - (1.0 - win_prob)) / win_loss_ratio

    @staticmethod
    def detect_market_regime(data: pd.DataFrame, window: int = 50) -> int:
        """
        Détecte le régime de marché actuel sur le dernier point (optimisé par tranche).
        
        Args:
            data: DataFrame contenant au moins la colonne 'close'.
            window: Fenêtre pour la moyenne mobile de tendance (défaut: 50).
            
        Returns:
            int: 1 = Haussier, -1 = Baissier, 0 = Sans tendance (volatilité trop basse).
        """
        if len(data) < window:
            return 0

        # Optimisation : On n'extrait que la fin nécessaire pour les calculs glissants locaux
        recent_close = data['close'].iloc[-window:]
        sma = recent_close.mean()
        std = recent_close.std()
        price = recent_close.iloc[-1]
        
        # Pour préserver le calcul de volatilité relative, on utilise la moyenne cumulative historique
        # pour éviter d'importer le futur
        mean_price = data['close'].mean()
        
        if mean_price == 0 or (std / mean_price) < 0.005:
            return 0
            
        return 1 if price > sma else -1

    @staticmethod
    def calculate_market_regime_series(data: pd.DataFrame, window: int = 50) -> pd.Series:
        """
        Calcule le régime de marché de manière vectorisée pour chaque ligne temporelle.
        Évite le look-ahead bias (fuite de données futures) en utilisant expanding.
        
        Args:
            data: DataFrame contenant au moins la colonne 'close'.
            window: Fenêtre de tendance SMA50 (défaut: 50).
            
        Returns:
            pd.Series: Série contenant le régime (-1, 0, 1) pour chaque pas temporel.
        """
        if len(data) < window:
            return pd.Series(0, index=data.index)
            
        close = data['close']
        sma = close.rolling(window=window).mean()
        std = close.rolling(window=window).std()
        
        # expanding() calcule la moyenne cumulative croissante pour éviter le look-ahead bias
        expanding_mean = close.expanding(min_periods=window).mean()
        volatility = std / expanding_mean
        
        # Initialisation par défaut à 0 (neutre/sideways)
        regime = pd.Series(0, index=data.index)
        
        valid_mask = ~sma.isna() & ~std.isna()
        
        # Bullish : prix > sma et volatilité >= 0.005
        bullish_mask = valid_mask & (close > sma) & (volatility >= 0.005)
        regime.loc[bullish_mask] = 1
        
        # Bearish : prix <= sma et volatilité >= 0.005
        bearish_mask = valid_mask & (close <= sma) & (volatility >= 0.005)
        regime.loc[bearish_mask] = -1
        
        return regime

