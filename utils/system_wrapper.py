"""
Wrapper système de trading principal pour Super Trader AI.

Ce module coordonne l'état global du système (mode de données, boucle temporelle),
exécute l'agent de trading à chaque tick, surveille la gestion du risque,
et orchestre l'accès aux tampons de données historiques Polygon.io.
Il respecte les principes SOLID en séparant la gestion d'interface de la coordination système.
"""

import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, Any
from super_trader.agent import SuperTrader
from utils.data_buffer import DataBufferManager


class SystemWrapper:
    """
    Gestionnaire central du cycle de vie du système de trading.
    
    Coordonne l'agent, le buffer manager de données historiques,
    le calcul des indicateurs en temps réel, le calcul du PnL et la gestion du risque.
    """

    def __init__(self):
        """Initialise le wrapper système avec un agent SuperTrader et des configurations par défaut."""
        self.agent = SuperTrader()
        self.is_running = False
        self.logs: list = []
        self.start_time: Optional[float] = None

        # Paramètres de capital et de risque
        self.trade_amount = 1.0
        self.stop_loss_limit = 50.0
        self.take_profit_limit = 100.0
        self.daily_pnl = 0.0
        self.max_pnl = 0.0
        self.min_pnl = 0.0
        self.auto_evolve = True

        # Historique de marché local
        self.market_history = pd.DataFrame(
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )

        # Mode de données (SIMULATION ou HISTORICAL)
        self.data_mode = 'SIMULATION'
        self.data_buffer_manager = DataBufferManager()
        self.initial_candles = 50

        # Configuration de rechargement automatique
        self.current_ticker: str = "AAPL"
        self.current_api_key: str = ""
        self.auto_reload_threshold = 10

        # Initialiser avec des données de simulation initiales
        self._init_dummy_data()

    def _init_dummy_data(self) -> None:
        """Génère un historique initial de données de marché simulées (60 bougies)."""
        rows = []
        current_time = datetime.now()
        for i in range(60):
            price = 100.0 + np.random.uniform(-1.0, 1.0)
            ts = current_time - timedelta(minutes=60 - i)
            rows.append({
                'timestamp': ts,
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': 1000.0
            })
        self.market_history = pd.DataFrame(rows)

    def load_api_data(self, api_key: str, ticker: str, append: bool = False) -> Tuple[bool, str]:
        """
        Charge des données historiques depuis l'API Polygon.io et crée un nouveau buffer.

        Args:
            api_key: Clé API Polygon.io.
            ticker: Symbole financier (ex: AAPL, X:BTCUSD).
            append: Si True, charge les données suivant la date du dernier buffer existant.

        Returns:
            Tuple[bool, str]: (Succès du chargement, Message de statut)
        """
        from api_client import PolygonClient

        self.log(f"🌍 Chargement des données historiques pour {ticker}...")

        # Enregistrer les métadonnées pour d'éventuels auto-reloads
        self.current_ticker = ticker
        self.current_api_key = api_key

        client = PolygonClient(api_key)
        
        # Détermination de la date de début pour éviter le chevauchement
        kwargs: Dict[str, Any] = {"limit": 5000}
        if append:
            latest_idx = len(self.data_buffer_manager.buffers) - 1
            latest_buffer = self.data_buffer_manager.buffers.get(
                f"{self.data_buffer_manager.buffer_prefix}_{latest_idx}"
            )
            if latest_buffer is not None and not latest_buffer.empty:
                last_ts = latest_buffer['timestamp'].max()
                kwargs['from_date'] = (last_ts + timedelta(days=1)).strftime('%Y-%m-%d')

        success, df, error_msg = client.get_aggregates(ticker, **kwargs)

        if not success:
            self.log(f"❌ {error_msg}")
            self.data_buffer_manager.mark_load_failed()
            return False, error_msg

        if len(df) < 50:
            msg = "⚠️ Pas assez de données historiques (>50 bougies requises)."
            self.log(msg)
            self.data_buffer_manager.mark_load_failed()
            return False, msg

        # Créer le buffer avec les données chargées
        buffer_name = self.data_buffer_manager.confirm_load_success(df)

        # Initialiser le market_history s'il s'agit du tout premier buffer chargé
        if self.data_buffer_manager.current_buffer_index == 0:
            self.data_mode = 'HISTORICAL'
            self.market_history = df.iloc[:self.initial_candles].copy()
            self.data_buffer_manager.current_position = self.initial_candles
            self.log(f"✅ Buffer '{buffer_name}' créé : {len(df)} bougies. Début à la position {self.initial_candles}.")
        else:
            self.log(f"🔄 Buffer '{buffer_name}' créé : {len(df)} nouvelles bougies ajoutées.")

        stats = self.data_buffer_manager.get_buffer_stats()
        self.log(f"📊 Total buffers : {stats['total_buffers']} | Buffer actuel : {stats['current_buffer_name']}")

        return True, f"Mode Historique activé sur {ticker}"

    def get_remaining_data_count(self) -> int:
        """
        Obtient le nombre de bougies restantes dans le buffer actuel.

        Returns:
            int: Nombre de bougies restantes.
        """
        return self.data_buffer_manager.get_remaining_data()

    def should_auto_reload(self) -> bool:
        """
        Vérifie si le chargement automatique de données supplémentaires doit être déclenché.

        Returns:
            bool: True si la limite de bougies restantes est franchie.
        """
        if self.data_mode != 'HISTORICAL':
            return False
        if not self.current_api_key:
            return False
        return self.data_buffer_manager.should_load_new_data(self.auto_reload_threshold)

    def auto_reload_data(self) -> bool:
        """
        Déclenche de manière asynchrone ou séquentielle le chargement de données via l'API.

        Returns:
            bool: True si le chargement a réussi.
        """
        if not self.should_auto_reload():
            return False

        self.data_buffer_manager.mark_load_pending()
        self.log(f"🔄 Auto-reload : seulement {self.get_remaining_data_count()} bougies restantes...")

        success, _ = self.load_api_data(self.current_api_key, self.current_ticker, append=True)
        return success

    def log(self, message: str) -> None:
        """
        Ajoute une entrée horodatée dans le journal des opérations.

        Args:
            message: Message textuel à enregistrer.
        """
        from config.constants import LOG_ENTRIES_LIMIT
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.insert(0, f"[{timestamp}] {message}")
        if len(self.logs) > LOG_ENTRIES_LIMIT:
            self.logs.pop()

    def run_cycle(self) -> Optional[Dict[str, float]]:
        """
        Exécute un cycle complet de trading (tick système).
        
        Cette fonction charge la nouvelle bougie (historique ou simulée),
        demande la prédiction de l'agent, met à jour le portefeuille et logue les résultats.

        Returns:
            Optional[Dict[str, float]]: Les indicateurs techniques de l'étape courante ou None.
        """
        from config.constants import EVOLUTION_PROBABILITY
        from utils.trading_utils import setup_market_data, process_trading_action

        # Récupérer le point de données historique si applicable
        data_point = None
        if self.data_mode == 'HISTORICAL' and self.data_buffer_manager.has_data():
            data_point = self.data_buffer_manager.get_current_data_point()

            if data_point is None:
                # Si le buffer actuel est épuisé, basculer au suivant
                if self.data_buffer_manager.advance_to_next_buffer():
                    stats = self.data_buffer_manager.get_buffer_stats()
                    self.log(f"🔄 Basculement vers le buffer '{stats['current_buffer_name']}'")
                    data_point = self.data_buffer_manager.get_current_data_point()
                    if data_point is None:
                        self.is_running = False
                        self.log("⏹️ Fin des données historiques (buffer vide).")
                        return None
                else:
                    self.is_running = False
                    self.log("⏹️ Fin des données historiques disponibles.")
                    return None

        # Configuration des données via trading_utils
        new_row = setup_market_data(self, data_point)
        current_price = float(new_row['close'])

        # Exécuter l'analyse et la prédiction de l'agent
        action, analysis, price = self.agent.execute_step(self.market_history, current_price)

        # Mettre à jour l'historique local pour le calcul glissant
        self.market_history = pd.concat(
            [self.market_history, pd.DataFrame([new_row])],
            ignore_index=True
        )
        if len(self.market_history) > 200:
            self.market_history = self.market_history.iloc[-200:]

        # Traiter les transactions à l'aide de trading_utils
        if action not in ["WAIT", "HOLD"]:
            profit = process_trading_action(self, action, price)
            self.daily_pnl += profit
            self.max_pnl = max(self.max_pnl, self.daily_pnl)
            self.min_pnl = min(self.min_pnl, self.daily_pnl)
            
            is_win = profit > 0.0
            self.agent.log_result(new_row, analysis, action, 1.0 if is_win else -1.0, self.daily_pnl)

        # Surveiller la journalisation d'erreurs asynchrones de l'évolution de l'IA
        if self.agent.evolution_error:
            self.log(f"❌ Erreur d'évolution de l'IA : {self.agent.evolution_error}")
            self.agent.evolution_error = None

        # Évolution automatique déclenchée de manière aléatoire (1% de chances)
        if self.auto_evolve and not self.agent.is_evolving and np.random.random() < EVOLUTION_PROBABILITY:
            msg = self.agent.evolve()
            self.log(f"🧬 {msg}")

        return analysis if analysis else None

