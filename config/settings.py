"""
Application settings and configuration loader
"""

import os
from typing import Optional


def load_api_key_from_env(filepath: str = ".env_data") -> str:
    """
    Securely load API key from .env_data file.
    Security: Strips whitespace and invisible characters.

    Args:
        filepath: Path to the environment file

    Returns:
        Cleaned API key or empty string if not found
    """
    if not os.path.exists(filepath):
        return ""

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("POLYGON_API_KEY="):
                    raw_value = line.split("=", 1)[1]
                    # Security: Remove all non-printable characters
                    cleaned = "".join(c for c in raw_value if c.isprintable())
                    return cleaned.strip().strip('"').strip("'")
    except Exception:
        pass

    return ""


# API Configuration
POLYGON_API_CONFIG = {
    "base_url": "https://api.polygon.io",
    "timeout": 30,  # seconds
    "default_limit": 5000,
}

# Model Configuration
MODEL_CONFIG = {
    "model_file": "super_trader_ppo.zip",
    "policy": "MlpPolicy",
    "learning_rate": 3e-4,
    "n_steps": 2048,
    "batch_size": 64,
    "total_timesteps": 10000,
}

# Configuration validator
class ConfigValidator:
    """Validate configuration values"""

    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """Validate ticker format (alphanumeric, colon for crypto, max 20 chars)"""
        if not ticker or len(ticker) > 20:
            return False
        # Allow A-Z, 0-9, colon (for X:BTCUSD format), hyphen, dot
        import re
        return bool(re.match(r'^[A-Za-z0-9:\-\.]+$', ticker))

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Basic API key validation"""
        return bool(api_key and len(api_key) > 10 and api_key != "YOUR_API_KEY_HERE")


SETTINGS = {
    "load_api_key": load_api_key_from_env,
    "validator": ConfigValidator,
}
