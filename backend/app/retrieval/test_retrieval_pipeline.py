from backend.app.ingestion.models import DocumentChunk

from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore

from backend.app.retrieval.bm25_index import BM25Index
from backend.app.retrieval.vector_retriever import VectorRetriever
from backend.app.retrieval.retrieval_pipeline import RetrievalPipeline

from backend.app.reranking.reranker import CrossEncoderReranker


def main():

    print("=" * 70)
    print("TWO-DOCUMENT RETRIEVAL DIAGNOSTIC")
    print("=" * 70)

    # --------------------------------------------------
    # 1. Create test document chunks
    # --------------------------------------------------

    chunks = [

        # ==================================================
        # PDF DOCUMENT
        # ==================================================

        DocumentChunk(
            chunk_id="pdf_chunk_1",
            text=(
                "Artificial Intelligence (AI) is a field of "
                "computer science that focuses on creating systems "
                "capable of performing tasks that normally require "
                "human intelligence."
            ),
            source="sample data.pdf",
            file_type="pdf",
            page_number=1,
            metadata={
                "filename": "sample data.pdf",
                "page": 1,
                "chunk_index": 0,
            },
        ),

        DocumentChunk(
            chunk_id="pdf_chunk_2",
            text=(
                "Machine Learning is a subset of AI that allows "
                "computers to learn patterns from data and make "
                "predictions."
            ),
            source="sample data.pdf",
            file_type="pdf",
            page_number=1,
            metadata={
                "filename": "sample data.pdf",
                "page": 1,
                "chunk_index": 1,
            },
        ),

        DocumentChunk(
            chunk_id="pdf_chunk_3",
            text=(
                "Deep Learning is a type of Machine Learning that "
                "uses neural networks with multiple layers."
            ),
            source="sample data.pdf",
            file_type="pdf",
            page_number=1,
            metadata={
                "filename": "sample data.pdf",
                "page": 1,
                "chunk_index": 2,
            },
        ),

        DocumentChunk(
            chunk_id="pdf_chunk_4",
            text=(
                "Natural Language Processing allows computers to "
                "understand and process human language."
            ),
            source="sample data.pdf",
            file_type="pdf",
            page_number=1,
            metadata={
                "filename": "sample data.pdf",
                "page": 1,
                "chunk_index": 3,
            },
        ),

        # ==================================================
        # DOCX DOCUMENT
        # ==================================================

        DocumentChunk(
            chunk_id="docx_chunk_1",
            text=(
                "Artificial Intelligence is a field of "
                "computer science."
            ),
            source="sample.docx",
            file_type="docx",
            page_number=None,
            metadata={
                "filename": "sample.docx",
                "chunk_index": 0,
            },
        ),

        DocumentChunk(
            chunk_id="docx_chunk_2",
            text=(
                "Machine Learning allows computers to learn "
                "from data."
            ),
            source="sample.docx",
            file_type="docx",
            page_number=None,
            metadata={
                "filename": "sample.docx",
                "chunk_index": 1,
            },
        ),

        DocumentChunk(
            chunk_id="docx_chunk_3",
            text=(
                "Deep Learning uses neural networks to learn "
                "complex patterns."
            ),
            source="sample.docx",
            file_type="docx",
            page_number=None,
            metadata={
                "filename": "sample.docx",
                "chunk_index": 2,
            },
        ),

        DocumentChunk(
            chunk_id="docx_chunk_4",
            text=(
                "Natural Language Processing helps computers "
                "understand human language."
            ),
            source="sample.docx",
            file_type="docx",
            page_number=None,
            metadata={
                "filename": "sample.docx",
                "chunk_index": 3,
            },
        ),
    ]

    print(f"\nTotal test chunks: {len(chunks)}")
    print("PDF chunks: 4")
    print("DOCX chunks: 4")

    # --------------------------------------------------
    # 2. Build BM25 index
    # --------------------------------------------------

    print("\nBuilding BM25 index...")

    bm25_index = BM25Index()
    bm25_index.add_chunks(chunks)

    print(f"BM25 chunks: {bm25_index.count()}")

    # --------------------------------------------------
    # 3. Load embedding model
    # --------------------------------------------------

    print("\nLoading embedding model...")

    embedder = Embedder()

    # --------------------------------------------------
    # 4. Create isolated ChromaDB collection
    # --------------------------------------------------

    print("\nInitializing diagnostic ChromaDB collection...")

    vector_store = ChromaVectorStore(
        collection_name="ask_my_docs_two_document_diagnostic"
    )

    # --------------------------------------------------
    # 5. Generate embeddings
    # --------------------------------------------------

    print("\nGenerating embeddings...")

    texts = [
        chunk.text
        for chunk in chunks
    ]

    embeddings = embedder.embed_texts(texts)

    # --------------------------------------------------
    # 6. Prepare ChromaDB data
    # --------------------------------------------------

    ids = [
        chunk.chunk_id
        for chunk in chunks
    ]

    metadatas = [
        {
            **chunk.metadata,
            "source": chunk.source,
            "file_type": chunk.file_type,
            "page_number": chunk.page_number,
        }
        for chunk in chunks
    ]

    # --------------------------------------------------
    # 7. Store chunks in ChromaDB
    # --------------------------------------------------

    print("\nStoring chunks in ChromaDB...")

    vector_store.add_documents(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(
        f"Vector chunks: {vector_store.count()}"
    )

    # --------------------------------------------------
    # 8. Create vector retriever
    # --------------------------------------------------

    vector_retriever = VectorRetriever(
        embedder=embedder,
        vector_store=vector_store,
    )

    # --------------------------------------------------
    # 9. Load cross-encoder
    # --------------------------------------------------

    print("\nLoading Cross-Encoder...")

    reranker = CrossEncoderReranker()

    # --------------------------------------------------
    # 10. Create complete retrieval pipeline
    # --------------------------------------------------

    print("\nCreating retrieval pipeline...")

    pipeline = RetrievalPipeline(
        bm25_index=bm25_index,
        vector_retriever=vector_retriever,
        reranker=reranker,
    )

    # --------------------------------------------------
    # 11. Diagnostic questions
    # --------------------------------------------------

    questions = [
        "What can computers learn through Machine Learning?",
        "What kind of neural networks does Deep Learning use?",
        "What does NLP allow computers to understand?",
        "How is Deep Learning related to Machine Learning?",
        "What is the relationship between Machine Learning and Artificial Intelligence?",
    ]

    # --------------------------------------------------
    # 12. Run diagnostic
    # --------------------------------------------------

    for question in questions:

        print("\n")
        print("=" * 70)
        print(f"QUESTION: {question}")
        print("=" * 70)

        results = pipeline.search(
            query=question,
            retrieval_k=8,
            top_k=8,
        )

        for rank, result in enumerate(
            results,
            start=1,
        ):

            print("-" * 70)

            print(f"FINAL RANK       : {rank}")
            print(f"CHUNK ID         : {result['chunk_id']}")
            print(f"SOURCE           : {result['source']}")

            print(
                f"RERANKER SCORE   : "
                f"{result.get('reranker_score')}"
            )

            print(
                f"HYBRID RRF SCORE : "
                f"{result.get('rrf_score')}"
            )

            print(
                f"HYBRID RANK      : "
                f"{result.get('hybrid_rank')}"
            )

            print(
                f"BM25 RANK        : "
                f"{result.get('bm25_rank')}"
            )

            print(
                f"VECTOR RANK      : "
                f"{result.get('vector_rank')}"
            )

            print(
                f"TEXT             : "
                f"{result['text']}"
            )

    print("\n")
    print("=" * 70)
    print("TWO-DOCUMENT RETRIEVAL DIAGNOSTIC COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()