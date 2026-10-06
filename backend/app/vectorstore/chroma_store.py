from typing import List, Dict, Any

import chromadb


class ChromaVectorStore:
    """
    Handles storing and searching document embeddings
    using ChromaDB.
    """

    def __init__(
        self,
        persist_directory: str = "backend/data/chroma",
        collection_name: str = "ask_my_docs",
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ):
        """
        Store document chunks, embeddings, and metadata.
        """

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Search for chunks most similar to the query embedding.
        """

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        return results

    def count(self) -> int:
        """
        Return the number of stored chunks.
        """

        return self.collection.count()