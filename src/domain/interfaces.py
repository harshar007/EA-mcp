"""
Domain Interfaces (Contracts) for Clean Architecture.
Decouples business logic from external frameworks, vector DBs, and embedding models.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from .entities import Document, Chunk, KnowledgeQuery, RetrievalResult, ClassificationCategory


class DocumentLoaderInterface(ABC):
    """Interface for loading raw electronics documents."""
    
    @abstractmethod
    def load(self, source_path: str) -> List[Document]:
        """Loads documents from a file or directory."""
        pass


class DocumentSplitterInterface(ABC):
    """Interface for cleaning and splitting documents into knowledge chunks."""
    
    @abstractmethod
    def split_document(self, document: Document) -> List[Chunk]:
        """Splits a single document into chunks."""
        pass

    @abstractmethod
    def split_documents(self, documents: List[Document]) -> List[Chunk]:
        """Splits a collection of documents into chunks."""
        pass


class ClassifierInterface(ABC):
    """Interface for classifying chunks into electronics knowledge domains."""
    
    @abstractmethod
    def classify(self, text: str) -> tuple[ClassificationCategory, float, List[str]]:
        """
        Classifies given text into an electronics domain.
        Returns: (Category, Confidence Score, List of Identified Keywords/Tags)
        """
        pass


class EmbeddingModelInterface(ABC):
    """Interface for generating dense vector embeddings."""
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of texts."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Generates embedding vector for a search query."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns embedding vector dimension."""
        pass


class VectorStoreInterface(ABC):
    """Interface for vector database operations."""
    
    @abstractmethod
    def add_chunks(self, chunks: List[Chunk]) -> int:
        """Stores chunks with their embeddings into the vector store."""
        pass

    @abstractmethod
    def search(self, query: KnowledgeQuery, query_embedding: List[float]) -> List[RetrievalResult]:
        """Performs vector similarity search with optional metadata filters."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Returns total number of stored chunks."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Returns vector database statistics (categories, counts, paths)."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clears all data in the collection."""
        pass
