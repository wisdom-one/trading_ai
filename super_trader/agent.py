import numpy as np
import pandas as pd
from stable_baselines3 import PPO
import os
import threading
from typing import Tuple, Dict, Any, Optional
from .indicators import Indicators
from .data_manager import DataManager
from .trading_env import TradingEnv

class SuperTrader:
    """
    Agent de trading hybride combinant signaux mathématiques et apprentissage par renforcement.
    
    Cette classe orchestre l'analyse technique du marché, effectue des prédictions d'actions,
    et gère l'entraînement/évolution continue du modèle d'apprentissage par renforcement (PPO).
    
    Suit les principes SOLID en déléguant les calculs mathématiques à Indicators et
    le stockage à DataManager, tout en encapsulant le modèle RL.
    """
    
    def __init__(self):
        """Initialise l'agent SuperTrader avec ses indicateurs, son gestionnaire de données et son modèle."""
        self.indicators = Indicators()
        self.data_manager = DataManager()
        self.model: Optional[PPO] = None
        self.is_learning = True
        self.trade_history = []
        
        # Attributs pour l'évolution asynchrone (non bloquante)
        self.is_evolving = False
        self.evolution_error: Optional[str] = None
        
        # Chargement ou création du modèle initial
        self.load_model()

    def load_model(self) -> None:
        """Charge le modèle PPO entraîné depuis le disque s'il existe."""
        if os.path.exists("super_trader_ppo.zip"):
            try:
                self.model = PPO.load("super_trader_ppo")
                print("Modèle PPO chargé avec succès depuis super_trader_ppo.zip")
            except Exception as e:
                print(f"Erreur lors du chargement du modèle existant : {e}")
                self.model = None
        else:
            self.model = None
            print("Aucun modèle existant trouvé. Le modèle sera initialisé lors de la première évolution.") 

    def analyze_market(self, market_data_history: pd.DataFrame) -> Optional[Dict[str, float]]:
        """
        Analyse les données du marché en calculant les indicateurs techniques clés.
        
        Optimisation : La série historique est tronquée aux 100 dernières bougies avant le calcul
        pour éviter une baisse de performance linéaire lorsque l'historique grandit.
        
        Args:
            market_data_history: DataFrame contenant les colonnes 'close', 'high', 'low'.
            
        Returns:
            Dict: Dictionnaire contenant les indicateurs techniques calculés, ou None s'il y a moins de 50 bougies.
        """
        if len(market_data_history) < 50:
            return None  # Pas assez de données pour les calculs (SMA50 requiert au moins 50 points)

        # Optimisation CPU : Calculer sur une tranche glissante maximale de 100 points
        df_slice = market_data_history.iloc[-100:].copy()

        # Calculer les indicateurs techniques sur la tranche optimisée
        rsi_series = self.indicators.calculate_rsi(df_slice)
        rsi = rsi_series.iloc[-1]
        
        macd_series, signal_series = self.indicators.calculate_macd(df_slice)
        macd = macd_series.iloc[-1]
        signal = signal_series.iloc[-1]
        
        upper_series, lower_series = self.indicators.calculate_bollinger_bands(df_slice)
        upper = upper_series.iloc[-1]
        lower = lower_series.iloc[-1]
        
        atr_series = self.indicators.calculate_atr(df_slice)
        atr = atr_series.iloc[-1]
        
        regime = self.indicators.detect_market_regime(df_slice)

        return {
            "rsi": float(rsi),
            "macd": float(macd),
            "macd_signal": float(signal),
            "upper_band": float(upper),
            "lower_band": float(lower),
            "atr": float(atr),
            "regime": regime
        }

    def predict_action(self, market_data: Dict[str, Any], analysis: Dict[str, float]) -> str:
        """
        Combine l'analyse mathématique traditionnelle et les prédictions du modèle RL.
        
        Args:
            market_data: Données de prix de l'étape courante.
            analysis: Indicateurs techniques calculés à l'étape courante.
            
        Returns:
            str: Action choisie par l'ensemble ("HOLD", "CALL" [Achat], "PUT" [Vente]).
        """
        # 1. Score basé sur les règles mathématiques (Modèle Quantitatif)
        math_score = 0
        
        # Logique RSI (Surachat/Survente)
        if analysis['rsi'] < 30.0: 
            math_score += 1  # Survente -> Achat potentiel
        elif analysis['rsi'] > 70.0: 
            math_score -= 1  # Surachat -> Vente potentielle
        
        # Logique MACD (Croisement de lignes)
        if analysis['macd'] > analysis['macd_signal']: 
            math_score += 1
        elif analysis['macd'] < analysis['macd_signal']: 
            math_score -= 1
        
        # Logique Bandes de Bollinger (Rebonds sur les bornes)
        price = float(market_data['close'])
        if price < analysis['lower_band']: 
            math_score += 1  # Prix sous la bande inférieure -> Achat
        elif price > analysis['upper_band']: 
            math_score -= 1  # Prix au-dessus de la bande supérieure -> Vente

        # 2. Prédiction du modèle d'Apprentissage par Renforcement (RL)
        rl_action = 0
        # Utiliser un verrou local implicite via assignation atomique
        local_model = self.model
        if local_model is not None:
            # Vecteur d'observation conforme à l'espace défini dans l'environnement Gym
            obs = np.array([
                analysis['rsi'], 
                analysis['macd'], 
                analysis['atr'], 
                price, 
                float(analysis['regime'])
            ], dtype=np.float32)
            try:
                rl_action, _ = local_model.predict(obs)
            except Exception as e:
                print(f"Erreur de prédiction RL : {e}")
                rl_action = 0  # HOLD par défaut en cas d'erreur
        
        # 3. Décision d'Ensemble
        rl_vote = 0
        if rl_action == 1: 
            rl_vote = 1    # BUY
        elif rl_action == 2: 
            rl_vote = -1   # SELL
        
        total_score = math_score + rl_vote
        
        final_action = "HOLD"
        if total_score >= 2:
            final_action = "CALL"
        elif total_score <= -2:
            final_action = "PUT"
            
        return final_action

    def execute_step(self, market_data_history: pd.DataFrame, current_price: float) -> Tuple[str, Dict[str, float], float]:
        """
        Point d'entrée exécuté à chaque tick système par le wrapper de trading.
        
        Args:
            market_data_history: Historique cumulé des bougies.
            current_price: Dernier cours connu (dernier tick).
            
        Returns:
            Tuple: (Action prédite, Indicateurs techniques calculés, Prix actuel)
        """
        current_data = {
            'close': current_price,
            'high': current_price,
            'low': current_price,
            'open': current_price,
            'volume': 0.0
        }
        
        # Simulation d'ajout de bougie temps réel
        history_with_tick = pd.concat([market_data_history, pd.DataFrame([current_data])], ignore_index=True)
        
        analysis = self.analyze_market(history_with_tick)
        
        if not analysis:
            return "WAIT", {}, current_price
            
        action = self.predict_action(current_data, analysis)
        
        return action, analysis, current_price

    def log_result(self, market_data: Dict[str, Any], analysis: Dict[str, float], action: str, reward: float, pnl: float) -> None:
        """Enregistre le résultat de l'étape pour le réentraînement ultérieur."""
        self.data_manager.log_step(market_data, analysis, action, reward, pnl)

    def evolve(self) -> str:
        """
        Démarre le processus de réentraînement du modèle RL dans un thread séparé.
        Permet à l'application Streamlit principale de continuer à fonctionner de manière réactive.
        
        Returns:
            str: Statut de l'évolution démarrée ou erreur.
        """
        if self.is_evolving:
            return "Évolution de l'IA déjà en cours..."

        data = self.data_manager.load_data()
        if len(data) < 100:
            return f"Données insuffisantes pour évoluer ({len(data)}/100 requises)."
            
        self.is_evolving = True
        self.evolution_error = None
        
        # Démarrage de l'entraînement dans un thread d'arrière-plan pour ne pas bloquer l'UI
        thread = threading.Thread(target=self._run_evolution, args=(data,))
        thread.daemon = True
        thread.start()
        
        return "Évolution de l'IA démarrée en arrière-plan (entraînement PPO actif)."

    def _run_evolution(self, data: pd.DataFrame) -> None:
        """
        Fonction interne exécutée dans le thread secondaire pour entraîner le modèle.
        
        Args:
            data: DataFrame contenant les données historiques de trading.
        """
        try:
            print("Arrière-plan : Début de l'entraînement PPO sur les données accumulées...")
            env = TradingEnv(df=data, window_size=50)
            
            model = PPO(
                policy="MlpPolicy",
                env=env,
                verbose=0,  # Désactiver verbose pour éviter de polluer la sortie standard
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=64
            )
            
            # Entraînement sur 10 000 pas
            model.learn(total_timesteps=10000)
            
            # Sauvegarde physique
            model.save("super_trader_ppo")
            print("Arrière-plan : Modèle entraîné et sauvegardé sous 'super_trader_ppo.zip'")
            
            # Assignation atomique de la nouvelle instance chargée
            self.model = PPO.load("super_trader_ppo")
            
            # Nettoyage des fichiers locaux pour le prochain cycle
            self.data_manager.clear_data()
            print("Arrière-plan : Données de data.csv réinitialisées.")
            
        except Exception as e:
            self.evolution_error = str(e)
            print(f"Arrière-plan : Échec de l'évolution du modèle : {e}")
        finally:
            self.is_evolving = False

