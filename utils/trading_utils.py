"""
Fonctions utilitaires de trading pour Super Trader AI.

Ce module contient des fonctions utilitaires partagées pour la configuration des données,
le traitement des résultats de transactions et la surveillance des limites de risque.
Il permet de centraliser la logique métier et de respecter le principe DRY (Don't Repeat Yourself).
"""

from datetime import datetime
import numpy as np
from typing import Dict, Tuple, Any, Optional


def setup_market_data(system_wrapper: Any, data_point: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Configure la nouvelle bougie de données de marché à partir d'un point brut ou d'une simulation.

    Args:
        system_wrapper: Instance du SystemWrapper.
        data_point: Dictionnaire optionnel contenant la bougie historique brute.

    Returns:
        Dict[str, Any]: La ligne de données formatée.
    """
    if system_wrapper.data_mode == 'HISTORICAL' and data_point is not None:
        return data_point
    
    # Mode Simulation
    last_price = float(system_wrapper.market_history.iloc[-1]['close'])
    current_price = last_price * (1.0 + np.random.uniform(-0.001, 0.001))
    return {
        'timestamp': datetime.now(),
        'open': current_price,
        'high': current_price,
        'low': current_price,
        'close': current_price,
        'volume': 0.0
    }


def process_trading_action(system_wrapper: Any, action: str, price: float) -> float:
    """
    Traite le résultat d'une transaction, journalise l'opération et retourne le profit/perte.

    Args:
        system_wrapper: Instance du SystemWrapper.
        action: Action exécutée ("CALL", "PUT").
        price: Cours auquel l'ordre a été passé.

    Returns:
        float: Le profit ou la perte net.
    """
    profit = 0.0

    if action not in ["WAIT", "HOLD"]:
        # Simulation d'un taux de réussite de 55%
        is_win = np.random.random() > 0.45
        if is_win:
            profit = float(system_wrapper.trade_amount * 0.85)
            system_wrapper.log(f"💰 WIN | {action} | Prix: {price:.2f} | PnL: +{profit:.2f}$")
        else:
            profit = float(-system_wrapper.trade_amount)
            system_wrapper.log(f"🔻 LOSS | {action} | Prix: {price:.2f} | PnL: {profit:.2f}$")

    return profit


def check_risk_limits(system_wrapper: Any) -> Tuple[bool, str]:
    """
    Vérifie si les limites de risque globales (Stop Loss ou Take Profit) ont été atteintes.

    Args:
        system_wrapper: Instance du SystemWrapper.

    Returns:
        Tuple[bool, str]: (limite_atteinte: bool, message: str)
    """
    if system_wrapper.daily_pnl <= -system_wrapper.stop_loss_limit:
        return True, "🛑 Stop Loss touché."

    if system_wrapper.daily_pnl >= system_wrapper.take_profit_limit:
        return True, "🥂 Take Profit touché."

    return False, ""

