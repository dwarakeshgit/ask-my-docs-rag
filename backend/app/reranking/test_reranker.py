from backend.app.reranking.reranker import CrossEncoderReranker


def main():

    print("=" * 60)
    print("CROSS-ENCODER RERANKER TEST")
    print("=" * 60)

    documents = [
        {
            "chunk_id": "chunk_1",
            "text": (
                "Artificial Intelligence is a field of "
                "computer science."
            ),
            "metadata": {
                "filename": "sample data.pdf",
                "page": 1,
            },
        },
        {
            "chunk_id": "chunk_2",
            "text": (
                "Machine Learning is a subset of Artificial "
                "Intelligence that allows computers to learn "
                "patterns from data."
            ),
            "metadata": {
                "filename": "sample data.pdf",
                "page": 1,
            },
        },
        {
            "chunk_id": "chunk_3",
            "text": (
                "Deep Learning uses neural networks with "
                "multiple layers."
            ),
            "metadata": {
                "filename": "sample data.pdf",
                "page": 1,
            },
        },
    ]

    query = "What is machine learning?"

    print(f"\nQuery: {query}")

    print("\nLoading Cross-Encoder model...")

    reranker = CrossEncoderReranker()

    print(f"Model: {reranker.model_name}")

    results = reranker.rerank(
        query=query,
        documents=documents,
        top_k=3,
    )

    print("\nReranked Results:")

    for index, result in enumerate(results, start=1):

        print("-" * 60)
        print(f"Rank: {index}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Score: {result['reranker_score']}")
        print(f"Text: {result['text']}")
        print(f"Metadata: {result['metadata']}")

    print("\n" + "=" * 60)
    print("CROSS-ENCODER RERANKER TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()