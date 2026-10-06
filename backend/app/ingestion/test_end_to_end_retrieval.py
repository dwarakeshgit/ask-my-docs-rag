from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.ingestion.indexing_pipeline import IndexingPipeline
from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore
from backend.app.retrieval.bm25_index import BM25Index
from backend.app.retrieval.vector_retriever import VectorRetriever
from backend.app.retrieval.retrieval_pipeline import RetrievalPipeline
from backend.app.reranking.reranker import CrossEncoderReranker


def main():
    file_path = "backend/app/ingestion/data/sample data.pdf"

    print("=" * 60)
    print("END-TO-END REAL DOCUMENT RETRIEVAL TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Create ingestion components
    # ---------------------------------------------------------

    ingestion_pipeline = IngestionPipeline()

    embedder = Embedder()

    vector_store = ChromaVectorStore(
        persist_directory="backend/data/chroma_end_to_end_test",
        collection_name="end_to_end_retrieval_test",
    )

    bm25_index = BM25Index()

    # ---------------------------------------------------------
    # 2. Create indexing pipeline
    # ---------------------------------------------------------

    indexing_pipeline = IndexingPipeline(
        ingestion_pipeline=ingestion_pipeline,
        embedder=embedder,
        vector_store=vector_store,
        bm25_index=bm25_index,
    )

    print("\nIndexing real PDF...")

    chunks = indexing_pipeline.index_document(file_path)

    print(f"Chunks indexed: {len(chunks)}")
    print(f"Chroma count: {vector_store.count()}")
    print(f"BM25 count: {bm25_index.count()}")

    # ---------------------------------------------------------
    # 3. Create retrieval components
    # ---------------------------------------------------------

    vector_retriever = VectorRetriever(
        embedder=embedder,
        vector_store=vector_store,
    )

    reranker = CrossEncoderReranker()

    retrieval_pipeline = RetrievalPipeline(
        bm25_index=bm25_index,
        vector_retriever=vector_retriever,
        reranker=reranker,
    )

    # ---------------------------------------------------------
    # 4. Ask a question about the real document
    # ---------------------------------------------------------

    query = "What is artificial intelligence?"

    print("\n" + "=" * 60)
    print(f"QUERY: {query}")
    print("=" * 60)

    results = retrieval_pipeline.search(
        query=query,
        retrieval_k=10,
        top_k=3,
    )

    # ---------------------------------------------------------
    # 5. Display final evidence
    # ---------------------------------------------------------

    print("\nFINAL RETRIEVED EVIDENCE:")

    for rank, result in enumerate(results, start=1):
        print("\n" + "-" * 60)
        print(f"Rank: {rank}")
        print(f"Chunk ID: {result.get('chunk_id')}")
        print(f"Reranker Score: {result.get('reranker_score')}")
        print(f"RRF Score: {result.get('rrf_score')}")
        print(f"BM25 Rank: {result.get('bm25_rank')}")
        print(f"Vector Rank: {result.get('vector_rank')}")
        print(f"Source: {result.get('source')}")
        print(f"Page: {result.get('page_number')}")
        print(f"Text: {result.get('text', '')[:500]}")

    print("\n" + "=" * 60)
    print("END-TO-END RETRIEVAL TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()