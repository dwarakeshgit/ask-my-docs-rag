from typing import List, Dict, Any

from backend.app.retrieval.bm25_retriever import BM25Retriever
from backend.app.retrieval.vector_retriever import VectorRetriever


class HybridRetriever:
    """
    Combines BM25 keyword retrieval and vector semantic retrieval
    using Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        vector_retriever: VectorRetriever,
        rrf_k: int = 60,
    ):
        self.bm25_retriever = bm25_retriever
        self.vector_retriever = vector_retriever
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        top_k: int = 5,
        retrieval_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Perform BM25 and vector retrieval, then combine
        their rankings using Reciprocal Rank Fusion.
        """

        bm25_results = self.bm25_retriever.search(
            query=query,
            top_k=retrieval_k,
        )

        vector_results = self.vector_retriever.search(
            query=query,
            top_k=retrieval_k,
        )

        combined = {}

        # Add BM25 ranking contribution
        for rank, result in enumerate(bm25_results, start=1):

            chunk_id = self._get_chunk_id(result)

            if chunk_id is None:
                continue

            if chunk_id not in combined:
                combined[chunk_id] = {
                    **result,
                    "rrf_score": 0.0,
                    "bm25_rank": None,
                    "vector_rank": None,
                }

            combined[chunk_id]["rrf_score"] += (
                1 / (self.rrf_k + rank)
            )

            combined[chunk_id]["bm25_rank"] = rank

        # Add vector ranking contribution
        for rank, result in enumerate(vector_results, start=1):

            chunk_id = self._get_chunk_id(result)

            if chunk_id is None:
                continue

            if chunk_id not in combined:
                combined[chunk_id] = {
                    **result,
                    "rrf_score": 0.0,
                    "bm25_rank": None,
                    "vector_rank": None,
                }

            combined[chunk_id]["rrf_score"] += (
                1 / (self.rrf_k + rank)
            )

            combined[chunk_id]["vector_rank"] = rank

        # Sort by combined RRF score
        ranked_results = sorted(
            combined.values(),
            key=lambda result: result["rrf_score"],
            reverse=True,
        )

        return ranked_results[:top_k]

    @staticmethod
    def _get_chunk_id(result: Dict[str, Any]):
        """
        Get a consistent chunk identifier from a retrieval result.
        """

        if result.get("chunk_id") is not None:
            return str(result["chunk_id"])

        metadata = result.get("metadata", {})

        if metadata.get("chunk_id") is not None:
            return str(metadata["chunk_id"])

        return None