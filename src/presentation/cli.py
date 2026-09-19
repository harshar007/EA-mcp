"""
Command Line Interface for Electronics RAG & MCP Pipeline.
Clean Architecture - Presentation Layer.
"""
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.application.ingestion import IngestDocumentsUseCase
from src.application.retrieval import RetrieveKnowledgeUseCase
from src.application.mcp_service import MCPService
from src.presentation.mcp_server import ElectronicsMCPServer


def main():
    parser = argparse.ArgumentParser(description="Electronics RAG Pipeline and MCP Server Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest electronics documents into vector store")
    ingest_parser.add_argument("--dir", type=str, default=None, help="Custom documents directory")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query vector knowledge base")
    query_parser.add_argument("text", type=str, help="Question / query text")
    query_parser.add_argument("--category", type=str, default=None, help="Optional category filter")
    query_parser.add_argument("--top-k", type=int, default=4, help="Number of results")

    # Serve MCP command
    subparsers.add_parser("serve-mcp", help="Run the MCP Server over stdio")

    # Stats command
    subparsers.add_parser("stats", help="Show vector database statistics")

    args = parser.parse_args()

    if args.command == "ingest":
        print("⚡ Starting Electronics Document Ingestion Pipeline...")
        use_case = IngestDocumentsUseCase()
        res = use_case.execute(source_path=args.dir)
        print(f"✅ Ingestion Complete! Loaded {res.get('documents_loaded')} docs, indexed {res.get('chunks_indexed')} chunks.")
        print(f"📊 Categories Summary: {res.get('categories_summary')}")

    elif args.command == "query":
        print(f"🔍 Searching for: '{args.text}'")
        retriever = RetrieveKnowledgeUseCase()
        res = retriever.execute(query_text=args.text, top_k=args.top_k, category=args.category)
        print(f"Found {res.get('results_count')} results:\n")
        print(res.get("formatted_context_for_llm"))

    elif args.command == "serve-mcp":
        server = ElectronicsMCPServer()
        server.run_stdio()

    elif args.command == "stats":
        service = MCPService()
        stats = service.list_categories()
        import json
        print(json.dumps(stats, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
