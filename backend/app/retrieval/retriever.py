from backend.app.processing.embedder import create_embeddings
from backend.app.retrieval.vector_store import collection


def search_documents(
    query: str,
    top_k: int = 5,
):
    query_embedding = create_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    return results