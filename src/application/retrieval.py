"""
Knowledge Retrieval Use Case.
Clean Architecture - Application Layer.
Queries Vector Database, performs similarity search, and formats citations/sources for MCP Clients & AI Agents.
"""
from typing import List, Dict, Any, Optional
from src.domain.entities import KnowledgeQuery, RetrievalResult, ClassificationCategory
from src.domain.interfaces import EmbeddingModelInterface, VectorStoreInterface
from src.infrastructure.embeddings import get_embedding_model
from src.infrastructure.vector_store import ChromaVectorStore
from src.infrastructure.config import settings


class RetrieveKnowledgeUseCase:
    """Retrieves electronics knowledge from Vector DB and structures response for AI agents."""

    def __init__(
        self,
        embedder: Optional[EmbeddingModelInterface] = None,
        vector_store: Optional[VectorStoreInterface] = None,
    ):
        self.embedder = embedder or get_embedding_model(
            provider=settings.EMBEDDING_PROVIDER,
            model_name=settings.EMBEDDING_MODEL_NAME
        )
        self.vector_store = vector_store or ChromaVectorStore(
            persist_directory=str(settings.VECTOR_DB_PATH),
            collection_name=settings.VECTOR_COLLECTION_NAME
        )

    def execute(
        self,
        query_text: str,
        top_k: int = 4,
        category: Optional[str] = None,
        min_similarity: float = 0.0
    ) -> Dict[str, Any]:
        """
        Executes search and formats knowledge with rich source citations.
        """
        # Parse category filter if given
        category_filter = None
        if category:
            for c in ClassificationCategory:
                if c.value.lower() == category.lower() or c.name.lower() == category.lower():
                    category_filter = c
                    break

        query = KnowledgeQuery(
            query_text=query_text,
            top_k=top_k,
            category_filter=category_filter,
            min_similarity=min_similarity
        )

        # Generate query embedding
        query_vec = self.embedder.embed_query(query_text)

        # Search Vector DB
        results: List[RetrievalResult] = self.vector_store.search(query, query_vec)

        # Format structured output for LLM agent
        citations = []
        for r in results:
            citations.append({
                "source_title": r.source_title,
                "source_path": r.source_path,
                "chunk_index": r.chunk_index,
                "category": r.category,
                "similarity_score": r.score,
                "tags": r.tags,
                "content": r.content
            })

        formatted_context = self._format_agent_context(citations)

        return {
            "query": query_text,
            "category_filter": category_filter.value if category_filter else None,
            "results_count": len(results),
            "citations": citations,
            "formatted_context_for_llm": formatted_context
        }

    def _format_agent_context(self, citations: List[Dict[str, Any]]) -> str:
        """Helper to format knowledge passages for LLMs to generate electronics answers."""
        if not citations:
            return "No relevant electronics documentation found in the vector database."

        blocks = []
        for i, c in enumerate(citations, 1):
            block = (
                f"[Source {i}: {c['source_title']} (Section/Chunk {c['chunk_index']}) | Category: {c['category']} | Score: {c['similarity_score']}]\n"
                f"{c['content']}\n"
            )
            blocks.append(block)

        return "\n---\n".join(blocks)
