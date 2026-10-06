from backend.app.ingestion.models import DocumentChunk
from backend.app.retrieval.bm25_retriever import BM25Retriever


class BM25Index:
    def __init__(self):
        self.documents = {}
        self.retriever = None

    def add_chunks(self, chunks: list[DocumentChunk]):
        for chunk in chunks:
            self.documents[chunk.chunk_id] = {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "source": chunk.source,
                "file_type": chunk.file_type,
                "page_number": chunk.page_number,
                "metadata": chunk.metadata,
            }

        self._rebuild()

    def _rebuild(self):
        document_list = list(self.documents.values())

        if document_list:
            self.retriever = BM25Retriever(document_list)
        else:
            self.retriever = None

    def search(self, query: str, top_k: int = 5):
        if self.retriever is None:
            return []

        return self.retriever.search(
            query=query,
            top_k=top_k,
        )

    def count(self):
        return len(self.documents)