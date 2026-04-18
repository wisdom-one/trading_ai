# Documentation de l'API

## SuperTrader Agent

### Méthodes

#### `analyze_market(market_data_history)`
Analyse les données du marché et retourne un dictionnaire d'indicateurs.

#### `predict_action(market_data, analysis)`
Combine les signaux mathématiques et l'apprentissage par renforcement pour prédire l'action de trading.

#### `execute_step(market_data_history, current_price)`
Exécute un cycle de trading complet.

#### `log_result(market_data, analysis, action, reward, pnl)`
Enregistre les résultats du trading dans le gestionnaire de données.

#### `evolve()`
Réentraîne le modèle d'apprentissage par renforcement avec les données historiques.

## Polygon API Client

### Méthodes

#### `get_aggregates(ticker, multiplier, timespan, from_date, to_date, limit)`
Récupère les données d'agrégation historiques au format OHLCV.

## DataBuffer Manager

### Méthodes

#### `create_new_buffer(data)`
Crée un nouveau tampon avec les données fournies.

#### `get_current_buffer()`
Retourne le tampon de données actif.

#### `get_current_data_point()`
Retourne le point de données actuel et avance la position.

#### `get_remaining_data()`
Compte les points de données restants dans le tampon actuel.

#### `should_load_new_data(threshold)`
Vérifie si de nouvelles données doivent être chargées.
