# aether_config/__init__.py
"""
Aether Config - Distributed Configuration & Secrets Orchestrator
"""

__version__ = "0.1.0"
__author__ = "Senior Engineer"

from .core import ConfigManager, ConfigSchema
from .consensus import ConsensusNode
from .storage import StorageBackend
from .api import create_app

__all__ = [
    "ConfigManager",
    "ConfigSchema",
    "ConsensusNode",
    "StorageBackend",
    "create_app"
]