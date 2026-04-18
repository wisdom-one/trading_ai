"""
Constants and configuration values for Super Trader AI
"""

# Ticker categories for different asset types
TICKER_CATEGORIES = {
    "Stocks": [
        # Tech & Communications
        "AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "NVDA", "AMD", "NFLX", "INTC", "CSCO", "CRM", "ORCL", "IBM", "QCOM", "TXN", "AVGO", "ADBE",
        # Finance
        "JPM", "BAC", "WFC", "C", "GS", "MS", "AXP", "V", "MA", "PYPL",
        # Healthcare
        "JNJ", "PFE", "UNH", "MRK", "ABBV", "LLY", "TMO", "MDT", "DHR",
        # Consumer
        "WMT", "KO", "PEP", "PG", "COST", "NKE", "MCD", "HD", "LOW", "SBUX",
        # Energy & Industrials
        "XOM", "CVX", "BA", "CAT", "GE", "MMM", "HON", "LMT", "RTX", "UNP",
        # ETFs
        "SPY", "QQQ", "DIA", "IWM", "VTI", "VOO", "ARKK", "XLK", "XLF", "XLV"
    ],
    "Forex": [
        "C:EURUSD", "C:GBPUSD", "C:USDJPY", "C:USDCHF", "C:AUDUSD", "C:USDCAD", "C:NZDUSD", 
        "C:EURGBP", "C:EURJPY", "C:EURAUD", "C:EURCAD", "C:EURCHF",
        "C:GBPJPY", "C:GBPAUD", "C:GBPCAD", "C:GBPCHF",
        "C:AUDJPY", "C:CADJPY", "C:CHFJPY", "C:NZDJPY"
    ],
    "Crypto": [
        "X:BTCUSD", "X:ETHUSD", "X:SOLUSD", "X:XRPUSD", "X:ADAUSD", "X:DOGEUSD", 
        "X:DOTUSD", "X:AVAXUSD", "X:MATICUSD", "X:LINKUSD", "X:UNIUSD", "X:LTCUSD", 
        "X:BCHUSD", "X:XLMUSD", "X:ATOMUSD", "X:NEARUSD", "X:APTUSD", "X:ALGOUSD",
        "X:AAVEUSD", "X:MKRUSD", "X:SHIBUSD", "X:TRXUSD", "X:FILUSD", "X:VETUSD"
    ]
}

# Flat list for auto-suggestions
ALL_TICKERS = [ticker for tickers in TICKER_CATEGORIES.values() for ticker in tickers]

# Application settings
APP_TITLE = "Super Trader AI - Hybride Math/RL"
APP_CONFIG = {
    "page_title": "Super Trader AI - Pocket Option",
    "layout": "wide"
}

# Default trading parameters
DEFAULT_TRADE_AMOUNT = 1.0
DEFAULT_STOP_LOSS = 50.0
DEFAULT_TAKE_PROFIT = 100.0

# Data configuration
DEFAULT_INITIAL_CANDLES = 50
DEFAULT_AUTO_RELOAD_THRESHOLD = 10

# Buffer configuration
BUFFER_PREFIX = "data_buffer"
DEFAULT_BUFFER_THRESHOLD = 10

# UI Configuration
LOG_ENTRIES_LIMIT = 50
MAX_SIMULATION_LOOPS = 200
CHART_UPDATE_INTERVAL = 0.3  # seconds
ANALYSIS_DISPLAY_INTERVAL = 10  # iterations

# Risk Management
MAX_TRADING_LOOPS = 200
EVOLUTION_PROBABILITY = 0.01
