import json
import re
from pathlib import Path
from typing import Any, Dict, List

from backend.app.services.rag_service import RAGService


class RAGEvaluator:
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Golden dataset not found: {self.dataset_path}"
            )

        with self.dataset_path.open(
            "r",
            encoding="utf-8-sig",
        ) as file:
            self.dataset = json.load(file)

        if not isinstance(self.dataset, list):
            raise ValueError(
                "Golden dataset must contain a JSON list."
            )

        self.rag_service = RAGService()

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""

        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @classmethod
    def calculate_answer_match(
        cls,
        expected_answer: str,
        actual_answer: str,
    ) -> float:
        expected = cls.normalize_text(expected_answer)
        actual = cls.normalize_text(actual_answer)

        if not expected:
            return 0.0

        expected_words = set(expected.split())
        actual_words = set(actual.split())

        if not expected_words:
            return 0.0

        matched_words = expected_words.intersection(
            actual_words
        )

        return len(matched_words) / len(expected_words)

    @staticmethod
    def normalize_source(source: str) -> str:
        if not source:
            return ""

        source = source.strip()

        source = re.sub(
            r",\s*page\s+\d+$",
            "",
            source,
            flags=re.IGNORECASE,
        )

        return Path(source).name.lower()

    @classmethod
    def check_source_retrieval(
        cls,
        expected_sources: List[str],
        actual_sources: List[str],
    ) -> bool:
        if not expected_sources:
            return not actual_sources

        normalized_actual = {
            cls.normalize_source(source)
            for source in actual_sources
        }

        normalized_expected = {
            cls.normalize_source(source)
            for source in expected_sources
        }

        return bool(
            normalized_expected.intersection(
                normalized_actual
            )
        )

    @classmethod
    def check_expected_refusal(
        cls,
        expected_answer: str,
        actual_answer: str,
        sufficient: bool,
    ) -> bool:
        expected = cls.normalize_text(expected_answer)
        actual = cls.normalize_text(actual_answer)

        refusal_message = cls.normalize_text(
            "I don't have enough information in the provided documents to answer that."
        )

        expected_refusal = expected == refusal_message
        actual_refusal = actual == refusal_message

        return (
            expected_refusal
            and actual_refusal
            and not sufficient
        )

    def evaluate_case(
        self,
        test_case: Dict[str, Any],
    ) -> Dict[str, Any]:
        question = test_case["question"]
        expected_answer = test_case["expected_answer"]
        expected_sources = test_case["expected_sources"]

        result = self.rag_service.answer(
            question=question
        )

        actual_answer = result["answer"]
        actual_sources = result.get("citations", [])

        answer_match = self.calculate_answer_match(
            expected_answer=expected_answer,
            actual_answer=actual_answer,
        )

        source_found = self.check_source_retrieval(
            expected_sources=expected_sources,
            actual_sources=actual_sources,
        )

        refusal_expected = (
            self.normalize_text(expected_answer)
            == self.normalize_text(
                "I don't have enough information in the provided documents to answer that."
            )
        )

        if refusal_expected:
            passed = self.check_expected_refusal(
                expected_answer=expected_answer,
                actual_answer=actual_answer,
                sufficient=result["sufficient"],
            )
        else:
            passed = (
                answer_match >= 0.5
                and source_found
                and result["sufficient"]
            )

        return {
            "id": test_case["id"],
            "question": question,
            "expected_answer": expected_answer,
            "actual_answer": actual_answer,
            "expected_sources": expected_sources,
            "actual_sources": actual_sources,
            "answer_match": round(answer_match, 4),
            "source_found": source_found,
            "sufficient": result["sufficient"],
            "refusal_expected": refusal_expected,
            "passed": passed,
        }

    def evaluate_all(self) -> Dict[str, Any]:
        results = []

        for test_case in self.dataset:
            print(
                f"Evaluating {test_case['id']}: "
                f"{test_case['question']}"
            )

            result = self.evaluate_case(test_case)
            results.append(result)

            print(
                f"  Answer match: "
                f"{result['answer_match']:.2f}"
            )

            print(
                f"  Source found: "
                f"{result['source_found']}"
            )

            print(
                f"  Sufficient: "
                f"{result['sufficient']}"
            )

            print(
                f"  Refusal expected: "
                f"{result['refusal_expected']}"
            )

            print(
                f"  Passed: "
                f"{result['passed']}"
            )

            print()

        total = len(results)

        passed = sum(
            1
            for result in results
            if result["passed"]
        )

        pass_rate = (
            passed / total
            if total > 0
            else 0.0
        )

        summary = {
            "total_cases": total,
            "passed_cases": passed,
            "failed_cases": total - passed,
            "pass_rate": round(pass_rate, 4),
            "results": results,
        }

        print("=" * 60)
        print("RAG EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total cases : {summary['total_cases']}")
        print(f"Passed      : {summary['passed_cases']}")
        print(f"Failed      : {summary['failed_cases']}")
        print(f"Pass rate   : {summary['pass_rate'] * 100:.2f}%")
        print("=" * 60)

        return summary


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]

    dataset_path = (
        project_root
        / "backend"
        / "app"
        / "evaluation"
        / "golden_dataset.json"
    )

    evaluator = RAGEvaluator(
        dataset_path=str(dataset_path)
    )

    evaluator.evaluate_all()