from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore


def main():

    print("=" * 60)
    print("VECTOR STORE TEST")
    print("=" * 60)

    embedder = Embedder()
    store = ChromaVectorStore()

    documents = [
        "Artificial Intelligence is a field of computer science.",
        "Machine Learning allows computers to learn patterns from data.",
        "Deep Learning uses neural networks with multiple layers.",
    ]

    ids = [
        "test_chunk_1",
        "test_chunk_2",
        "test_chunk_3",
    ]

    metadatas = [
        {
            "filename": "sample data.pdf",
            "page": 1,
            "chunk_index": 0,
        },
        {
            "filename": "sample data.pdf",
            "page": 1,
            "chunk_index": 1,
        },
        {
            "filename": "sample data.pdf",
            "page": 1,
            "chunk_index": 2,
        },
    ]

    embeddings = embedder.embed_texts(documents)

    store.add_documents(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"\nStored chunks: {store.count()}")

    query = "What is machine learning?"

    query_embedding = embedder.embed_text(query)

    results = store.search(
        query_embedding=query_embedding,
        top_k=2,
    )

    print(f"\nQuery: {query}")
    print("\nSearch Results:")

    for i, document in enumerate(results["documents"][0]):

        print("-" * 60)
        print(f"Result {i + 1}")
        print(f"Text: {document}")
        print(f"Metadata: {results['metadatas'][0][i]}")
        print(f"Distance: {results['distances'][0][i]}")

    print("\n" + "=" * 60)
    print("VECTOR STORE TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()