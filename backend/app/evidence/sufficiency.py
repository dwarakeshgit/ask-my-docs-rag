from typing import List, Dict, Any
import re


class EvidenceSufficiencyChecker:
    """
    Determines whether retrieved evidence is strong enough
    to support an answer to the user's specific question.

    Evidence selection considers:

    1. Cross-encoder relevance.
    2. Question-term coverage.
    3. Evidence detail/coverage.

    The goal is to avoid selecting a short but only partially
    informative chunk when another retrieved chunk contains
    stronger answer-bearing information.
    """

    def __init__(
        self,
        minimum_score: float = 0.0,
        minimum_evidence: int = 1,
        maximum_evidence: int = 1,
        minimum_question_overlap: float = 0.2,
    ):
        self.minimum_score = minimum_score
        self.minimum_evidence = minimum_evidence
        self.maximum_evidence = maximum_evidence
        self.minimum_question_overlap = minimum_question_overlap

    def check(
        self,
        question: str,
        documents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        if not question or not question.strip():
            return {
                "sufficient": False,
                "reason": "Question cannot be empty.",
                "evidence": [],
            }

        if not documents:
            return {
                "sufficient": False,
                "reason": "No evidence was retrieved.",
                "evidence": [],
            }

        scored_documents = [
            document
            for document in documents
            if document.get("reranker_score") is not None
        ]

        if not scored_documents:
            return {
                "sufficient": False,
                "reason": "Retrieved evidence has no relevance scores.",
                "evidence": [],
            }

        best_score = max(
            document["reranker_score"]
            for document in scored_documents
        )

        if best_score < self.minimum_score:
            return {
                "sufficient": False,
                "reason": (
                    "The strongest retrieved evidence was not "
                    "sufficiently relevant."
                ),
                "evidence": [],
            }

        ranked_documents = self._rank_evidence(
            question=question,
            documents=scored_documents,
        )

        evidence = ranked_documents[: self.maximum_evidence]

        if len(evidence) < self.minimum_evidence:
            return {
                "sufficient": False,
                "reason": "Not enough relevant evidence was retrieved.",
                "evidence": [],
            }

        question_overlap = self._calculate_question_overlap(
            question=question,
            evidence=evidence,
        )

        if question_overlap < self.minimum_question_overlap:
            return {
                "sufficient": False,
                "reason": (
                    "The retrieved evidence is related to the topic, "
                    "but it does not contain enough information to "
                    "answer the specific question."
                ),
                "evidence": [],
            }

        question_type_check = self._check_question_type(
            question=question,
            evidence=evidence,
        )

        if not question_type_check["sufficient"]:
            return {
                "sufficient": False,
                "reason": question_type_check["reason"],
                "evidence": [],
            }

        return {
            "sufficient": True,
            "reason": "Sufficient relevant evidence was found.",
            "evidence": evidence,
        }

    def _rank_evidence(
        self,
        question: str,
        documents: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Rank retrieved documents using both relevance and
        answer-bearing evidence coverage.

        The reranker remains the primary relevance signal,
        while lexical coverage helps distinguish between
        similarly relevant but differently informative chunks.
        """

        question_terms = self._extract_terms(question)

        if not question_terms:
            return documents

        scored_documents = []

        reranker_scores = [
            float(document["reranker_score"])
            for document in documents
        ]

        minimum_reranker = min(reranker_scores)
        maximum_reranker = max(reranker_scores)

        reranker_range = (
            maximum_reranker - minimum_reranker
        )

        for document in documents:

            text = document.get("text", "")

            evidence_terms = set(
                self._extract_terms(text)
            )

            matched_terms = [
                term
                for term in question_terms
                if term in evidence_terms
            ]

            question_coverage = (
                len(matched_terms) / len(question_terms)
                if question_terms
                else 0.0
            )

            evidence_length = len(evidence_terms)

            detail_score = min(
                evidence_length / 20.0,
                1.0,
            )

            if reranker_range > 0:
                normalized_reranker = (
                    (
                        float(document["reranker_score"])
                        - minimum_reranker
                    )
                    / reranker_range
                )
            else:
                normalized_reranker = 1.0

            evidence_quality_score = (
                0.60 * normalized_reranker
                + 0.25 * question_coverage
                + 0.15 * detail_score
            )

            result = document.copy()

            result["question_coverage"] = question_coverage
            result["evidence_detail_score"] = detail_score
            result["evidence_quality_score"] = evidence_quality_score

            scored_documents.append(result)

        scored_documents.sort(
            key=lambda document: (
                -document["evidence_quality_score"],
                -document["reranker_score"],
            )
        )

        return scored_documents

    def _calculate_question_overlap(
        self,
        question: str,
        evidence: List[Dict[str, Any]],
    ) -> float:

        question_terms = self._extract_terms(question)

        if not question_terms:
            return 1.0

        evidence_text = " ".join(
            document.get("text", "")
            for document in evidence
        ).lower()

        evidence_terms = set(
            self._extract_terms(evidence_text)
        )

        matched_terms = sum(
            1
            for term in question_terms
            if term in evidence_terms
        )

        return matched_terms / len(question_terms)

    def _check_question_type(
        self,
        question: str,
        evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        question_words = re.findall(
            r"\b[a-zA-Z]+\b",
            question.lower(),
        )

        if not question_words:
            return {
                "sufficient": False,
                "reason": "Question does not contain recognizable terms.",
            }

        question_type = question_words[0]

        evidence_text = " ".join(
            document.get("text", "")
            for document in evidence
        )

        if question_type == "who":
            if not self._contains_person_or_entity_answer(
                evidence_text
            ):
                return {
                    "sufficient": False,
                    "reason": (
                        "The retrieved evidence discusses the topic "
                        "but does not contain a person or entity that "
                        "answers the 'who' question."
                    ),
                }

        elif question_type == "when":
            if not self._contains_date_or_time_answer(
                evidence_text
            ):
                return {
                    "sufficient": False,
                    "reason": (
                        "The retrieved evidence discusses the topic "
                        "but does not contain a date or time that "
                        "answers the 'when' question."
                    ),
                }

        elif question_type == "where":
            if not self._contains_location_answer(
                evidence_text
            ):
                return {
                    "sufficient": False,
                    "reason": (
                        "The retrieved evidence discusses the topic "
                        "but does not contain a location that "
                        "answers the 'where' question."
                    ),
                }

        return {
            "sufficient": True,
            "reason": "Question type is compatible with the evidence.",
        }

    @staticmethod
    def _contains_person_or_entity_answer(
        evidence_text: str,
    ) -> bool:

        if not evidence_text.strip():
            return False

        explicit_patterns = [
            r"\binvented\s+by\s+[A-Z][a-z]+",
            r"\bcreated\s+by\s+[A-Z][a-z]+",
            r"\bfounded\s+by\s+[A-Z][a-z]+",
            r"\bdeveloped\s+by\s+[A-Z][a-z]+",
            r"\bintroduced\s+by\s+[A-Z][a-z]+",
            r"\bdiscovered\s+by\s+[A-Z][a-z]+",
            r"\bproposed\s+by\s+[A-Z][a-z]+",
            r"\bdesigned\s+by\s+[A-Z][a-z]+",
            r"\binventor(?:\s+is|\s*:\s*)\s*[A-Z][a-z]+",
            r"\bcreator(?:\s+is|\s*:\s*)\s*[A-Z][a-z]+",
            r"\bfounder(?:\s+is|\s*:\s*)\s*[A-Z][a-z]+",
        ]

        return any(
            re.search(pattern, evidence_text)
            for pattern in explicit_patterns
        )

    @staticmethod
    def _contains_date_or_time_answer(
        evidence_text: str,
    ) -> bool:

        date_patterns = [
            r"\b(?:19|20)\d{2}\b",
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b(?:January|February|March|April|May|June|July|"
            r"August|September|October|November|December)"
            r"\s+\d{1,2}(?:,\s+\d{4})?\b",
            r"\b\d{1,2}:\d{2}\b",
        ]

        return any(
            re.search(pattern, evidence_text, re.IGNORECASE)
            for pattern in date_patterns
        )

    @staticmethod
    def _contains_location_answer(
        evidence_text: str,
    ) -> bool:

        location_patterns = [
            r"\bin\s+[A-Z][a-z]+",
            r"\bat\s+[A-Z][a-z]+",
            r"\bnear\s+[A-Z][a-z]+",
            r"\bfrom\s+[A-Z][a-z]+",
            r"\b(?:city|country|state|province|region)\b",
        ]

        return any(
            re.search(pattern, evidence_text)
            for pattern in location_patterns
        )

    @staticmethod
    def _extract_terms(text: str) -> List[str]:

        stop_words = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "can",
            "do",
            "does",
            "for",
            "from",
            "how",
            "in",
            "is",
            "it",
            "of",
            "on",
            "or",
            "that",
            "the",
            "these",
            "this",
            "to",
            "was",
            "what",
            "when",
            "where",
            "which",
            "who",
            "why",
            "with",
        }

        normalized = text.lower()

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            normalized,
        )

        return [
            word
            for word in words
            if word not in stop_words
        ]