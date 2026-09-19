"""
Document Cleaners and Splitters.
Cleans raw electronics documents, splits them intelligently with overlap, and attaches classifications.
"""
import re
from typing import List, Optional
from src.domain.entities import Document, Chunk, ClassificationCategory
from src.domain.interfaces import DocumentSplitterInterface, ClassifierInterface
from src.infrastructure.classifier import ElectronicsDomainClassifier


class CleanElectronicsSplitter(DocumentSplitterInterface):
    """
    Cleans raw electronics documentation (markdown tables, schematics, pinout notations)
    and splits into context-aware chunks with category tagging.
    """

    def __init__(
        self,
        chunk_size: int = 600,
        chunk_overlap: int = 120,
        classifier: Optional[ClassifierInterface] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.classifier = classifier or ElectronicsDomainClassifier()

    def clean_text(self, text: str) -> str:
        """Sanitizes text, removing excessive whitespace while preserving code/diagram structures."""
        # Replace non-breaking spaces
        cleaned = text.replace("\xa0", " ")
        # Replace multiple horizontal spaces with single space
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        # Normalize newline characters
        cleaned = re.sub(r"\r\n", "\n", cleaned)
        # Replace 3 or more consecutive newlines with 2
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def split_document(self, document: Document) -> List[Chunk]:
        """Splits a single document into cleaned, classified chunks."""
        cleaned_full_text = self.clean_text(document.content)
        raw_chunks = self._recursive_split(cleaned_full_text, self.chunk_size, self.chunk_overlap)
        
        chunks: List[Chunk] = []
        for idx, chunk_text in enumerate(raw_chunks):
            if not chunk_text.strip():
                continue
            
            category, confidence, tags = self.classifier.classify(chunk_text)
            
            chunk = Chunk(
                document_id=document.id,
                source_title=document.title,
                source_path=document.source_path,
                chunk_index=idx,
                content=chunk_text,
                clean_content=chunk_text.strip(),
                category=category,
                confidence=confidence,
                tags=tags,
                metadata={
                    "file_type": document.file_type,
                    "chunk_size_chars": len(chunk_text),
                    **document.metadata
                }
            )
            chunks.append(chunk)

        return chunks

    def split_documents(self, documents: List[Document]) -> List[Chunk]:
        """Splits multiple documents."""
        all_chunks: List[Chunk] = []
        for doc in documents:
            all_chunks.extend(self.split_document(doc))
        return all_chunks

    def _recursive_split(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Splits text hierarchically by Markdown sections, paragraphs, sentences."""
        separators = ["\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". ", " "]
        
        def _split_with_separators(txt: str, sep_index: int) -> List[str]:
            if len(txt) <= chunk_size or sep_index >= len(separators):
                return [txt] if txt else []
            
            sep = separators[sep_index]
            splits = txt.split(sep)
            result = []
            current_piece = ""

            for piece in splits:
                piece_to_add = (sep if current_piece else "") + piece
                if len(current_piece) + len(piece_to_add) <= chunk_size:
                    current_piece += piece_to_add
                else:
                    if current_piece:
                        result.append(current_piece)
                    if len(piece) > chunk_size:
                        # Sub-split larger pieces with next separator
                        sub_pieces = _split_with_separators(piece, sep_index + 1)
                        result.extend(sub_pieces)
                        current_piece = ""
                    else:
                        current_piece = piece

            if current_piece:
                result.append(current_piece)
            return result

        raw_pieces = _split_with_separators(text, 0)
        
        # Merge overlapping chunks if desired
        if overlap <= 0 or len(raw_pieces) <= 1:
            return [p.strip() for p in raw_pieces if p.strip()]

        final_chunks = []
        for i, piece in enumerate(raw_pieces):
            if i > 0 and overlap > 0:
                # Add overlap suffix from previous chunk
                prev_overlap = raw_pieces[i-1][-overlap:] if len(raw_pieces[i-1]) > overlap else raw_pieces[i-1]
                combined = f"{prev_overlap}... {piece}".strip()
            else:
                combined = piece.strip()
            if combined:
                final_chunks.append(combined)

        return final_chunks
