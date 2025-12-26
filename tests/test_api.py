# tests/test_api.py
"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from aether_config.api import create_app
from aether_config.core import ConfigManager
from aether_config.storage import InMemoryStorage

@pytest.fixture
def storage():
    return InMemoryStorage()

@pytest.fixture
def config_manager(storage):
    return ConfigManager(storage)

@pytest.fixture
def client(config_manager):
    app = create_app(config_manager, None)
    return TestClient(app)

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_login(client):
    """Test login endpoint."""
    response = client.post("/login")
    assert response.status_code == 200
    assert "access_token" in response.json()