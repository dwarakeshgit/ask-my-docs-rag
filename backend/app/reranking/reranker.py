from typing import List, Dict, Any

from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker:
    """
    Reranks retrieved document chunks using a Cross-Encoder model.
    """

    def __init__(self, model_name: str = MODEL_NAME):

        self.model_name = model_name

        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Score each document against the query and
        return documents ordered by relevance.
        """

        if not query or not query.strip():
            return []

        if not documents:
            return []

        pairs = [
            [query, document["text"]]
            for document in documents
        ]

        scores = self.model.predict(pairs)

        reranked_documents = []

        for document, score in zip(documents, scores):

            result = document.copy()

            result["reranker_score"] = float(score)

            reranked_documents.append(result)

        reranked_documents.sort(
            key=lambda document: document["reranker_score"],
            reverse=True,
        )

        return reranked_documents[:top_k]