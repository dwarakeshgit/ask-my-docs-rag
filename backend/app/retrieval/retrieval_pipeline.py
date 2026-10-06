from typing import List, Dict, Any

from backend.app.retrieval.bm25_index import BM25Index
from backend.app.retrieval.vector_retriever import VectorRetriever
from backend.app.retrieval.hybrid_retriever import HybridRetriever
from backend.app.reranking.reranker import CrossEncoderReranker


class RetrievalPipeline:
    """
    Complete retrieval pipeline.

    Flow:

    Query
        ↓
    BM25 + Vector Search
        ↓
    Hybrid RRF Retrieval
        ↓
    Cross-Encoder Reranking
        ↓
    Reranker-Priority Final Ranking
        ↓
    Final Relevant Chunks
    """

    def __init__(
        self,
        bm25_index: BM25Index,
        vector_retriever: VectorRetriever,
        reranker: CrossEncoderReranker,
        rrf_k: int = 60,
    ):
        self.bm25_index = bm25_index
        self.vector_retriever = vector_retriever
        self.reranker = reranker
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        retrieval_k: int = 10,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval followed by cross-encoder reranking.

        Hybrid retrieval creates the candidate set.

        The cross-encoder then determines the final relevance
        ordering because it evaluates the relationship between
        the user's query and each retrieved document directly.
        """

        if not query or not query.strip():
            return []

        if self.bm25_index.retriever is None:
            return []

        hybrid_retriever = HybridRetriever(
            bm25_retriever=self.bm25_index.retriever,
            vector_retriever=self.vector_retriever,
            rrf_k=self.rrf_k,
        )

        hybrid_results = hybrid_retriever.search(
            query=query,
            top_k=retrieval_k,
            retrieval_k=retrieval_k,
        )

        if not hybrid_results:
            return []

        reranked_results = self.reranker.rerank(
            query=query,
            documents=hybrid_results,
            top_k=retrieval_k,
        )

        if not reranked_results:
            return []

        hybrid_rank_map = {}

        for rank, document in enumerate(
            hybrid_results,
            start=1,
        ):
            chunk_id = self._get_chunk_id(document)

            if chunk_id is not None:
                hybrid_rank_map[chunk_id] = rank

        reranker_rank_map = {}

        for rank, document in enumerate(
            reranked_results,
            start=1,
        ):
            chunk_id = self._get_chunk_id(document)

            if chunk_id is not None:
                reranker_rank_map[chunk_id] = rank

        final_results = []

        for document in reranked_results:
            chunk_id = self._get_chunk_id(document)

            hybrid_rank = hybrid_rank_map.get(chunk_id)
            reranker_rank = reranker_rank_map.get(chunk_id)

            hybrid_rrf_score = 0.0

            if hybrid_rank is not None:
                hybrid_rrf_score = 1 / (
                    self.rrf_k + hybrid_rank
                )

            result = document.copy()

            result["hybrid_rank"] = hybrid_rank
            result["reranker_rank"] = reranker_rank
            result["hybrid_rrf_score"] = hybrid_rrf_score

            final_results.append(result)

        final_results.sort(
            key=lambda document: (
                -document.get(
                    "reranker_score",
                    float("-inf"),
                ),
                document["hybrid_rank"]
                if document["hybrid_rank"] is not None
                else float("inf"),
            )
        )

        return final_results[:top_k]

    @staticmethod
    def _get_chunk_id(
        result: Dict[str, Any],
    ):
        if result.get("chunk_id") is not None:
            return str(result["chunk_id"])

        metadata = result.get("metadata", {})

        if metadata.get("chunk_id") is not None:
            return str(metadata["chunk_id"])

        return None