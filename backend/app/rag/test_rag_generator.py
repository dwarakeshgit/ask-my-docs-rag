from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.ingestion.indexing_pipeline import IndexingPipeline
from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore
from backend.app.retrieval.bm25_index import BM25Index
from backend.app.retrieval.vector_retriever import VectorRetriever
from backend.app.reranking.reranker import CrossEncoderReranker
from backend.app.retrieval.retrieval_pipeline import RetrievalPipeline
from backend.app.evidence.sufficiency import EvidenceSufficiencyChecker
from backend.app.llm.prompt_builder import GroundedPromptBuilder
from backend.app.llm.ollama_client import OllamaClient
from backend.app.citations.formatter import CitationFormatter
from backend.app.rag.rag_generator import RAGGenerator


def main():
    print("=" * 60)
    print("REAL DOCUMENT RAG GENERATION TEST")
    print("=" * 60)

    pdf_path = "backend/app/ingestion/data/sample data.pdf"

    # ---------------------------------------------------------
    # 1. Create the ingestion pipeline
    # ---------------------------------------------------------
    ingestion_pipeline = IngestionPipeline(
        chunk_size=600,
        overlap=100,
    )

    # ---------------------------------------------------------
    # 2. Create the embedding model
    # ---------------------------------------------------------
    embedder = Embedder()

    # ---------------------------------------------------------
    # 3. Create an isolated Chroma vector store for this test
    # ---------------------------------------------------------
    vector_store = ChromaVectorStore(
        persist_directory="backend/data/chroma_rag_test",
        collection_name="rag_generation_test",
    )

    # ---------------------------------------------------------
    # 4. Create the BM25 index
    # ---------------------------------------------------------
    bm25_index = BM25Index()

    # ---------------------------------------------------------
    # 5. Create the indexing pipeline
    # ---------------------------------------------------------
    indexing_pipeline = IndexingPipeline(
        ingestion_pipeline=ingestion_pipeline,
        embedder=embedder,
        vector_store=vector_store,
        bm25_index=bm25_index,
    )

    # ---------------------------------------------------------
    # 6. Index the real PDF
    # ---------------------------------------------------------
    print("\nIndexing real PDF...")

    chunks = indexing_pipeline.index_document(pdf_path)

    print(f"Chunks indexed: {len(chunks)}")
    print(f"Chroma count: {vector_store.count()}")
    print(f"BM25 count: {bm25_index.count()}")

    # ---------------------------------------------------------
    # 7. Create vector retriever
    # ---------------------------------------------------------
    vector_retriever = VectorRetriever(
        embedder=embedder,
        vector_store=vector_store,
    )

    # ---------------------------------------------------------
    # 8. Create cross-encoder reranker
    # ---------------------------------------------------------
    reranker = CrossEncoderReranker()

    # ---------------------------------------------------------
    # 9. Create the complete retrieval pipeline
    # ---------------------------------------------------------
    retrieval_pipeline = RetrievalPipeline(
        bm25_index=bm25_index,
        vector_retriever=vector_retriever,
        reranker=reranker,
    )

    # ---------------------------------------------------------
    # 10. Create evidence sufficiency checker
    # ---------------------------------------------------------
    evidence_checker = EvidenceSufficiencyChecker(
        minimum_score=0.0,
        minimum_evidence=1,
    )

    # ---------------------------------------------------------
    # 11. Create grounded prompt builder
    # ---------------------------------------------------------
    prompt_builder = GroundedPromptBuilder()

    # ---------------------------------------------------------
    # 12. Create Ollama client
    # ---------------------------------------------------------
    ollama_client = OllamaClient(
        model_name="qwen3:4b",
    )

    # ---------------------------------------------------------
    # 13. Create citation formatter
    # ---------------------------------------------------------
    citation_formatter = CitationFormatter()

    # ---------------------------------------------------------
    # 14. Create the complete RAG generator
    # ---------------------------------------------------------
    rag_generator = RAGGenerator(
        retrieval_pipeline=retrieval_pipeline,
        evidence_checker=evidence_checker,
        prompt_builder=prompt_builder,
        ollama_client=ollama_client,
        citation_formatter=citation_formatter,
    )

    # ---------------------------------------------------------
    # 15. Ask a real question
    # ---------------------------------------------------------
    question = "What is artificial intelligence?"

    print("\n" + "=" * 60)
    print(f"QUESTION: {question}")
    print("=" * 60)

    # ---------------------------------------------------------
    # 16. Generate the grounded answer
    # ---------------------------------------------------------
    result = rag_generator.answer(
        question=question,
        retrieval_k=10,
        top_k=5,
    )

    # ---------------------------------------------------------
    # 17. Display the generated answer
    # ---------------------------------------------------------
    print("\nANSWER:")
    print(result["answer"])

    # ---------------------------------------------------------
    # 18. Display evidence sufficiency result
    # ---------------------------------------------------------
    print("\nSUFFICIENT:")
    print(result["sufficient"])

    print("\nREASON:")
    print(result["reason"])

    # ---------------------------------------------------------
    # 19. Display verified application-generated citations
    # ---------------------------------------------------------
    print("\nVERIFIED CITATIONS:")

    for citation in result["citations"]:
        print(f"- {citation}")

    # ---------------------------------------------------------
    # 20. Display the evidence used by the RAG system
    # ---------------------------------------------------------
    print("\nEVIDENCE USED:")

    for index, evidence in enumerate(result["evidence"], start=1):
        print("\n" + "-" * 60)
        print(f"Evidence {index}")
        print(f"Chunk ID: {evidence.get('chunk_id')}")
        print(f"Source: {evidence.get('source')}")
        print(f"Page: {evidence.get('page_number')}")
        print(f"Reranker Score: {evidence.get('reranker_score')}")
        print(f"Text: {evidence.get('text')}")

    print("\n" + "=" * 60)
    print("REAL DOCUMENT RAG GENERATION TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()