from pathlib import Path
from typing import List

from backend.app.ingestion.pdf_reader import read_pdf
from backend.app.ingestion.models import DocumentChunk
from backend.app.chunking.chunker import chunk_document_pages
from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore


class DocumentIndexer:
    """
    Converts documents into searchable chunks
    and stores their embeddings in ChromaDB.
    """

    def __init__(
        self,
        embedder: Embedder,
        vector_store: ChromaVectorStore,
    ):

        self.embedder = embedder

        self.vector_store = vector_store

    def index_pdf(
        self,
        file_path: str,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> List[DocumentChunk]:
        """
        Read a PDF, create chunks, generate embeddings,
        and store the chunks in ChromaDB.
        """

        # ---------------------------------------------
        # 1. Read PDF
        # ---------------------------------------------

        pages = read_pdf(file_path)

        if not pages:
            return []

        # ---------------------------------------------
        # 2. Create document chunks
        # ---------------------------------------------

        chunks = chunk_document_pages(
            pages,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        if not chunks:
            return []

        # ---------------------------------------------
        # 3. Extract chunk text
        # ---------------------------------------------

        texts = [
            chunk.text
            for chunk in chunks
        ]

        # ---------------------------------------------
        # 4. Generate embeddings
        # ---------------------------------------------

        embeddings = self.embedder.embed_texts(
            texts
        )

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Number of embeddings does not match "
                "number of chunks."
            )

        # ---------------------------------------------
        # 5. Prepare ChromaDB data
        # ---------------------------------------------

        ids = [
            chunk.chunk_id
            for chunk in chunks
        ]

        metadatas = []

        for chunk in chunks:

            metadata = {
                **chunk.metadata,
                "source": chunk.source,
                "file_type": chunk.file_type,
                "page_number": chunk.page_number,
            }

            metadatas.append(metadata)

        # ---------------------------------------------
        # 6. Store in ChromaDB
        # ---------------------------------------------

        self.vector_store.add_documents(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return chunks