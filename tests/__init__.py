"""
Test suite for Super Trader AI
"""

import pytest

# Test configuration
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest for the project"""
    config.addinivalue_line(
        "markers", "integration: tests that integrate multiple components"
    )
    config.addinivalue_line(
        "markers", "unit: tests for individual components"
    )
