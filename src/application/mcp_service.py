"""
MCP Application Service.
Provides tool definitions, diagnostics, and vector DB status helpers for the Model Context Protocol server.
"""
from typing import List, Dict, Any, Optional
from src.domain.entities import MCPToolInfo, ClassificationCategory
from src.application.retrieval import RetrieveKnowledgeUseCase
from src.application.ingestion import IngestDocumentsUseCase
from src.infrastructure.vector_store import ChromaVectorStore
from src.infrastructure.config import settings


class MCPService:
    """Manages MCP Tool execution, status reporting, and connection diagnostics."""

    def __init__(
        self,
        retriever: Optional[RetrieveKnowledgeUseCase] = None,
        ingester: Optional[IngestDocumentsUseCase] = None,
        vector_store: Optional[ChromaVectorStore] = None
    ):
        self.retriever = retriever or RetrieveKnowledgeUseCase()
        self.ingester = ingester or IngestDocumentsUseCase()
        self.vector_store = vector_store or ChromaVectorStore(
            persist_directory=str(settings.VECTOR_DB_PATH),
            collection_name=settings.VECTOR_COLLECTION_NAME
        )

    def get_registered_tools(self) -> List[MCPToolInfo]:
        """Returns schemas of all tools exposed by the Electronics RAG MCP server."""
        return [
            MCPToolInfo(
                name="query_electronics_knowledge",
                description="Queries the electronics vector database to retrieve technical documentation, schematics, component pinouts, op-amp calculations, SMPS designs, and protocols with sources.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The electronics technical question or query (e.g. 'How to calculate buck converter inductor value' or 'ESP32 SPI pinout config')."
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category filter: 'Power Electronics & SMPS', 'Microcontrollers & Embedded Systems', 'Analog Circuits & Op-Amps', 'Digital Systems & Communication Protocols', 'Passive Components & Sensors', 'RF & Wireless Electronics'.",
                            "enum": [c.value for c in ClassificationCategory]
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of top relevant knowledge chunks to retrieve (default: 4).",
                            "default": 4
                        }
                    },
                    "required": ["query"]
                }
            ),
            MCPToolInfo(
                name="list_electronics_categories",
                description="Lists all available knowledge categories and document statistics stored in the electronics vector database.",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPToolInfo(
                name="get_system_health",
                description="Returns health status of the electronics RAG vector store, embedding model, and MCP server runtime.",
                input_schema={
                    "type": "object",
                    "properties": {}
                }
            ),
            MCPToolInfo(
                name="trigger_ingestion_pipeline",
                description="Triggers document ingestion from the data/sample_docs directory to update vector database with new electronics files.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source_directory": {
                            "type": "string",
                            "description": "Optional custom folder path to ingest documents from."
                        }
                    }
                }
            )
        ]

    def query_electronics(self, query: str, category: Optional[str] = None, top_k: int = 4) -> Dict[str, Any]:
        """Handler for query_electronics_knowledge MCP tool."""
        return self.retriever.execute(
            query_text=query,
            top_k=top_k,
            category=category
        )

    def list_categories(self) -> Dict[str, Any]:
        """Handler for list_electronics_categories MCP tool."""
        stats = self.vector_store.get_stats()
        return {
            "available_categories": [c.value for c in ClassificationCategory],
            "database_stats": stats
        }

    def get_health(self) -> Dict[str, Any]:
        """Handler for get_system_health MCP tool."""
        stats = self.vector_store.get_stats()
        return {
            "status": "healthy",
            "server_name": settings.MCP_SERVER_NAME,
            "transport": settings.MCP_TRANSPORT,
            "embedding_provider": settings.EMBEDDING_PROVIDER,
            "embedding_model": settings.EMBEDDING_MODEL_NAME,
            "total_indexed_chunks": stats.get("total_chunks", 0),
            "vector_store_backend": stats.get("backend", "Unknown")
        }

    def run_ingestion(self, source_dir: Optional[str] = None) -> Dict[str, Any]:
        """Handler for trigger_ingestion_pipeline MCP tool."""
        return self.ingester.execute(source_path=source_dir)
