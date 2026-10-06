from typing import Dict, Any

from backend.app.citations.formatter import CitationFormatter
from backend.app.evidence.sufficiency import EvidenceSufficiencyChecker
from backend.app.llm.prompt_builder import GroundedPromptBuilder


class RAGGenerator:
    def __init__(
        self,
        retrieval_pipeline,
        evidence_checker: EvidenceSufficiencyChecker,
        prompt_builder: GroundedPromptBuilder,
        llm_client,
        citation_formatter: CitationFormatter,
    ):
        self.retrieval_pipeline = retrieval_pipeline
        self.evidence_checker = evidence_checker
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client
        self.citation_formatter = citation_formatter

    def answer(
        self,
        question: str,
        retrieval_k: int = 10,
        top_k: int = 5,
    ) -> Dict[str, Any]:

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        # ---------------------------------------------------------
        # 1. Retrieve relevant documents
        # ---------------------------------------------------------

        retrieved_documents = self.retrieval_pipeline.search(
            query=question,
            retrieval_k=retrieval_k,
            top_k=top_k,
        )

        # ---------------------------------------------------------
        # 2. Check whether retrieved evidence can answer
        #    the specific question
        # ---------------------------------------------------------

        evidence_result = self.evidence_checker.check(
            question=question,
            documents=retrieved_documents,
        )

        if not evidence_result["sufficient"]:
            return {
                "answer": (
                    "I don't have enough information in the provided "
                    "documents to answer that."
                ),
                "sufficient": False,
                "reason": evidence_result["reason"],
                "evidence": [],
                "citations": [],
            }

        evidence = evidence_result["evidence"]

        # ---------------------------------------------------------
        # 3. Build grounded prompt
        # ---------------------------------------------------------

        prompt = self.prompt_builder.build(
            question=question,
            evidence=evidence,
        )

        # ---------------------------------------------------------
        # 4. Generate answer using the configured LLM
        # ---------------------------------------------------------

        answer = self.llm_client.generate(
            prompt=prompt,
            temperature=0.0,
        )

        # ---------------------------------------------------------
        # 5. Generate and enforce citations
        # ---------------------------------------------------------

        citations = []

        for document in evidence:
            citation = self.citation_formatter.format_citation(
                document
            )

            if citation and citation not in citations:
                citations.append(citation)

        # ---------------------------------------------------------
        # 6. Citation enforcement
        # ---------------------------------------------------------

        if not citations:
            return {
                "answer": (
                    "I don't have enough information in the provided "
                    "documents to answer that."
                ),
                "sufficient": False,
                "reason": (
                    "Relevant evidence was retrieved, but a valid "
                    "citation could not be generated."
                ),
                "evidence": [],
                "citations": [],
            }

        # ---------------------------------------------------------
        # 7. Return complete grounded RAG response
        # ---------------------------------------------------------

        return {
            "answer": answer,
            "sufficient": True,
            "reason": evidence_result["reason"],
            "evidence": evidence,
            "citations": citations,
        }