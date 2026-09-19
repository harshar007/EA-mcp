"""
MCP Connection & Setup UI.
Clean Architecture - Presentation Layer.
Design Rule: UI is used for MCP setup and tool diagnostic inspection only (No chatbot interface).
"""
import sys
import os
import json
import subprocess
from pathlib import Path
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.infrastructure.config import settings
from src.application.mcp_service import MCPService
from src.application.ingestion import IngestDocumentsUseCase
from src.domain.entities import ClassificationCategory

# Configure Page
st.set_page_config(
    page_title="MCP Setup & Connection Manager | Electronics RAG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 14px;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .status-card {
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        background-color: #F9FAFB;
        margin-bottom: 12px;
    }
    .code-box {
        background-color: #111827;
        color: #10B981;
        padding: 12px;
        border-radius: 6px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Service Initialization
@st.cache_resource
def get_service():
    return MCPService()

mcp_service = get_service()

# Header
st.markdown('<div class="main-header">⚡ Electronics RAG — Model Context Protocol (MCP) Setup Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Administrative Interface for MCP Server Configuration, Connection Testing, and Tool Inspection. (MCP Setup Only &bull; No Chatbot)</div>', unsafe_allow_html=True)

st.divider()

# Sidebar: Environment & Server Status
with st.sidebar:
    st.header("⚙️ Server Diagnostics")
    health = mcp_service.get_health()
    
    st.metric("Vector DB Chunks", health.get("total_indexed_chunks", 0))
    st.metric("Vector Store Backend", health.get("vector_store_backend", "N/A"))
    st.metric("Embedding Model", health.get("embedding_model", "N/A"))
    
    st.divider()
    st.subheader("📚 Quick Ingestion")
    if st.button("🔄 Ingest / Re-index Sample Docs", use_container_width=True):
        with st.spinner("Processing documents, generating embeddings & updating vector DB..."):
            result = mcp_service.run_ingestion()
            st.success(f"Indexed {result.get('chunks_indexed', 0)} chunks from {result.get('documents_loaded', 0)} documents!")
            st.rerun()

# Layout: 3 Tabs (1. Connection & Settings, 2. Test Connection & Tools, 3. Client Export Configs)
tab1, tab2, tab3 = st.tabs([
    "🔧 1. Enter MCP Server & Configure Access",
    "🧪 2. Test Connection & List Tools",
    "📋 3. Export MCP Client Configurations"
])

with tab1:
    st.subheader("MCP Server Connection Settings")
    st.caption("Configure how external AI agents (Claude, Cursor, Antigravity, Custom Agents) connect to this Electronics RAG server.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        server_name = st.text_input("MCP Server Identifier", value=settings.MCP_SERVER_NAME)
        transport_type = st.selectbox("Transport Protocol", ["stdio", "sse"], index=0 if settings.MCP_TRANSPORT == "stdio" else 1)
        command_executable = st.text_input("Python Executable / Command", value=sys.executable)
        server_script_path = st.text_input("MCP Server Script Path", value=str(PROJECT_ROOT / "src" / "presentation" / "mcp_server.py"))
        
    with col2:
        vector_path = st.text_input("Vector Database Path", value=str(settings.VECTOR_DB_PATH))
        collection_name = st.text_input("Collection Name", value=settings.VECTOR_COLLECTION_NAME)
        embedding_model = st.text_input("Embedding Model", value=settings.EMBEDDING_MODEL_NAME)
        top_k_default = st.slider("Default Top-K Retrieved Chunks", min_value=1, max_value=10, value=4)

    st.markdown("#### Configured Execution Command")
    full_cmd = f'"{command_executable}" "{server_script_path}"'
    st.code(full_cmd, language="bash")

with tab2:
    st.subheader("Test Connection & Inspect Registered MCP Tools")
    st.caption("Verify that the MCP server responds to standard protocol requests and execute dry-run tool calls.")
    
    col_t1, col_t2 = st.columns([1, 2])
    
    with col_t1:
        if st.button("🚀 Ping Server & List Tools", type="primary", use_container_width=True):
            st.session_state["tools_listed"] = True
            
        tools = mcp_service.get_registered_tools()
        st.write(f"**Discovered Tools ({len(tools)}):**")
        selected_tool_name = st.selectbox(
            "Select Tool to Inspect / Test",
            options=[t.name for t in tools]
        )
        
    with col_t2:
        selected_tool = next((t for t in tools if t.name == selected_tool_name), None)
        if selected_tool:
            st.markdown(f"### Tool: `{selected_tool.name}`")
            st.info(selected_tool.description)
            
            with st.expander("📄 JSON Schema (Input Schema)", expanded=True):
                st.json(selected_tool.input_schema)
                
            st.markdown("#### ⚡ Dry-Run Tool Execution")
            
            if selected_tool.name == "query_electronics_knowledge":
                q_input = st.text_input("Query", value="How do I calculate the inductor for a buck converter?")
                cat_input = st.selectbox(
                    "Category Filter (Optional)",
                    ["None"] + [c.value for c in ClassificationCategory]
                )
                top_k_input = st.number_input("Top K", min_value=1, max_value=10, value=3)
                
                if st.button("Execute query_electronics_knowledge", use_container_width=True):
                    category_param = None if cat_input == "None" else cat_input
                    with st.spinner("Retrieving from Vector Database..."):
                        res = mcp_service.query_electronics(query=q_input, category=category_param, top_k=top_k_input)
                        st.success(f"Retrieved {res.get('results_count', 0)} sources!")
                        st.json(res)
                        
            elif selected_tool.name == "list_electronics_categories":
                if st.button("Execute list_electronics_categories", use_container_width=True):
                    res = mcp_service.list_categories()
                    st.json(res)
                    
            elif selected_tool.name == "get_system_health":
                if st.button("Execute get_system_health", use_container_width=True):
                    res = mcp_service.get_health()
                    st.json(res)
                    
            elif selected_tool.name == "trigger_ingestion_pipeline":
                if st.button("Execute trigger_ingestion_pipeline", use_container_width=True):
                    with st.spinner("Ingesting documents..."):
                        res = mcp_service.run_ingestion()
                        st.json(res)

with tab3:
    st.subheader("Client MCP Configuration Snippets")
    st.caption("Paste these JSON snippets into your AI Agent or IDE MCP configuration file.")
    
    # Generate JSON configurations for Claude Desktop & Antigravity
    config_dict = {
        "mcpServers": {
            "electronics-rag": {
                "command": command_executable,
                "args": [server_script_path],
                "env": {
                    "PYTHONPATH": str(PROJECT_ROOT),
                    "VECTOR_DB_PATH": str(settings.VECTOR_DB_PATH)
                }
            }
        }
    }
    
    st.markdown("##### 1. Claude Desktop Config (`claude_desktop_config.json`)")
    st.json(config_dict)
    
    st.markdown("##### 2. Cursor IDE Config (`.cursor/mcp.json`)")
    cursor_config = {
        "mcpServers": {
            "electronics-rag": {
                "command": command_executable,
                "args": [server_script_path]
            }
        }
    }
    st.json(cursor_config)
    
    st.markdown("##### 3. Antigravity / Agent CLI Config (`mcp_config.json`)")
    st.code(json.dumps(config_dict, indent=2), language="json")
