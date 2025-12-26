# aether_config

A distributed configuration and secrets orchestration system with:

- Versioned, typed configuration schemas (Pydantic v2)
- Lightweight consensus protocol (Raft-like simplified implementation)
- Admin FastAPI backend with JWT-based RBAC
- Hot-reload watchers for dependent services
- Pluggable storage backends (S3, Redis, Postgres)
- Zero-downtime config rotation

## Features

### Core Components
1. **ConfigManager** - Manages configuration versions with storage backend
2. **ConsensusNode** - Simplified Raft-like consensus protocol
3. **StorageBackend** - Abstract interface for pluggable storage backends
4. **FastAPI Admin API** - JWT-based RBAC with CRUD operations

### Storage Backends
- InMemoryStorage (for testing)
- RedisStorage
- PostgresStorage

### Consensus Protocol
- Simplified Raft implementation with leader election
- Heartbeat mechanism for follower detection
- Configuration replication simulation

## Installation