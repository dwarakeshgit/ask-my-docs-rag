from backend.app.ingestion.models import DocumentChunk
from backend.app.retrieval.bm25_index import BM25Index


def main():

    print("=" * 60)
    print("BM25 INDEX TEST")
    print("=" * 60)

    chunks = [

        DocumentChunk(
            chunk_id="chunk_1",
            text=(
                "Artificial Intelligence is a field of "
                "computer science."
            ),
            source="sample data.pdf",
            file_type="pdf",
            page_number=1,
            metadata={
                "filename": "sample data.pdf",
                "page": 1,
            },
        ),

        DocumentChunk(
            chunk_id="chunk_2",
            text=(
                "Machine Learning allows computers to "
                "learn patterns from data."
            ),
            source="sample data.pdf",
            file_type="pdf",
            page_number=1,
            metadata={
                "filename": "sample data.pdf",
                "page": 1,
            },
        ),

        DocumentChunk(
            chunk_id="chunk_3",
            text=(
                "Deep Learning uses neural networks "
                "with multiple layers."
            ),
            source="sample data.pdf",
            file_type="pdf",
            page_number=1,
            metadata={
                "filename": "sample data.pdf",
                "page": 1,
            },
        ),
    ]

    index = BM25Index()

    index.add_chunks(chunks)

    print(f"\nChunks indexed: {index.count()}")

    query = "machine learning"

    results = index.search(
        query=query,
        top_k=3,
    )

    print(f"\nQuery: {query}")

    print("\nBM25 Results:")

    for rank, result in enumerate(results, start=1):

        print("-" * 60)

        print(f"Rank: {rank}")

        print(f"Chunk ID: {result['chunk_id']}")

        print(f"Score: {result['bm25_score']}")

        print(f"Text: {result['text']}")

        print(f"Source: {result['source']}")

        print(f"Page: {result['page_number']}")

    print("\n" + "=" * 60)
    print("BM25 INDEX TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()