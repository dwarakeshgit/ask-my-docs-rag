from typing import List, Dict, Any

from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore


class VectorRetriever:
    """
    Semantic retrieval using embeddings and ChromaDB.
    """

    def __init__(
        self,
        embedder: Embedder,
        vector_store: ChromaVectorStore,
    ):
        self.embedder = embedder
        self.vector_store = vector_store

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Convert the query into an embedding and retrieve
        the most semantically similar document chunks.
        """

        query_embedding = self.embedder.embed_text(query)

        if not query_embedding:
            return []

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        retrieved_documents = []

        for index, document in enumerate(documents):

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            document_id = (
                ids[index]
                if index < len(ids)
                else None
            )

            retrieved_documents.append(
                {
                    "chunk_id": document_id,
                    "text": document,
                    "metadata": metadata,
                    "vector_distance": distance,
                }
            )

        return retrieved_documents