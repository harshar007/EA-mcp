"""
Embedding Adapters for Electronics RAG System.
Provides dense vector representations with sentence-transformers and lightweight deterministic fallback.
"""
import math
import hashlib
from typing import List
from src.domain.interfaces import EmbeddingModelInterface


class SentenceTransformerEmbeddingAdapter(EmbeddingModelInterface):
    """Generates dense neural embeddings using sentence-transformers (e.g. all-MiniLM-L6-v2)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dimension = 384

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                self._dimension = self._model.get_sentence_embedding_dimension()
            except Exception as e:
                print(f"Warning: Could not load sentence-transformers ({e}). Falling back to deterministic hashing embedding.")
                self._model = "fallback"

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        if self._model == "fallback":
            return [DeterministicHashingEmbedding().embed_query(t) for t in texts]
        
        embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        self._load_model()
        if self._model == "fallback":
            return DeterministicHashingEmbedding().embed_query(query)
        
        embedding = self._model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        return embedding[0].tolist()

    @property
    def dimension(self) -> int:
        return self._dimension


class DeterministicHashingEmbedding(EmbeddingModelInterface):
    """
    Lightweight, deterministic hashing-based embedding vectorizer (384 dims).
    Useful for offline testing, CI/CD, and environments without large PyTorch/HuggingFace downloads.
    """

    def __init__(self, dim: int = 384):
        self._dim = dim

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        vec = [0.0] * self._dim
        words = query.lower().split()
        if not words:
            return vec

        for word in words:
            # Multi-hash projection
            h1 = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % self._dim
            h2 = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16) % self._dim
            vec[h1] += 1.0
            vec[h2] += 0.5

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    @property
    def dimension(self) -> int:
        return self._dim


def get_embedding_model(provider: str = "sentence-transformers", model_name: str = "all-MiniLM-L6-v2") -> EmbeddingModelInterface:
    """Factory to retrieve configured embedding model."""
    if provider.lower() in {"sentence-transformers", "local", "huggingface"}:
        try:
            import sentence_transformers
            return SentenceTransformerEmbeddingAdapter(model_name=model_name)
        except ImportError:
            return DeterministicHashingEmbedding()
    elif provider.lower() == "hash":
        return DeterministicHashingEmbedding()
    else:
        return SentenceTransformerEmbeddingAdapter(model_name=model_name)
