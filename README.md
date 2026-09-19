# ⚡ Electronics RAG Pipeline & MCP Server

An enterprise-grade, **Clean Architecture** Python system implementing a specialized **Electronics Document Retrieval-Augmented Generation (RAG)** pipeline and a **Model Context Protocol (MCP)** server.

This project directly fulfills the workflow diagram:
- **Ingestion Pipeline**: Ingests, cleans, splits, classifies (Power Electronics, Microcontrollers, Analog, Digital Protocols, etc.), embeds, and indexes technical documents into a persistent Vector Database.
- **Python MCP Server**: Exposes standardized tools over MCP (stdio / SSE) for AI agents to query component datasheets, pinouts, SMPS calculations, and circuit designs with grounded source citations.
- **MCP Connection & Setup UI**: Streamlit-based administrative interface strictly designed for server setup, parameter tuning, connection testing, and tool inspection (**MCP Setup Only • No Chatbot Interface**).
- **Interactive Jupyter Notebook**: Step-by-step walkthrough covering data loading, classification, embedding generation, vector search, and AI agent tool calling simulation.

---

## 🏛️ Clean Architecture Structure

```
P:/rag pipline EA/
├── data/                                 # Storage Layer
│   ├── sample_docs/                      # General electronics documentation (ESP32, SMPS, Op-Amps, MOSFETs)
│   └── vector_store/                     # Persistent Vector Database store
│
├── notebooks/                            # Interactive Research & Walkthrough
│   └── electronics_rag_pipeline_walkthrough.ipynb
│
├── src/
│   ├── domain/                           # Enterprise Domain Layer (Pure Entities & Interfaces)
│   │   ├── __init__.py
│   │   ├── entities.py                   # Document, Chunk, KnowledgeQuery, RetrievalResult, Categories
│   │   └── interfaces.py                 # VectorStore, EmbeddingModel, Loader, Splitter, Classifier contracts
│   │
│   ├── application/                      # Use Cases & Orchestration Layer
│   │   ├── __init__.py
│   │   ├── ingestion.py                  # IngestDocumentsUseCase
│   │   ├── retrieval.py                  # RetrieveKnowledgeUseCase
│   │   └── mcp_service.py                # MCP Application Service & Diagnostics
│   │
│   ├── infrastructure/                   # External Frameworks & Adapters
│   │   ├── __init__.py
│   │   ├── config.py                     # Pydantic environment configuration
│   │   ├── classifier.py                 # Rule/Keyword electronics domain classifier
│   │   ├── loaders.py                    # Universal loader (Markdown, Text, PDF, JSON)
│   │   ├── splitters.py                  # Clean recursive text splitter with overlap
│   │   ├── embeddings.py                 # Sentence-transformers with hashing fallback
│   │   └── vector_store.py               # ChromaDB / persistent vector storage adapter
│   │
│   └── presentation/                     # Delivery Mechanisms & User Interfaces
│       ├── __init__.py
│       ├── mcp_server.py                 # Standard JSON-RPC stdio Model Context Protocol Server
│       ├── cli.py                        # Command Line Interface (ingest, query, serve, stats)
│       └── ui/
│           ├── __init__.py
│           └── app.py                    # Streamlit MCP Setup & Connection Portal (No Chatbot)
│
├── tests/                                # Automated Test Suite
│   ├── __init__.py
│   └── test_pipeline.py
│
├── .env.example                          # Environment template
├── requirements.txt                      # Project dependencies
└── README.md                             # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Ingest Sample Electronics Documents
Run the ingestion pipeline via the CLI:
```bash
python src/presentation/cli.py ingest
```

### 3. Query the Electronics Knowledge Base
```bash
python src/presentation/cli.py query "How do I calculate the inductor for a buck converter?"
```

### 4. Launch the MCP Setup & Connection UI
To configure parameters, test server connection, and inspect tool schemas:
```bash
streamlit run src/presentation/ui/app.py
```
> **Note**: As specified in the architecture, the UI is dedicated exclusively to **MCP server configuration, access settings, connection testing, and tool dry-run inspection** (no chatbot interface).

### 5. Launch the Jupyter Notebook Walkthrough
Open and execute the end-to-end walkthrough:
```bash
jupyter notebook notebooks/electronics_rag_pipeline_walkthrough.ipynb
```

---

## ⚡ Connecting AI Agents via MCP (Model Context Protocol)

The Python MCP server (`src/presentation/mcp_server.py`) can be integrated into any MCP-compatible AI agent or client (Claude Desktop, Cursor IDE, Antigravity CLI, or custom autonomous agents).

### Claude Desktop Configuration (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "electronics-rag": {
      "command": "python",
      "args": ["P:/rag pipline EA/src/presentation/mcp_server.py"],
      "env": {
        "PYTHONPATH": "P:/rag pipline EA"
      }
    }
  }
}
```

### Registered MCP Tools
| MCP Tool Name | Description | Key Inputs |
| :--- | :--- | :--- |
| `query_electronics_knowledge` | Retrieves technical electronics documentation, calculations, pinouts, and circuits with sources. | `query` (str), `category` (optional), `top_k` (int) |
| `list_electronics_categories` | Lists all knowledge categories and vector database statistics. | none |
| `get_system_health` | Returns health status of vector database, embeddings, and server runtime. | none |
| `trigger_ingestion_pipeline` | Triggers document ingestion and indexing on the sample docs directory. | `source_directory` (optional) |

---

## 🧪 Running Unit Tests
```bash
pytest tests/
```
