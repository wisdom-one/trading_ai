# Super Trader AI - Pocket Option

"Intelligence Artificielle Hybride (Math/RL) pour le Trading Automatisé de Pocket Option"

## Description

Super Trader AI est une application de trading avancée qui combine des modèles mathématiques et de l'apprentissage par renforcement (RL) pour prendre des décisions de trading automatisées. L'application utilise l'API Polygon.io pour obtenir des données de marché en temps réel et simule des opérations de trading basées sur des indicateurs techniques et des modèles d'apprentissage automatique.

## ✨ Fonctionnalités Principales

### 🔍 Analyse Technique Intégrée
- **RSI (Relative Strength Index)** - Détection de conditions de surachat/survente
- **MACD (Moving Average Convergence Divergence)** - Analyse de la convergence/divergence des moyennes mobiles
- **Bandes de Bollinger** - Identification des niveaux de support et de résistance
- **ATR (Average True Range)** - Mesure de la volatilité du marché
- **Détection du Régime de Marché** - Identification des tendances haussières/baissières

### 🤖 Apprentissage par Renforcement
- Modèle PPO (Proximal Policy Optimization) pour la prise de décision
- Apprentissage et évolution continus basés sur les performances historiques
- Système d'ensemble combinant signaux mathématiques et prédictions IA

### 📊 Interface Streamlit
- Tableau de bord en temps réel avec métriques et graphiques
- Interface de configuration côté
- Journal d'opérations exhaustif
- Visualisation des données avec mises à jour en temps réel

