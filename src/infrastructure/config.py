"""
Infrastructure Configuration Settings.
Loads from environment variables or .env file with strict validation.
"""
import os
from pathlib import Path
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

from pydantic import Field, ConfigDict


class AppSettings(BaseSettings):
    """Application and Pipeline Configuration."""
    model_config = ConfigDict(extra="ignore")
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = Path(__file__).resolve().parent.parent.parent / "data"
    DOCS_DIR: Path = Path(__file__).resolve().parent.parent.parent / "data" / "sample_docs"
    VECTOR_DB_PATH: Path = Path(__file__).resolve().parent.parent.parent / "data" / "vector_store"
    
    # Vector store
    VECTOR_COLLECTION_NAME: str = "electronics_knowledge"
    
    # Embedding config
    EMBEDDING_PROVIDER: str = "sentence-transformers"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # Chunking config
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 120
    
    # MCP server config
    MCP_SERVER_NAME: str = "electronics-rag-mcp"
    MCP_SERVER_HOST: str = "127.0.0.1"
    MCP_SERVER_PORT: int = 8000
    MCP_TRANSPORT: str = "stdio"  # "stdio" or "sse"
    
    # Admin UI config
    UI_PORT: int = 8501


settings = AppSettings()
# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.DOCS_DIR.mkdir(parents=True, exist_ok=True)
settings.VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
