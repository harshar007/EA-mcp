"""
Document Loaders for Electronics Technical Documents.
Supports Markdown, Text, PDF, and JSON formats.
"""
import os
from pathlib import Path
from typing import List, Dict, Any
from src.domain.entities import Document
from src.domain.interfaces import DocumentLoaderInterface


class UniversalDocumentLoader(DocumentLoaderInterface):
    """Loads technical documents from files or directories."""

    SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf", ".json"}

    def load(self, source_path: str) -> List[Document]:
        """Loads all supported documents from path (file or folder)."""
        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {source_path}")

        if path.is_file():
            return [self._load_file(path)]
        elif path.is_dir():
            documents = []
            for file_path in path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    try:
                        doc = self._load_file(file_path)
                        documents.append(doc)
                    except Exception as e:
                        print(f"Warning: Failed to load {file_path}: {e}")
            return documents
        else:
            return []

    def _load_file(self, file_path: Path) -> Document:
        ext = file_path.suffix.lower()
        title = file_path.stem.replace("_", " ").replace("-", " ").title()

        if ext in {".txt", ".md", ".markdown"}:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return Document(
                title=title,
                source_path=str(file_path.resolve()),
                content=content,
                file_type=ext[1:],
                metadata={"filename": file_path.name, "file_size_bytes": file_path.stat().st_size}
            )

        elif ext == ".pdf":
            content = self._extract_pdf(file_path)
            return Document(
                title=title,
                source_path=str(file_path.resolve()),
                content=content,
                file_type="pdf",
                metadata={"filename": file_path.name, "file_size_bytes": file_path.stat().st_size}
            )

        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
            return Document(
                title=title,
                source_path=str(file_path.resolve()),
                content=raw_text,
                file_type="json",
                metadata={"filename": file_path.name, "file_size_bytes": file_path.stat().st_size}
            )

        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _extract_pdf(self, file_path: Path) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(f"--- Page {i+1} ---\n{text}")
            return "\n\n".join(pages_text)
        except ImportError:
            # Fallback when pypdf is not installed
            return f"[PDF content from {file_path.name} - install pypdf to extract full text]"
