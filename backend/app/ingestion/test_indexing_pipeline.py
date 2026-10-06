from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.ingestion.indexing_pipeline import IndexingPipeline
from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore
from backend.app.retrieval.bm25_index import BM25Index


def main():
    file_path = "backend/app/ingestion/data/sample data.pdf"

    ingestion_pipeline = IngestionPipeline()

    embedder = Embedder()

    vector_store = ChromaVectorStore(
        persist_directory="backend/data/chroma_indexing_test",
        collection_name="indexing_pipeline_test",
    )

    bm25_index = BM25Index()

    indexing_pipeline = IndexingPipeline(
        ingestion_pipeline=ingestion_pipeline,
        embedder=embedder,
        vector_store=vector_store,
        bm25_index=bm25_index,
    )

    chunks = indexing_pipeline.index_document(file_path)

    print("=" * 60)
    print("INDEXING PIPELINE TEST")
    print("=" * 60)

    print(f"\nChunks created: {len(chunks)}")
    print(f"Chroma documents: {vector_store.count()}")
    print(f"BM25 documents: {bm25_index.count()}")

    for chunk in chunks:
        print("\n" + "-" * 60)
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Source: {chunk.source}")
        print(f"Page: {chunk.page_number}")
        print(f"Text: {chunk.text[:200]}...")

    print("\n" + "=" * 60)
    print("INDEXING PIPELINE TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()