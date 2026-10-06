from pathlib import Path
from typing import Any, Dict

from backend.app.ingestion.pipeline import IngestionPipeline
from backend.app.ingestion.indexing_pipeline import IndexingPipeline
from backend.app.embeddings.embedder import Embedder
from backend.app.vectorstore.chroma_store import ChromaVectorStore
from backend.app.retrieval.bm25_index import BM25Index
from backend.app.retrieval.vector_retriever import VectorRetriever
from backend.app.retrieval.retrieval_pipeline import RetrievalPipeline
from backend.app.reranking.reranker import CrossEncoderReranker
from backend.app.evidence.sufficiency import EvidenceSufficiencyChecker
from backend.app.llm.prompt_builder import GroundedPromptBuilder
from backend.app.llm.transformers_client import TransformersClient
from backend.app.citations.formatter import CitationFormatter
from backend.app.rag.rag_generator import RAGGenerator


class RAGService:
    def __init__(self):
        # ---------------------------------------------------------
        # 1. Ingestion pipeline
        # ---------------------------------------------------------
        self.ingestion_pipeline = IngestionPipeline(
            chunk_size=600,
            overlap=100,
        )

        # ---------------------------------------------------------
        # 2. Embedding model
        # ---------------------------------------------------------
        self.embedder = Embedder()

        # ---------------------------------------------------------
        # 3. Persistent Chroma vector store
        # ---------------------------------------------------------
        self.vector_store = ChromaVectorStore(
            persist_directory="backend/data/chroma",
            collection_name="ask_my_docs",
        )

        # ---------------------------------------------------------
        # 4. BM25 index
        # ---------------------------------------------------------
        self.bm25_index = BM25Index()

        self._rebuild_bm25_index()

        # ---------------------------------------------------------
        # 5. Vector retriever
        # ---------------------------------------------------------
        self.vector_retriever = VectorRetriever(
            embedder=self.embedder,
            vector_store=self.vector_store,
        )

        # ---------------------------------------------------------
        # 6. Cross-encoder reranker
        # ---------------------------------------------------------
        self.reranker = CrossEncoderReranker()

        # ---------------------------------------------------------
        # 7. Complete retrieval pipeline
        # ---------------------------------------------------------
        self.retrieval_pipeline = RetrievalPipeline(
            bm25_index=self.bm25_index,
            vector_retriever=self.vector_retriever,
            reranker=self.reranker,
        )

        # ---------------------------------------------------------
        # 8. Evidence sufficiency checker
        # ---------------------------------------------------------
        #
        # Pass up to two strong evidence chunks to the LLM.
        #
        # This allows the model to use complementary evidence
        # when one chunk does not contain every important detail.
        #
        self.evidence_checker = EvidenceSufficiencyChecker(
            minimum_score=0.0,
            minimum_evidence=1,
            maximum_evidence=2,
        )

        # ---------------------------------------------------------
        # 9. Versioned grounded prompt
        # ---------------------------------------------------------
        self.prompt_builder = GroundedPromptBuilder(
            prompt_version="grounded_answer_v2.txt",
        )

        # ---------------------------------------------------------
        # 10. Local LLM through Hugging Face Transformers
        # ---------------------------------------------------------
        self.transformers_client = TransformersClient(
            model_name="Qwen/Qwen2.5-1.5B-Instruct",
            max_new_tokens=256,
        )

        # ---------------------------------------------------------
        # 11. Citation formatter
        # ---------------------------------------------------------
        self.citation_formatter = CitationFormatter()

        # ---------------------------------------------------------
        # 12. Complete RAG generation pipeline
        # ---------------------------------------------------------
        self.rag_generator = RAGGenerator(
            retrieval_pipeline=self.retrieval_pipeline,
            evidence_checker=self.evidence_checker,
            prompt_builder=self.prompt_builder,
            llm_client=self.transformers_client,
            citation_formatter=self.citation_formatter,
        )

        # ---------------------------------------------------------
        # 13. Document indexing pipeline
        # ---------------------------------------------------------
        self.indexing_pipeline = IndexingPipeline(
            ingestion_pipeline=self.ingestion_pipeline,
            embedder=self.embedder,
            vector_store=self.vector_store,
            bm25_index=self.bm25_index,
        )

    # =============================================================
    # BM25 REBUILD
    # =============================================================

    def _rebuild_bm25_index(self):
        """
        Rebuild the BM25 index from chunks already stored
        in the persistent Chroma vector store.
        """

        results = self.vector_store.collection.get(
            include=["documents", "metadatas"],
        )

        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []
        ids = results.get("ids") or []

        chunks = []

        for chunk_id, text, metadata in zip(
            ids,
            documents,
            metadatas,
        ):
            metadata = metadata or {}

            from backend.app.ingestion.models import DocumentChunk

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                text=text,
                source=metadata.get("source", ""),
                file_type=metadata.get("file_type", ""),
                page_number=metadata.get("page_number"),
                metadata=metadata,
            )

            chunks.append(chunk)

        if chunks:
            self.bm25_index.add_chunks(chunks)

        print(
            f"BM25 index rebuilt successfully: "
            f"{self.bm25_index.count()} chunks loaded."
        )

    # =============================================================
    # DOCUMENT INDEXING
    # =============================================================

    def index_document(self, file_path: str):
        """
        Ingest, chunk, embed, and index a document.
        """

        result = self.indexing_pipeline.index_document(
            file_path=file_path,
        )

        # Rebuild BM25 after adding new chunks so keyword
        # retrieval includes the newly indexed document.
        self._rebuild_bm25_index()

        return result

    # =============================================================
    # LIST DOCUMENTS
    # =============================================================

    def list_documents(self):
        """
        Return the documents currently stored in the vector store.
        """

        results = self.vector_store.collection.get(
            include=["documents", "metadatas"],
        )

        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []

        document_map = {}

        for text, metadata in zip(documents, metadatas):
            metadata = metadata or {}

            filename = metadata.get("filename")

            if not filename:
                source = metadata.get("source", "")
                filename = Path(source).name if source else "Unknown"

            if filename not in document_map:
                document_map[filename] = {
                    "filename": filename,
                    "file_type": metadata.get("file_type"),
                    "source": metadata.get("source"),
                    "chunks": 0,
                }

            document_map[filename]["chunks"] += 1

        return list(document_map.values())

    # =============================================================
    # ASK QUESTION
    # =============================================================

    def answer(self, question: str) -> Dict[str, Any]:
        """
        Run the complete RAG pipeline for a user question.

        Pipeline:

        Question
            ↓
        Hybrid Retrieval
            ↓
        Cross-Encoder Reranking
            ↓
        Evidence Sufficiency Check
            ↓
        Grounded Prompt
            ↓
        Transformers LLM
            ↓
        Answer + Citations
        """

        return self.rag_generator.answer(
            question=question,
            retrieval_k=10,
            top_k=5,
        )