"""
Polygon.io API Client
SOLID Principle: Single Responsibility - This module ONLY fetches data, no UI logic.
Security: Input validation on ticker, no secrets logging.
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Optional
import re


class PolygonClient:
    """Client for Polygon.io REST API."""
    
    BASE_URL = "https://api.polygon.io"
    
    def __init__(self, api_key: str):
        """
        Initialize the client with an API key.
        
        Args:
            api_key: Your Polygon.io API key.
        """
        self._api_key = api_key
        self._session = requests.Session()
    
    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """
        Validate ticker format (alphanumeric, colon for crypto, max 20 chars).
        Security: Prevents injection attacks via ticker parameter.
        """
        if not ticker or len(ticker) > 20:
            return False
        # Allow A-Z, 0-9, colon (for X:BTCUSD format), hyphen, dot
        return bool(re.match(r'^[A-Za-z0-9:\-\.]+$', ticker))
    
    def get_aggregates(
        self, 
        ticker: str, 
        multiplier: int = 1, 
        timespan: str = "minute", 
        from_date: Optional[str] = None, 
        to_date: Optional[str] = None, 
        limit: int = 5000
    ) -> Tuple[bool, pd.DataFrame, str]:
        """
        Fetch historical aggregate data (OHLCV candles).
        
        Args:
            ticker: The ticker symbol (e.g., 'AAPL', 'X:BTCUSD').
            multiplier: The size of the timespan multiplier.
            timespan: The size of the time window (minute, hour, day).
            from_date: Start date (YYYY-MM-DD). Defaults to 30 days ago.
            to_date: End date (YYYY-MM-DD). Defaults to today.
            limit: Max number of results.
            
        Returns:
            Tuple of (success: bool, data: DataFrame, error_message: str)
        """
        # Validate inputs
        if not self._api_key:
            return False, pd.DataFrame(), "Clé API manquante."
        
        if not self.validate_ticker(ticker):
            return False, pd.DataFrame(), f"Ticker invalide: {ticker}"
        
        # Default date range: last 30 days
        if not from_date:
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not to_date:
            to_date = datetime.now().strftime('%Y-%m-%d')

        endpoint = f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        url = f"{self.BASE_URL}{endpoint}"
        
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": limit,
            "apiKey": self._api_key
        }

        try:
            response = self._session.get(url, params=params, timeout=30)
            
            # Handle HTTP errors
            if response.status_code == 401:
                return False, pd.DataFrame(), "Clé API invalide (401 Unauthorized)."
            if response.status_code == 403:
                return False, pd.DataFrame(), "Accès refusé (403 Forbidden)."
            if response.status_code != 200:
                return False, pd.DataFrame(), f"Erreur HTTP {response.status_code}."
            
            # Parse JSON
            try:
                data = response.json()
            except ValueError:
                return False, pd.DataFrame(), "Réponse API invalide (JSON parse error)."
            
            # Check API status (OK or DELAYED for free plans)
            status = data.get("status", "")
            if status not in ["OK", "DELAYED"]:
                error_msg = data.get("error", "Statut API inconnu.")
                return False, pd.DataFrame(), f"API Error: {error_msg}"
            
            # Check for results
            if data.get("resultsCount", 0) == 0:
                return False, pd.DataFrame(), "Aucune donnée disponible pour cette période."
            
            # Build DataFrame
            results = data["results"]
            df = pd.DataFrame(results)
            
            # Rename columns: Polygon uses t, o, h, l, c, v
            df = df.rename(columns={
                't': 'timestamp',
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume'
            })
            
            # Convert timestamp from ms to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Ensure numeric types (security against unexpected data types)
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Select only required columns
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            return True, df, ""
            
        except requests.exceptions.Timeout:
            return False, pd.DataFrame(), "Timeout de connexion à l'API."
        except requests.exceptions.ConnectionError:
            return False, pd.DataFrame(), "Erreur de connexion réseau."
        except Exception as e:
            # Generic fallback - do not expose internal details
            return False, pd.DataFrame(), f"Erreur interne: {type(e).__name__}"