### 🔒 Gestion du Risque
- **Stop Loss** - Limite automatique des pertes
- **Take Profit** - Verrouillage des profits à des objectifs prédéfinis
- **Simulation avant opérations réelles** - Tester les stratégies sans risque
- **Rechargement automatique des données** - Gestion transparente des données historiques

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.8+
- Clé API Polygon.io (obtenez-en une sur [polygon.io](https://polygon.io/))

### Installation

1. Clonez le dépôt :
```bash
git clone <repository-url>
cd super_trader_ai
```

2. Créez et activez un environnement virtuel :
```bash
python -m venv .env
source .env/Scripts/activate  # Sur Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurez votre clé API :
```bash
cp .env.example .env_data
# Modifiez .env_data et ajoutez votre clé API Polygone
```

### Configuration

Le projet utilise un fichier `.env_data` pour gérer les clés API en toute sécurité. Le format attendu est :

```
POLYGON_API_KEY="your_polygon_api_key_here"
```

**⚠️ Sécurité :** Ne commettez jamais le fichier `.env_data` - il est inclus dans `.gitignore` par défaut.

### Lancement de l'Application

Exécutez l'application Streamlit :

```bash
streamlit run app.py
```

## 📁 Structure du Projet

```
super_trader_ai/
├── app.py                      # Application Streamlit principale
├── requirements.txt            # Dépendances Python
├── .env_data                   # Fichier de clés API (non suivi par Git)
├── .env.example               # Exemple de configuration
├── .gitignore                 # Fichiers à ignorer par Git
├── api_client.py              # Client API Polygon.io
├── config/                    # Configuration de l'application
│   ├── constants.py           # Constantes et paramètres
│   ├── settings.py            # Paramètres de configuration
│   └── styles.py              # Styles CSS Streamlit
├── utils/                     # Librairies utilitaires
│   ├── data_buffer.py         # Gestionnaire de tampons de données
│   ├── system_wrapper.py      # Wrapper du système de trading
│   └── trading_utils.py       # Fonctions utilitaires de trading
└── super_trader/              # Cœur du système IA
    ├── agent.py               # Agent de trading principal
    ├── indicators.py          # Calculs des indicateurs techniques
    ├── trading_env.py         # Environnement RL
    └── data_manager.py        # Gestion des données
```

## 🔧 Composants Principaux

### `api_client.py`
- Client pour les données d'agrégation Polygon.io
- Gestion complète d'erreurs et validation d'entrée
- Validation et nettoyage des tickers

### `super_trader/agent.py`
Intègre l'analyse technique et l'apprentissage par renforcement :  
- Chargement/création de modèles PPO  
- Calculs des indicateurs techniques  
- Prédiction d'actions basée sur l'ensemble  
- Évolution continue  

### `utils/system_wrapper.py`
Gère l'état du trading et la coordination :  
- Gestion du mode de données (historique/simulation)  
- Chargement automatique des données  
- Surveillance de la gestion du risque  
- Journalisation et suivi des positions  

### `utils/data_buffer.py`
System manager :  
- Tampons de données dynamiques  
- Position de lecture automatique  
- Gestion basculante des tampons  

## 🎯 Utilisation

### Mode Simulation
- **Par défaut quand aucune clé API n'est disponible**
- Génère des données de marché simulées
- Parfait pour le test et le développement

### Mode Données Historiques
- **Utilise des données du marché réel via Polygon.io**
- Configurez une clé API valide dans `.env_data`
- Recharge automatiquement les données quand les tampons sont épuisés

### Configuration des Positions  
- Affectez les paramètres de trading dans la barre latérale :
  - Montant par trade (par défaut: 1,00$)
  - Limite Stop Loss (par défaut: 50,00$)
  - Limite Take Profit (par défaut: 100$)
- Activez/Désactivez l'évolution automatique
- Définissez des limites de temps de trading

### Sélection des Tickers  
Choisir parmi des catégories prédéfinies ou entrer manuellement :  
- **Actions** : AAPL, GOOGL, MSFT, etc.
- **Devises** : C:EURUSD, C:GBPUSD, etc.  
- **Crypto** : X:BTCUSD, X:ETHUSD, etc.  

## 🧪 Apprentissage par Renforcement  

L'agent utilise l'apprentissage par renforcement fondé sur l'ensemble :  

### Architecture du Modèle  
- **Modèle** : Proximal Policy Optimization (PPO)
- **Politique** : MlpPolicy
- **Observation Space** : [RSI, MACD, ATR, Prix, Régime]
- **Space d'Action** : HOLD(0), BUY(1), SELL(2)

### Processus d'Évolution  
1. Les données historiques sont collectées dans `data.csv`
2. L'agent évolue quand suffisamment de données (>100 lignes)
3. Le modèle PPO est entraîné sur les données
4. Le modèle entraîné est sauvegardé comme `super_trader_ppo.zip`

## 📈 Indicateurs Techniques  

### Indicateurs Implémentés
- **RSI** : Surachat (>70) vs Survente (<30)
- **MACD** : Points d'achat/vente via croisements de ligne
- **Bandes de Bollinger** : Breakouts au-delà des moyennes mobiles ±2σ
- **ATR** : Mesure de la volatilité pour les stops
- **Régime** : Tendance basée sur le prix vs SMA50

### Logique des Signaux
L'agent combine les scores mathématiques :
- +1 en survente RSI
- +1 pour MACD au-dessus du signal
- +1 si prix sous la bande inférieure
L'apprentissage par renforcement ajoute une autre couche de signal

## 🔒 Gestion de la Sécurité

### Bonnes Pratiques de Sécurité Implémentées
1. **Gestion des Secrets**
   - Chargement sécurisé des clés à partir de fichiers .env dédiés
   - Encodage UTF-8 et nettoyage des caractères pour les secrets
   - Exclusion des fichiers à clés secrètes des commits git

2. **Validation de l'Entrée**
   - Validation du format des tickers
   - Validation de la clé API
   - Nettoyage des données de marché

3. **Gestion d'Erreur**
   - Gestion complète d'erreur API (401, 403, 500, etc.)
   - Gestion des timeouts et erreurs de connexion
   - Retours d'erreur propres sans exposition de détails internes

## ⚙️ Dépendances

| Package | Version | Objectif |
|---------|---------|----------|
| streamlit | >=1.28.0 | Framework d'interface |
| stable-baselines3 | >=2.0.0 | Apprentissage par renforcement |
| shimmy | >=0.2.1 | Environnements Gym |
| pandas | >=2.0.0 | Manipulation de données |
| numpy | >=1.24.0 | Calculs numériques |
| gymnasium | >=0.29.0 | Environnements RL |
| requests | >=2.31.0 | Client HTTP |

## 🐛 Dépannage

### Problèmes Courants

1. **"Clé API manquante"**
   - Copiez `.env.example` vers `.env_data`
   - Ajoutez une clé API Polygon.io valide

2. **"Pas assez de données historiques"**
   - Le marché doit avoir 50+ jours de données
   - Essayez un ticker différent

3. **"Erreur d'évolution"**
   - Assurez-vous d'avoir assez de données historiques (100+ lignes dans data.csv)

4. **Problèmes limites de mémoire**
   - Réduisez MAX_SIMULATION_LOOPS dans config/constants.py
   - Augmentez les intervalles d'effacement du journal

## 🤝 Contribution

Comment contribuer :

1. Forkez le dépôt
2. Créez une branche feature (`git checkout -b feature/NouvelleFonction`)
3. Committez vos changements (`git commit -am 'Ajout d'une nouvelle fonction'`)
4. Pushez vers la branche (`git push origin feature/NouvelleFonction`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- [Polygon.io](https://polygon.io/) pour fournir des données de marché
- [Stable Baselines3](https://stable-baselines3.readthedocs.io/) pour les frameworks d'apprentissage par renforcement
- [Streamlit](https://streamlit.io/) pour la création d'interfaces web

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub ou contacter l'équipe de développement.

---

**⚠️ Avertissement de Trading** : Ce logiciel est à titre éducatif. Le trading réel comporte un risque de perte. Utilisez toujours un nouvel argent pour les simulations avant les investissements réels.
