from typing import List, Dict, Any

from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    Keyword-based retrieval using the BM25 algorithm.
    """

    def __init__(self, documents: List[Dict[str, Any]]):
        self.documents = documents

        tokenized_documents = [
            self._tokenize(document["text"])
            for document in documents
        ]

        self.bm25 = BM25Okapi(tokenized_documents)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        Convert text into lowercase tokens.
        """

        return text.lower().split()

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search documents using BM25.
        """

        query_tokens = self._tokenize(query)

        scores = self.bm25.get_scores(query_tokens)

        ranked_indexes = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        results = []

        for index in ranked_indexes[:top_k]:

            result = self.documents[index].copy()

            result["bm25_score"] = float(scores[index])

            results.append(result)

        return results