import sys
import math
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.domain.entities import Chunk, KnowledgeQuery, RetrievalResult, ClassificationCategory
from src.domain.interfaces import VectorStoreInterface


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class ChromaVectorStore(VectorStoreInterface):
    """Vector database implementation using ChromaDB."""

    def __init__(self, persist_directory: str = "./data/vector_store", collection_name: str = "electronics_knowledge"):
        self.persist_directory = str(Path(persist_directory).resolve())
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._fallback_store: List[Chunk] = []
        self._is_using_chroma = False
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            from chromadb.config import Settings
            
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_directory)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self._is_using_chroma = True
        except Exception as e:
            sys.stderr.write(f"Notice: ChromaDB initialization ({e}). Using persistent in-memory/JSON fallback store.\n")
            sys.stderr.flush()
            self._is_using_chroma = False
            self._load_fallback_from_disk()

    def _get_fallback_file(self) -> Path:
        p = Path(self.persist_directory)
        p.mkdir(parents=True, exist_ok=True)
        return p / f"{self.collection_name}_fallback.json"

    def _load_fallback_from_disk(self):
        f = self._get_fallback_file()
        if f.exists():
            try:
                with open(f, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self._fallback_store = [Chunk(**item) for item in data]
            except Exception:
                self._fallback_store = []

    def _save_fallback_to_disk(self):
        f = self._get_fallback_file()
        try:
            with open(f, "w", encoding="utf-8") as file:
                json.dump([chunk.model_dump(mode="json") for chunk in self._fallback_store], file, indent=2)
        except Exception as e:
            print(f"Error saving fallback store: {e}")

    def add_chunks(self, chunks: List[Chunk]) -> int:
        if not chunks:
            return 0

        if self._is_using_chroma and self._collection is not None:
            ids = [chunk.id for chunk in chunks]
            documents = [chunk.clean_content for chunk in chunks]
            embeddings = [chunk.embedding for chunk in chunks]
            metadatas = [
                {
                    "document_id": chunk.document_id,
                    "source_title": chunk.source_title,
                    "source_path": chunk.source_path,
                    "chunk_index": chunk.chunk_index,
                    "category": chunk.category.value if hasattr(chunk.category, "value") else str(chunk.category),
                    "confidence": float(chunk.confidence),
                    "tags": ",".join(chunk.tags),
                }
                for chunk in chunks
            ]
            
            # Upsert into Chroma
            self._collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            return len(chunks)
        else:
            # Fallback
            existing_ids = {c.id for c in self._fallback_store}
            for c in chunks:
                if c.id in existing_ids:
                    self._fallback_store = [x for x in self._fallback_store if x.id != c.id]
                self._fallback_store.append(c)
            self._save_fallback_to_disk()
            return len(chunks)

    def search(self, query: KnowledgeQuery, query_embedding: List[float]) -> List[RetrievalResult]:
        if self._is_using_chroma and self._collection is not None:
            where_filter = None
            if query.category_filter:
                cat_val = query.category_filter.value if hasattr(query.category_filter, "value") else str(query.category_filter)
                where_filter = {"category": cat_val}

            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=query.top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )

            retrieval_results = []
            if results and results.get("ids") and results["ids"][0]:
                ids = results["ids"][0]
                docs = results["documents"][0]
                metas = results["metadatas"][0]
                distances = results["distances"][0]

                for i in range(len(ids)):
                    # Distance to similarity (for cosine space in chroma, sim = 1 - distance)
                    dist = distances[i] if distances else 0.0
                    sim = 1.0 - dist if dist is not None else 1.0
                    if sim < query.min_similarity:
                        continue

                    meta = metas[i] or {}
                    tags = meta.get("tags", "").split(",") if meta.get("tags") else []
                    
                    retrieval_results.append(
                        RetrievalResult(
                            chunk_id=ids[i],
                            document_id=meta.get("document_id", ""),
                            source_title=meta.get("source_title", "Unknown"),
                            source_path=meta.get("source_path", ""),
                            chunk_index=int(meta.get("chunk_index", 0)),
                            content=docs[i],
                            category=meta.get("category", "General Electronics"),
                            score=round(sim, 4),
                            tags=[t for t in tags if t],
                            metadata=meta
                        )
                    )
            return retrieval_results
        else:
            # Fallback search
            scored = []
            for chunk in self._fallback_store:
                if query.category_filter:
                    cat_val = query.category_filter.value if hasattr(query.category_filter, "value") else str(query.category_filter)
                    chunk_cat = chunk.category.value if hasattr(chunk.category, "value") else str(chunk.category)
                    if chunk_cat != cat_val:
                        continue

                sim = cosine_similarity(query_embedding, chunk.embedding or [0.0] * len(query_embedding))
                if sim >= query.min_similarity:
                    scored.append((sim, chunk))

            scored.sort(key=lambda x: x[0], reverse=True)
            top_items = scored[:query.top_k]

            return [
                RetrievalResult(
                    chunk_id=item[1].id,
                    document_id=item[1].document_id,
                    source_title=item[1].source_title,
                    source_path=item[1].source_path,
                    chunk_index=item[1].chunk_index,
                    content=item[1].clean_content,
                    category=item[1].category.value if hasattr(item[1].category, "value") else str(item[1].category),
                    score=round(item[0], 4),
                    tags=item[1].tags,
                    metadata=item[1].metadata
                )
                for item in top_items
            ]

    def count(self) -> int:
        if self._is_using_chroma and self._collection is not None:
            return self._collection.count()
        return len(self._fallback_store)

    def get_stats(self) -> Dict[str, Any]:
        cnt = self.count()
        categories: Dict[str, int] = {}
        
        if self._is_using_chroma and self._collection is not None:
            data = self._collection.get(include=["metadatas"])
            for meta in data.get("metadatas", []):
                cat = meta.get("category", "Unknown")
                categories[cat] = categories.get(cat, 0) + 1
        else:
            for chunk in self._fallback_store:
                cat = chunk.category.value if hasattr(chunk.category, "value") else str(chunk.category)
                categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_chunks": cnt,
            "backend": "ChromaDB" if self._is_using_chroma else "Persistent JSON Fallback",
            "persist_directory": self.persist_directory,
            "collection_name": self.collection_name,
            "categories_breakdown": categories
        }

    def clear(self) -> bool:
        if self._is_using_chroma and self._client is not None:
            self._client.delete_collection(self.collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return True
        else:
            self._fallback_store = []
            self._save_fallback_to_disk()
            return True
