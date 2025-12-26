# tests/test_storage.py
"""
Unit tests for storage backends.
"""

import pytest
from aether_config.storage import InMemoryStorage, RedisStorage, PostgresStorage
from aether_config.core import ConfigSchema

@pytest.fixture
def in_memory_storage():
    return InMemoryStorage()

@pytest.mark.asyncio
async def test_in_memory_storage(in_memory_storage):
    """Test in-memory storage backend."""
    schema = ConfigSchema(
        name="test",
        version=1,
        data={"key": "value"}
    )
    
    # Save config
    result = await in_memory_storage.save_config(schema)
    assert result is True
    
    # Get latest config
    retrieved = await in_memory_storage.get_latest_config("test")
    assert retrieved.name == "test"
    assert retrieved.data["key"] == "value"
    
    # List versions
    versions = await in_memory_storage.list_config_versions("test")
    assert versions == [0]

@pytest.mark.asyncio
async def test_in_memory_storage_multiple_versions(in_memory_storage):
    """Test multiple versions in storage."""
    for i in range(3):
        schema = ConfigSchema(
            name="multi-test",
            version=i,
            data={"version": i}
        )
        await in_memory_storage.save_config(schema)
    
    # Get specific version
    retrieved = await in_memory_storage.get_config_by_version("multi-test", 1)
    assert retrieved.data["version"] == 1
    
    # List versions
    versions = await in_memory_storage.list_config_versions("multi-test")
    assert versions == [0, 1, 2]