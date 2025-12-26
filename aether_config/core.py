# aether_config/core.py
"""
Core configuration management with versioning and validation.
"""

import asyncio
import json
import time
from typing import Any, Dict, Optional, Type, Union
from pydantic import BaseModel, Field
from .storage import StorageBackend

class ConfigSchema(BaseModel):
    """Typed configuration schema."""
    name: str = Field(..., description="Configuration name")
    version: int = Field(..., description="Version number")
    data: Dict[str, Any] = Field(..., description="Configuration data")
    created_at: float = Field(default_factory=time.time)
    
    class Config:
        frozen = True

class ConfigManager:
    """Manages configuration versions with storage backend."""
    
    def __init__(self, storage_backend: StorageBackend):
        self.storage = storage_backend
        self._watchers: Dict[str, asyncio.Queue] = {}
        
    async def set_config(self, schema: ConfigSchema) -> bool:
        """Set a new configuration version."""
        try:
            await self.storage.save_config(schema)
            # Notify watchers
            if schema.name in self._watchers:
                for queue in self._watchers[schema.name]:
                    await queue.put(schema)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to save config: {e}")
    
    async def get_config(self, name: str, version: Optional[int] = None) -> ConfigSchema:
        """Get configuration by name and optional version."""
        try:
            if version is None:
                return await self.storage.get_latest_config(name)
            return await self.storage.get_config_by_version(name, version)
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve config: {e}")
    
    async def watch_config(self, name: str) -> asyncio.Queue:
        """Watch for configuration changes."""
        if name not in self._watchers:
            self._watchers[name] = []
        queue = asyncio.Queue()
        self._watchers[name].append(queue)
        return queue
    
    async def list_configs(self, name: str) -> list:
        """List all versions of a configuration."""
        try:
            return await self.storage.list_config_versions(name)
        except Exception as e:
            raise RuntimeError(f"Failed to list configs: {e}")