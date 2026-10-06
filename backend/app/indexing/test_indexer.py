from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore
from backend.app.indexing.indexer import DocumentIndexer


PDF_PATH = "backend/app/ingestion/data/sample data.pdf"


def main():

    print("=" * 60)
    print("DOCUMENT INDEXING TEST")
    print("=" * 60)

    print("\nInitializing embedding model...")

    embedder = Embedder()

    print("Initializing ChromaDB...")

    vector_store = ChromaVectorStore()

    print("\nCreating document indexer...")

    indexer = DocumentIndexer(
        embedder=embedder,
        vector_store=vector_store,
    )

    print(f"\nIndexing PDF:")
    print(PDF_PATH)

    chunks = indexer.index_pdf(
        file_path=PDF_PATH,
        chunk_size=200,
        chunk_overlap=50,
    )

    print("\nIndexing completed!")

    print(f"\nChunks indexed: {len(chunks)}")

    print(
        f"Total chunks in ChromaDB: "
        f"{vector_store.count()}"
    )

    for chunk in chunks:

        print("-" * 60)

        print(f"Chunk ID: {chunk.chunk_id}")

        print(f"Page: {chunk.page_number}")

        print(f"Text: {chunk.text}")

        print(f"Metadata: {chunk.metadata}")

    print("\n" + "=" * 60)
    print("DOCUMENT INDEXING TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()