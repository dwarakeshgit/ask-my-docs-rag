from typing import List

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


class Embedder:
    """
    Converts text into semantic vector embeddings.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding for a single piece of text.
        """

        if not text or not text.strip():
            return []

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        """

        valid_texts = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

        if not valid_texts:
            return []

        embeddings = self.model.encode(
            valid_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()