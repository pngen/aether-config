# aether_config/storage.py
"""
Storage backend interface and implementations.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional
from .core import ConfigSchema

class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    async def save_config(self, config: ConfigSchema) -> bool:
        """Save a configuration."""
        pass
    
    @abstractmethod
    async def get_latest_config(self, name: str) -> ConfigSchema:
        """Get the latest version of a configuration."""
        pass
    
    @abstractmethod
    async def get_config_by_version(self, name: str, version: int) -> ConfigSchema:
        """Get a specific version of a configuration."""
        pass
    
    @abstractmethod
    async def list_config_versions(self, name: str) -> List[int]:
        """List all versions of a configuration."""
        pass

class InMemoryStorage(StorageBackend):
    """In-memory storage backend for testing."""
    
    def __init__(self):
        self._configs: Dict[str, List[ConfigSchema]] = {}
        
    async def save_config(self, config: ConfigSchema) -> bool:
        if config.name not in self._configs:
            self._configs[config.name] = []
        self._configs[config.name].append(config)
        return True
    
    async def get_latest_config(self, name: str) -> ConfigSchema:
        if name not in self._configs or not self._configs[name]:
            raise KeyError(f"No config found for {name}")
        return self._configs[name][-1]
    
    async def get_config_by_version(self, name: str, version: int) -> ConfigSchema:
        if name not in self._configs or version >= len(self._configs[name]):
            raise KeyError(f"Config {name} version {version} not found")
        return self._configs[name][version]
    
    async def list_config_versions(self, name: str) -> List[int]:
        if name not in self._configs:
            return []
        return list(range(len(self._configs[name])))

class RedisStorage(StorageBackend):
    """Redis-based storage backend."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
    async def save_config(self, config: ConfigSchema) -> bool:
        key = f"config:{config.name}:{config.version}"
        await self.redis.set(key, config.json())
        return True
    
    async def get_latest_config(self, name: str) -> ConfigSchema:
        # Get latest version from Redis
        keys = await self.redis.keys(f"config:{name}:*")
        if not keys:
            raise KeyError(f"No config found for {name}")
        # Sort by version and get last one
        versions = [int(k.split(":")[-1]) for k in keys]
        latest_version = max(versions)
        key = f"config:{name}:{latest_version}"
        data = await self.redis.get(key)
        return ConfigSchema.parse_raw(data)
    
    async def get_config_by_version(self, name: str, version: int) -> ConfigSchema:
        key = f"config:{name}:{version}"
        data = await self.redis.get(key)
        if not data:
            raise KeyError(f"Config {name} version {version} not found")
        return ConfigSchema.parse_raw(data)
    
    async def list_config_versions(self, name: str) -> List[int]:
        keys = await self.redis.keys(f"config:{name}:*")
        versions = [int(k.split(":")[-1]) for k in keys]
        return sorted(versions)

class PostgresStorage(StorageBackend):
    """PostgreSQL-based storage backend."""
    
    def __init__(self, connection_pool):
        self.pool = connection_pool
        
    async def save_config(self, config: ConfigSchema) -> bool:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO configs (name, version, data)
                VALUES ($1, $2, $3)
                ON CONFLICT (name, version) DO UPDATE SET data = EXCLUDED.data
                """,
                config.name,
                config.version,
                config.json()
            )
        return True
    
    async def get_latest_config(self, name: str) -> ConfigSchema:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM configs WHERE name = $1 ORDER BY version DESC LIMIT 1",
                name
            )
            if not row:
                raise KeyError(f"No config found for {name}")
            return ConfigSchema.parse_raw(row['data'])
    
    async def get_config_by_version(self, name: str, version: int) -> ConfigSchema:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM configs WHERE name = $1 AND version = $2",
                name,
                version
            )
            if not row:
                raise KeyError(f"Config {name} version {version} not found")
            return ConfigSchema.parse_raw(row['data'])
    
    async def list_config_versions(self, name: str) -> List[int]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT version FROM configs WHERE name = $1 ORDER BY version",
                name
            )
            return [row['version'] for row in rows]