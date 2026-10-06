from typing import List

from backend.app.ingestion.models import DocumentChunk
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore
from backend.app.retrieval.bm25_index import BM25Index


class IndexingPipeline:
    """
    Converts documents into searchable data for both
    BM25 and vector retrieval.
    """

    def __init__(
        self,
        ingestion_pipeline: IngestionPipeline,
        embedder: Embedder,
        vector_store: ChromaVectorStore,
        bm25_index: BM25Index,
    ):
        self.ingestion_pipeline = ingestion_pipeline
        self.embedder = embedder
        self.vector_store = vector_store
        self.bm25_index = bm25_index

    def index_document(self, file_path: str) -> List[DocumentChunk]:
        """
        Read, clean, chunk, embed, and index one document.
        """

        # Step 1: Convert the file into DocumentChunk objects
        chunks = self.ingestion_pipeline.process_document(file_path)

        if not chunks:
            return []

        # Step 2: Extract chunk text
        texts = [chunk.text for chunk in chunks]

        # Step 3: Create embeddings for every chunk
        embeddings = self.embedder.embed_texts(texts)

        # Step 4: Prepare IDs and metadata for ChromaDB
        ids = [chunk.chunk_id for chunk in chunks]

        metadatas = []

        for chunk in chunks:
            metadata = dict(chunk.metadata)

            metadata.update(
                {
                    "source": chunk.source,
                    "file_type": chunk.file_type,
                    "page_number": chunk.page_number,
                }
            )

            metadatas.append(metadata)

        # Step 5: Store chunks in ChromaDB
        self.vector_store.add_documents(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        # Step 6: Add the same chunks to BM25
        self.bm25_index.add_chunks(chunks)

        return chunks