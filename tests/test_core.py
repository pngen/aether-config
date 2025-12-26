# tests/test_core.py
"""
Unit tests for core components.
"""

import pytest
from aether_config.core import ConfigManager, ConfigSchema
from aether_config.storage import InMemoryStorage

@pytest.fixture
def storage():
    return InMemoryStorage()

@pytest.fixture
def config_manager(storage):
    return ConfigManager(storage)

@pytest.mark.asyncio
async def test_set_and_get_config(config_manager):
    """Test setting and getting configuration."""
    schema = ConfigSchema(
        name="test-config",
        version=1,
        data={"key": "value"}
    )
    
    # Set config
    result = await config_manager.set_config(schema)
    assert result is True
    
    # Get config
    retrieved = await config_manager.get_config("test-config")
    assert retrieved.name == "test-config"
    assert retrieved.version == 1
    assert retrieved.data["key"] == "value"

@pytest.mark.asyncio
async def test_list_configs(config_manager):
    """Test listing configuration versions."""
    # Create multiple versions
    for i in range(3):
        schema = ConfigSchema(
            name="test-config",
            version=i+1,
            data={"key": f"value-{i}"}
        )
        await config_manager.set_config(schema)
    
    versions = await config_manager.list_configs("test-config")
    assert versions == [0, 1, 2]

@pytest.mark.asyncio
async def test_watch_config(config_manager):
    """Test watching configuration changes."""
    schema = ConfigSchema(
        name="watch-test",
        version=1,
        data={"key": "value"}
    )
    
    queue = await config_manager.watch_config("watch-test")
    
    # Set config should notify watchers
    await config_manager.set_config(schema)
    
    # Check that we got the notification
    result = await queue.get()
    assert result.name == "watch-test"