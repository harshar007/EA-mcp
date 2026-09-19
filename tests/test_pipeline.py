"""
Unit and Integration Tests for Electronics RAG and MCP Pipeline.
"""
import pytest
from src.domain.entities import Document, ClassificationCategory
from src.infrastructure.classifier import ElectronicsDomainClassifier
from src.infrastructure.splitters import CleanElectronicsSplitter
from src.infrastructure.loaders import UniversalDocumentLoader
from src.infrastructure.embeddings import DeterministicHashingEmbedding
from src.infrastructure.vector_store import ChromaVectorStore
from src.application.ingestion import IngestDocumentsUseCase
from src.application.retrieval import RetrieveKnowledgeUseCase
from src.application.mcp_service import MCPService
from src.presentation.mcp_server import ElectronicsMCPServer


def test_classifier():
    classifier = ElectronicsDomainClassifier()
    cat, conf, tags = classifier.classify("Designing an ESP32 microcontroller with GPIO and SPI bus.")
    assert cat == ClassificationCategory.MICROCONTROLLERS_EMBEDDED
    assert conf > 0.3
    assert len(tags) > 0


def test_splitter():
    splitter = CleanElectronicsSplitter(chunk_size=200, chunk_overlap=30)
    doc = Document(
        title="Test Buck Converter",
        source_path="/tmp/test.md",
        content="# Buck Converter\n\nA buck converter is a step-down SMPS with MOSFET switches and inductors.\n\n## Equation\nDuty cycle D = Vout / Vin."
    )
    chunks = splitter.split_document(doc)
    assert len(chunks) >= 1
    assert chunks[0].category == ClassificationCategory.POWER_ELECTRONICS


def test_end_to_end_ingestion_and_retrieval(tmp_path):
    # Setup temporary store
    db_dir = tmp_path / "test_vdb"
    embedder = DeterministicHashingEmbedding(dim=64)
    store = ChromaVectorStore(persist_directory=str(db_dir), collection_name="test_electronics")
    
    ingester = IngestDocumentsUseCase(embedder=embedder, vector_store=store)
    res = ingester.execute()
    assert res["status"] == "success"
    assert res["chunks_indexed"] > 0

    retriever = RetrieveKnowledgeUseCase(embedder=embedder, vector_store=store)
    query_res = retriever.execute(query_text="buck converter inductor formula", top_k=2)
    assert query_res["results_count"] > 0
    assert len(query_res["citations"]) > 0


def test_mcp_service_and_server():
    server = ElectronicsMCPServer()
    health = server.handle_tool_call("get_system_health", {})
    assert health["status"] == "healthy"

    cats = server.handle_tool_call("list_electronics_categories", {})
    assert "available_categories" in cats
