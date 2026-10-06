from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore
from backend.app.retrieval.vector_retriever import VectorRetriever


def main():

    print("=" * 60)
    print("VECTOR RETRIEVER TEST")
    print("=" * 60)

    embedder = Embedder()
    vector_store = ChromaVectorStore()

    retriever = VectorRetriever(
        embedder=embedder,
        vector_store=vector_store,
    )

    query = "What is machine learning?"

    results = retriever.search(
        query=query,
        top_k=2,
    )

    print(f"\nQuery: {query}")
    print("\nResults:")

    for index, result in enumerate(results, start=1):

        print("-" * 60)
        print(f"Result {index}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Text: {result['text']}")
        print(f"Vector Distance: {result['vector_distance']}")
        print(f"Metadata: {result['metadata']}")

    print("\n" + "=" * 60)
    print("VECTOR RETRIEVER TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()