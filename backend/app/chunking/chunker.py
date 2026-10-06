from typing import List

from backend.app.ingestion.models import (
    DocumentPage,
    DocumentChunk,
)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> List[str]:
    """
    Split text into overlapping chunks.
    """

    if not text or not text.strip():
        return []

    text = text.strip()

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - chunk_overlap

    return chunks


def chunk_document_pages(
    pages: List[DocumentPage],
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> List[DocumentChunk]:
    """
    Convert document pages into structured DocumentChunk objects
    while preserving source and citation metadata.
    """

    chunks = []

    chunk_counter = 0

    for page in pages:

        page_chunks = chunk_text(
            page.text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for chunk_index, text in enumerate(page_chunks):

            chunk_counter += 1

            chunk = DocumentChunk(
                chunk_id=f"{page.metadata.get('filename', 'document')}"
                f"_page_{page.page_number}"
                f"_chunk_{chunk_counter}",

                text=text,

                source=page.source,

                file_type=page.file_type,

                page_number=page.page_number,

                metadata={
                    **page.metadata,
                    "chunk_index": chunk_index,
                },
            )

            chunks.append(chunk)

    return chunks