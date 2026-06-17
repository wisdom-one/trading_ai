import pytest
import pandas as pd
import numpy as np
import os
from super_trader.indicators import Indicators
from super_trader.data_manager import DataManager
from super_trader.trading_env import TradingEnv


def test_indicators_market_regime_series():
    """Vérifie le calcul correct de la série de régime de marché."""
    # Créer de fausses données de prix
    np.random.seed(42)
    prices = [100.0]
    for _ in range(99):
        prices.append(prices[-1] * (1.0 + np.random.uniform(-0.01, 0.01)))
        
    df = pd.DataFrame({
        'close': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'volume': [1000.0] * 100
    })
    
    regime = Indicators.calculate_market_regime_series(df, window=50)
    
    assert isinstance(regime, pd.Series)
    assert len(regime) == len(df)
    
    # Les 49 premiers éléments doivent être 0 car la fenêtre minimale est 50
    assert (regime.iloc[:49] == 0).all()
    
    # La série doit contenir des régimes variés (-1, 0, 1) sans fuite de look-ahead
    assert set(regime.unique()).issubset({-1, 0, 1})


def test_indicators_detect_market_regime():
    """Vérifie la fonction de détection du dernier régime de marché."""
    np.random.seed(42)
    prices = [100.0]
    for _ in range(99):
        prices.append(prices[-1] * (1.0 + np.random.uniform(-0.01, 0.01)))
        
    df = pd.DataFrame({
        'close': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices]
    })
    
    # Détection sur l'ensemble
    regime_val = Indicators.detect_market_regime(df, window=50)
    assert regime_val in [-1, 0, 1]
    
    # Détection sur un historique insuffisant
    regime_short = Indicators.detect_market_regime(df.iloc[:20], window=50)
    assert regime_short == 0


def test_data_manager_csv_logging(tmp_path):
    """Vérifie que le DataManager écrit et efface correctement les logs via le module csv."""
    filepath = str(tmp_path / "test_data.csv")
    
    # Initialisation
    dm = DataManager(filename=filepath)
    assert os.path.exists(filepath)
    
    # Lire et vérifier l'en-tête
    df_init = pd.read_csv(filepath)
    assert list(df_init.columns) == dm.columns
    
    # Logger une étape
    market_data = {'open': 10.0, 'high': 12.0, 'low': 9.0, 'close': 11.0, 'volume': 1500.0}
    indicators = {'rsi': 45.0, 'macd': 0.5, 'macd_signal': 0.4, 'upper_band': 13.0, 'lower_band': 8.0, 'atr': 1.5}
    dm.log_step(market_data, indicators, action="CALL", reward=1.0, pnl=0.85)
    
    # Vérifier l'enregistrement
    df_after = dm.load_data()
    assert len(df_after) == 1
    assert df_after.iloc[0]['action'] == "CALL"
    assert float(df_after.iloc[0]['close']) == 11.0
    assert float(df_after.iloc[0]['rsi']) == 45.0
    assert float(df_after.iloc[0]['reward']) == 1.0
    assert float(df_after.iloc[0]['pnl']) == 0.85
    
    # Nettoyage
    dm.clear_data()
    df_clear = dm.load_data()
    assert len(df_clear) == 0


def test_trading_env_initialization():
    """Vérifie l'initialisation et le bon fonctionnement de l'environnement de trading Gym."""
    np.random.seed(42)
    prices = [100.0]
    for _ in range(99):
        prices.append(prices[-1] * (1.0 + np.random.uniform(-0.01, 0.01)))
        
    df = pd.DataFrame({
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': [1000.0] * 100
    })
    
    env = TradingEnv(df=df, window_size=50)
    
    # Vérifier la taille et le type
    obs, info = env.reset()
    assert obs.shape == (5,)
    assert isinstance(obs, np.ndarray)
    assert info['balance'] == 10000.0
    assert info['shares'] == 0.0
    
    # Faire un pas d'action (BUY)
    next_obs, reward, terminated, truncated, info_step = env.step(1)
    assert next_obs.shape == (5,)
    assert not terminated
    assert not truncated
    assert info_step['shares'] == 1.0
