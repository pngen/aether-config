# aether_config/api.py
"""
FastAPI admin backend with JWT-based RBAC.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import jwt
import datetime
from .core import ConfigManager, ConfigSchema
from .consensus import ConsensusNode

# JWT configuration
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class User(BaseModel):
    username: str
    role: str

class ConfigCreate(BaseModel):
    name: str
    data: dict

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

def create_access_token(data: dict):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token."""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return User(username=username, role="admin")  # Simplified
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def create_app(config_manager: ConfigManager, consensus_node: ConsensusNode):
    """Create FastAPI application."""
    app = FastAPI(title="Aether Config API")
    
    @app.post("/login", response_model=Token)
    async def login():
        """Login endpoint."""
        access_token = create_access_token(data={"sub": "admin"})
        return {"access_token": access_token, "token_type": "bearer"}
    
    @app.get("/configs/{name}", response_model=ConfigSchema)
    async def get_config(name: str, version: int = None, user: User = Depends(get_current_user)):
        """Get configuration."""
        try:
            config = await config_manager.get_config(name, version)
            return config
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    @app.post("/configs", response_model=ConfigSchema)
    async def create_config(config: ConfigCreate, user: User = Depends(get_current_user)):
        """Create new configuration."""
        try:
            schema = ConfigSchema(
                name=config.name,
                version=1,
                data=config.data
            )
            await config_manager.set_config(schema)
            return schema
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.put("/configs/{name}", response_model=ConfigSchema)
    async def update_config(name: str, config: ConfigCreate, user: User = Depends(get_current_user)):
        """Update configuration."""
        try:
            latest = await config_manager.get_config(name)
            schema = ConfigSchema(
                name=name,
                version=latest.version + 1,
                data=config.data
            )
            await config_manager.set_config(schema)
            return schema
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/configs/{name}/versions", response_model=List[int])
    async def list_versions(name: str, user: User = Depends(get_current_user)):
        """List all versions of a configuration."""
        try:
            return await config_manager.list_configs(name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app