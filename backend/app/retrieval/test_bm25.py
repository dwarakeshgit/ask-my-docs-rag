from backend.app.retrieval.bm25_retriever import BM25Retriever


def main():

    print("=" * 60)
    print("BM25 RETRIEVAL TEST")
    print("=" * 60)

    documents = [
        {
            "chunk_id": 1,
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
            "chunk_id": 2,
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
            "chunk_id": 3,
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

    retriever = BM25Retriever(documents)

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
        print(f"BM25 Score: {result['bm25_score']}")
        print(f"Metadata: {result['metadata']}")

    print("\n" + "=" * 60)
    print("BM25 RETRIEVAL TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()