"""
Core trading system wrapper
"""

import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict
from super_trader.agent import SuperTrader
from utils.data_buffer import DataBufferManager
from config.constants import (
    DEFAULT_TRADE_AMOUNT, DEFAULT_STOP_LOSS, DEFAULT_TAKE_PROFIT,
    DEFAULT_INITIAL_CANDLES
)


class SystemWrapper:
    """
    Core trading system wrapper.
    SOLID: Single Responsibility - Manages trading state and agent execution.
    """

    def __init__(self):
        self.agent = SuperTrader()
        self.is_running = False
        self.logs: list = []
        self.start_time: Optional[float] = None

        # Configuration
        self.trade_amount = DEFAULT_TRADE_AMOUNT
        self.stop_loss_limit = DEFAULT_STOP_LOSS
        self.take_profit_limit = DEFAULT_TAKE_PROFIT
        self.daily_pnl = 0.0
        self.max_pnl = 0.0
        self.min_pnl = 0.0
        self.auto_evolve = True

        # Market Data
        self.market_history = pd.DataFrame(
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )

        # Data Mode
        self.data_mode = 'SIMULATION'
        self.data_buffer_manager = DataBufferManager()
        self.initial_candles = DEFAULT_INITIAL_CANDLES

        # Auto-reload configuration
        self.current_ticker: str = "AAPL"
        self.current_api_key: str = ""
        self.auto_reload_threshold = 10

        # Initialize with dummy data
        self._init_dummy_data()

    def _init_dummy_data(self):
        """Generate initial simulated market data."""
        rows = []
        current_time = datetime.now()
        for i in range(60):
            price = 100.0 + np.random.uniform(-1, 1)
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

    def load_api_data(self, api_key: str, ticker: str, append: bool = False) -> tuple:
        """
        Load historical data from Polygon API.

        Args:
            api_key: Polygon API key
            ticker: Ticker symbol
            append: If True, append new data to existing history

        Returns:
            tuple: (success: bool, message: str)
        """
        from api_client import PolygonClient

        self.log(f"🌍 Chargement des donnees pour {ticker}...")

        # Store for auto-reload
        self.current_ticker = ticker
        self.current_api_key = api_key

        client = PolygonClient(api_key)
        
        # Gestion de la date de départ pour éviter de boucler sur les mêmes données
        kwargs = {"limit": 5000}
        if append:
            latest_buffer = self.data_buffer_manager.buffers.get(f"{self.data_buffer_manager.buffer_prefix}_{len(self.data_buffer_manager.buffers)-1}")
            if latest_buffer is not None and not latest_buffer.empty:
                last_ts = latest_buffer['timestamp'].max()
                # On ajoute 1 jour pour demander la suite des données
                kwargs['from_date'] = (last_ts + timedelta(days=1)).strftime('%Y-%m-%d')

        success, df, error_msg = client.get_aggregates(ticker, **kwargs)

        if not success:
            self.log(f"❌ {error_msg}")
            self.data_buffer_manager.mark_load_failed()
            return False, error_msg

        if len(df) < 50:
            msg = "⚠️ Pas assez de donnees historiques (>50 requis)."
            self.log(msg)
            self.data_buffer_manager.mark_load_failed()
            return False, msg

        # Create new buffer with loaded data
        buffer_name = self.data_buffer_manager.confirm_load_success(df)

        # Initialize market_history with first candles if this is the first buffer
        if self.data_buffer_manager.current_buffer_index == 0:
            self.data_mode = 'HISTORICAL'
            self.market_history = df.iloc[:self.initial_candles].copy()
            # Set position to initial_candles so we start reading from there
            self.data_buffer_manager.current_position = self.initial_candles
            self.log(f"✅ Buffer '{buffer_name}' créé: {len(df)} bougies. Debut a la position {self.initial_candles}.")
        else:
            self.log(f"🔄 Buffer '{buffer_name}' créé: {len(df)} nouvelles bougies ajoutees.")

        stats = self.data_buffer_manager.get_buffer_stats()
        self.log(f"📊 Total buffers: {stats['total_buffers']} | Buffer actuel: {stats['current_buffer_name']}")

        return True, f"Mode Historique activé sur {ticker}"

    def get_remaining_data_count(self) -> int:
        """Get the number of remaining data points to process."""
        return self.data_buffer_manager.get_remaining_data()

    def should_auto_reload(self) -> bool:
        """Check if auto-reload should be triggered."""
        if self.data_mode != 'HISTORICAL':
            return False
        if not self.current_api_key:
            return False
        return self.data_buffer_manager.should_load_new_data(self.auto_reload_threshold)

    def auto_reload_data(self) -> bool:
        """Automatically reload data if threshold is reached."""
        if not self.should_auto_reload():
            return False

        # Mark load as pending to prevent multiple simultaneous loads
        self.data_buffer_manager.mark_load_pending()
        self.log(f"🔄 Auto-reload: seulement {self.get_remaining_data_count()} donnees restantes...")

        success, _ = self.load_api_data(self.current_api_key, self.current_ticker, append=True)
        return success

    def log(self, message: str):
        """Add a timestamped log entry."""
        from config.constants import LOG_ENTRIES_LIMIT
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.insert(0, f"[{timestamp}] {message}")
        if len(self.logs) > LOG_ENTRIES_LIMIT:
            self.logs.pop()

    def run_cycle(self) -> Optional[Dict]:
        """Execute one trading cycle. Returns analysis dict or None."""
        from config.constants import EVOLUTION_PROBABILITY

        current_price = 0.0
        new_row = None

        if self.data_mode == 'HISTORICAL' and self.data_buffer_manager.has_data():
            # Get current data point from buffer manager
            data_point = self.data_buffer_manager.get_current_data_point()

            if data_point is not None:
                # Data available in current buffer
                current_price = float(data_point['close'])
                new_row = data_point
            else:
                # Current buffer exhausted, try to advance to next buffer
                if self.data_buffer_manager.advance_to_next_buffer():
                    stats = self.data_buffer_manager.get_buffer_stats()
                    self.log(f"🔄 Basculement vers buffer '{stats['current_buffer_name']}'")
                    # Get first data point from new buffer
                    data_point = self.data_buffer_manager.get_current_data_point()
                    if data_point is not None:
                        current_price = float(data_point['close'])
                        new_row = data_point
                    else:
                        self.is_running = False
                        self.log("⏹️ Fin des donnees historiques.")
                        return None
                else:
                    # No next buffer available
                    self.is_running = False
                    self.log("⏹️ Fin des donnees historiques.")
                    return None
        else:
            # Simulation mode
            last_price = float(self.market_history.iloc[-1]['close'])
            current_price = last_price * (1 + np.random.uniform(-0.001, 0.001))
            new_row = {
                'timestamp': datetime.now(),
                'open': current_price,
                'high': current_price,
                'low': current_price,
                'close': current_price,
                'volume': 0.0
            }

        # Execute agent analysis
        action, analysis, price = self.agent.execute_step(self.market_history, current_price)

        # Update market history
        self.market_history = pd.concat(
            [self.market_history, pd.DataFrame([new_row])],
            ignore_index=True
        )
        if len(self.market_history) > 200:
            self.market_history = self.market_history.iloc[-200:]

        # Process action
        if action not in ["WAIT", "HOLD"]:
            is_win = np.random.random() > 0.45
            if is_win:
                profit = self.trade_amount * 0.85
                self.log(f"💰 WIN | {action} | Prix: {price:.2f} | PnL: +{profit:.2f}$")
            else:
                profit = -self.trade_amount
                self.log(f"🔻 LOSS | {action} | Prix: {price:.2f} | PnL: {profit:.2f}$")

            self.daily_pnl += profit
            self.max_pnl = max(self.max_pnl, self.daily_pnl)
            self.min_pnl = min(self.min_pnl, self.daily_pnl)
            self.agent.log_result(new_row, analysis, action, 1.0 if is_win else -1.0, self.daily_pnl)

        # Auto-evolution (1% chance per tick)
        if self.auto_evolve and np.random.random() < EVOLUTION_PROBABILITY:
            msg = self.agent.evolve()
            self.log(f"🧬 {msg}")

        return analysis
