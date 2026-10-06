from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def create_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
    )

    return embeddings.tolist()