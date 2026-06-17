import pandas as pd
import os
import csv
from datetime import datetime
from typing import Dict, Any

class DataManager:
    """
    Gestionnaire des données locales d'historique de trading.
    
    Cette classe gère le stockage sur disque des données de marché combinées aux
    signaux d'indicateurs, actions de l'agent et résultats de PnL dans un fichier CSV.
    Ces données sont accumulées puis chargées pour le réentraînement du modèle RL (PPO).
    
    Suit le principe de Responsabilité Unique (Single Responsibility Principle) en
    isolant tout ce qui concerne le cycle de vie du fichier de données d'entraînement.
    """

    def __init__(self, filename: str = "data.csv"):
        """
        Initialise le gestionnaire de données et crée le fichier s'il n'existe pas.
        
        Args:
            filename: Nom du fichier de données (défaut: "data.csv").
        """
        self.filename = filename
        self.columns = [
            "timestamp", "open", "high", "low", "close", "volume",
            "rsi", "macd", "macd_signal", "upper_band", "lower_band", "atr",
            "action", "reward", "pnl"
        ]
        self._initialize_file()

    def _initialize_file(self) -> None:
        """
        Initialise le fichier de données avec les en-têtes de colonnes s'il n'existe pas.
        Utilise le module csv natif pour une performance d'E/S optimale.
        """
        if not os.path.exists(self.filename):
            try:
                with open(self.filename, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.columns)
            except IOError as e:
                print(f"Erreur d'initialisation du fichier {self.filename}: {e}")

    def log_step(self, market_data: Dict[str, Any], indicators: Dict[str, Any], action: str, reward: float, pnl: float) -> None:
        """
        Enregistre une étape de trading (bougie, indicateurs et action prise) dans le fichier CSV.
        
        Optimisé pour utiliser le module standard csv.DictWriter au lieu de Pandas,
        ce qui réduit drastiquement la latence d'E/S disque et l'allocation CPU/Mémoire.
        
        Args:
            market_data: Données de la bougie courante (close, high, low, etc.).
            indicators: Valeurs calculées des indicateurs techniques.
            action: Action effectuée (CALL, PUT, HOLD).
            reward: Récompense obtenue.
            pnl: Profit et perte cumulé.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Construction directe de la ligne sous forme de dictionnaire
        row = {
            "timestamp": timestamp,
            "open": market_data.get('open', 0.0),
            "high": market_data.get('high', 0.0),
            "low": market_data.get('low', 0.0),
            "close": market_data.get('close', 0.0),
            "volume": market_data.get('volume', 0.0),
            "rsi": indicators.get('rsi', 0.0),
            "macd": indicators.get('macd', 0.0),
            "macd_signal": indicators.get('macd_signal', 0.0),
            "upper_band": indicators.get('upper_band', 0.0),
            "lower_band": indicators.get('lower_band', 0.0),
            "atr": indicators.get('atr', 0.0),
            "action": action,
            "reward": reward,
            "pnl": pnl
        }
        
        try:
            with open(self.filename, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.columns)
                writer.writerow(row)
        except IOError as e:
            print(f"Impossible d'écrire l'étape de trading dans {self.filename}: {e}")

    def load_data(self) -> pd.DataFrame:
        """
        Charge l'historique complet pour l'entraînement du modèle RL.
        L'utilisation de Pandas est ici conservée car un DataFrame est requis par l'environnement Gym.
        
        Returns:
            pd.DataFrame: Les données d'entraînement chargées.
        """
        if os.path.exists(self.filename):
            try:
                # Lecture efficace en sautant la ligne d'en-tête originale
                return pd.read_csv(self.filename, names=self.columns, skiprows=1)
            except Exception as e:
                print(f"Erreur de chargement des données depuis {self.filename}: {e}")
        return pd.DataFrame(columns=self.columns)

    def clear_data(self) -> None:
        """
        Nettoie le fichier de données (ne conserve que les en-têtes) pour éviter
        l'accumulation de données d'entraînement obsolètes lors de la prochaine évolution.
        """
        try:
            with open(self.filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.columns)
        except IOError as e:
            print(f"Erreur lors du nettoyage du fichier {self.filename}: {e}")

