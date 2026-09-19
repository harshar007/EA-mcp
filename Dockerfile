# ==========================================
# ⚡ Electronics RAG & MCP Server Dockerfile
# ==========================================
FROM python:3.11-slim AS base

# System environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and data
COPY src/ /app/src/
COPY data/ /app/data/
COPY notebooks/ /app/notebooks/
COPY tests/ /app/tests/
COPY .env.example /app/.env

# Create non-root user for security best practices
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data/vector_store /app/data/sample_docs && \
    chown -R appuser:appuser /app

USER appuser

# Expose ports:
# - 8501: Streamlit MCP Setup UI
# - 8000: MCP Server (HTTP/SSE transport mode)
# - 8888: Jupyter Notebook
EXPOSE 8501 8000 8888

# Health check for the Web UI
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default Command: Launch MCP Setup Portal
CMD ["streamlit", "run", "src/presentation/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
