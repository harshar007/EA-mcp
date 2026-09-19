"""
Document Ingestion Pipeline Use Case.
Clean Architecture - Application Layer.
Coordinates: Loading -> Cleaning & Splitting -> Categorization -> Embedding -> Vector DB Storage.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.domain.entities import Document, Chunk
from src.domain.interfaces import (
    DocumentLoaderInterface,
    DocumentSplitterInterface,
    EmbeddingModelInterface,
    VectorStoreInterface,
)
from src.infrastructure.loaders import UniversalDocumentLoader
from src.infrastructure.splitters import CleanElectronicsSplitter
from src.infrastructure.embeddings import get_embedding_model
from src.infrastructure.vector_store import ChromaVectorStore
from src.infrastructure.config import settings


class IngestDocumentsUseCase:
    """Orchestrates end-to-end ingestion of general electronics documents."""

    def __init__(
        self,
        loader: Optional[DocumentLoaderInterface] = None,
        splitter: Optional[DocumentSplitterInterface] = None,
        embedder: Optional[EmbeddingModelInterface] = None,
        vector_store: Optional[VectorStoreInterface] = None,
    ):
        self.loader = loader or UniversalDocumentLoader()
        self.splitter = splitter or CleanElectronicsSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.embedder = embedder or get_embedding_model(
            provider=settings.EMBEDDING_PROVIDER,
            model_name=settings.EMBEDDING_MODEL_NAME
        )
        self.vector_store = vector_store or ChromaVectorStore(
            persist_directory=str(settings.VECTOR_DB_PATH),
            collection_name=settings.VECTOR_COLLECTION_NAME
        )

    def execute(self, source_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the full ingestion pipeline from raw files to vector storage.
        """
        path_to_load = source_path or str(settings.DOCS_DIR)
        
        # Step 1: Load raw electronics documents
        documents: List[Document] = self.loader.load(path_to_load)
        if not documents:
            return {
                "status": "warning",
                "message": f"No supported documents found in {path_to_load}",
                "documents_loaded": 0,
                "chunks_created": 0,
                "chunks_indexed": 0
            }

        # Step 2: Clean, split, and classify knowledge
        chunks: List[Chunk] = self.splitter.split_documents(documents)
        if not chunks:
            return {
                "status": "warning",
                "message": "Documents were loaded but yielded 0 chunks.",
                "documents_loaded": len(documents),
                "chunks_created": 0,
                "chunks_indexed": 0
            }

        # Step 3: Generate dense embeddings for knowledge chunks
        texts_to_embed = [chunk.clean_content for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts_to_embed)

        for chunk, emb in zip(chunks, embeddings):
            chunk.embedding = emb

        # Step 4: Store into Vector Database
        indexed_count = self.vector_store.add_chunks(chunks)

        # Category breakdown
        category_counts: Dict[str, int] = {}
        for c in chunks:
            cat_name = c.category.value if hasattr(c.category, "value") else str(c.category)
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

        return {
            "status": "success",
            "source_path": path_to_load,
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "chunks_indexed": indexed_count,
            "categories_summary": category_counts,
            "vector_store_total": self.vector_store.count()
        }
