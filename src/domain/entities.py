"""
Domain Entities and Data Models for Electronics RAG & MCP System.
Clean Architecture - Domain Layer.
"""
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone


class ClassificationCategory(str, Enum):
    POWER_ELECTRONICS = "Power Electronics & SMPS"
    MICROCONTROLLERS_EMBEDDED = "Microcontrollers & Embedded Systems"
    ANALOG_CIRCUITS = "Analog Circuits & Op-Amps"
    DIGITAL_SYSTEMS_PROTOCOLS = "Digital Systems & Communication Protocols"
    PASSIVE_COMPONENTS = "Passive Components & Sensors"
    RF_WIRELESS = "RF & Wireless Electronics"
    GENERAL_ELECTRONICS = "General Electronics & Fundamentals"


class Document(BaseModel):
    """Represents a raw loaded document before splitting."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    source_path: str
    content: str
    file_type: str = "text"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Chunk(BaseModel):
    """Represents a split, classified, and embeddable knowledge chunk."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    source_title: str
    source_path: str
    chunk_index: int
    content: str
    clean_content: str
    category: ClassificationCategory = ClassificationCategory.GENERAL_ELECTRONICS
    confidence: float = 1.0
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeQuery(BaseModel):
    """Query object for retrieving electronics knowledge."""
    query_text: str
    top_k: int = 5
    category_filter: Optional[ClassificationCategory] = None
    min_similarity: float = 0.0
    include_metadata: bool = True


class RetrievalResult(BaseModel):
    """Search result returned to caller / MCP server."""
    chunk_id: str
    document_id: str
    source_title: str
    source_path: str
    chunk_index: int
    content: str
    category: str
    score: float
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MCPServerConfig(BaseModel):
    """Configuration data for MCP server connection and runtime."""
    server_name: str = "electronics-rag-mcp"
    transport: str = "stdio"  # stdio | sse
    host: str = "0.0.0.0"
    port: int = 8000
    vector_db_path: str = "./data/vector_store"
    collection_name: str = "electronics_knowledge"
    embedding_model: str = "all-MiniLM-L6-v2"
    auth_token: Optional[str] = None


class MCPToolInfo(BaseModel):
    """Metadata describing an MCP Tool exposed by the server."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    category: str = "Electronics RAG"
