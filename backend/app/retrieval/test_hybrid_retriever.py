from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore

from backend.app.retrieval.bm25_retriever import BM25Retriever
from backend.app.retrieval.vector_retriever import VectorRetriever
from backend.app.retrieval.hybrid_retriever import HybridRetriever


def main():

    print("=" * 60)
    print("HYBRID RETRIEVAL TEST")
    print("=" * 60)

    documents = [
        {
            "chunk_id": "test_chunk_1",
            "text": (
                "Artificial Intelligence is a field of computer science."
            ),
            "source": "sample data.pdf",
            "page_number": 1,
            "metadata": {
                "filename": "sample data.pdf",
                "page": 1,
                "chunk_index": 0,
            },
        },
        {
            "chunk_id": "test_chunk_2",
            "text": (
                "Machine Learning allows computers to learn "
                "patterns from data."
            ),
            "source": "sample data.pdf",
            "page_number": 1,
            "metadata": {
                "filename": "sample data.pdf",
                "page": 1,
                "chunk_index": 1,
            },
        },
        {
            "chunk_id": "test_chunk_3",
            "text": (
                "Deep Learning uses neural networks with "
                "multiple layers."
            ),
            "source": "sample data.pdf",
            "page_number": 1,
            "metadata": {
                "filename": "sample data.pdf",
                "page": 1,
                "chunk_index": 2,
            },
        },
    ]

    # BM25 retriever
    bm25_retriever = BM25Retriever(documents)

    # Vector components
    embedder = Embedder()
    vector_store = ChromaVectorStore()

    vector_retriever = VectorRetriever(
        embedder=embedder,
        vector_store=vector_store,
    )

    # Hybrid retriever
    hybrid_retriever = HybridRetriever(
        bm25_retriever=bm25_retriever,
        vector_retriever=vector_retriever,
    )

    query = "What is machine learning?"

    results = hybrid_retriever.search(
        query=query,
        top_k=3,
    )

    print(f"\nQuery: {query}")
    print("\nHybrid Results:")

    for index, result in enumerate(results, start=1):

        print("-" * 60)
        print(f"Result {index}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Text: {result['text']}")
        print(f"BM25 Rank: {result['bm25_rank']}")
        print(f"Vector Rank: {result['vector_rank']}")
        print(f"RRF Score: {result['rrf_score']}")
        print(f"Metadata: {result['metadata']}")

    print("\n" + "=" * 60)
    print("HYBRID RETRIEVAL TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()