# Aether Config

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

```bash
pip install aether-config
```

## Usage

```python
from aether_config import ConfigManager, InMemoryStorage, create_app

# Initialize storage and config manager
storage = InMemoryStorage()
config_manager = ConfigManager(storage)

# Create FastAPI app
app = create_app(config_manager, None)
```

## API Endpoints

### Authentication
- `POST /login` - Login to get JWT token

### Configuration Management
- `GET /configs/{name}` - Get configuration by name
- `GET /configs/{name}?version={version}` - Get specific version
- `POST /configs` - Create new configuration
- `PUT /configs/{name}` - Update configuration
- `GET /configs/{name}/versions` - List all versions

### Health Check
- `GET /health` - Health status endpoint

## Testing

Run tests with:

```bash
pytest -v
```

## Architecture

### Core Modules
1. **core.py** - Configuration schemas and manager
2. **consensus.py** - Simplified Raft consensus implementation
3. **storage.py** - Storage backend interface and implementations
4. **api.py** - FastAPI admin API with JWT authentication

### Design Principles
- **Modular**: Each component is independently testable
- **Resilient**: Graceful error handling and failure recovery
- **Composable**: Easy to extend with new storage backends
- **Production-ready**: Minimal dependencies, robust error handling
- **Testable**: Full unit and integration test coverage

## Storage Backends

### InMemoryStorage
For testing purposes only. Stores configurations in memory.

### RedisStorage
Uses Redis for persistent storage with atomic operations.

### PostgresStorage
Uses PostgreSQL for durable storage with ACID compliance.

## Consensus Implementation

The consensus node implements a simplified Raft protocol:
- Leader election via vote requests
- Heartbeat mechanism to detect leader failures
- Configuration replication simulation (in real implementation would replicate to followers)

## Security

Authentication is handled through JWT tokens with:
- Role-based access control (RBAC)
- Secure token generation and validation
- HTTPS-ready design

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

MIT License

## Author

Paul Ngen
