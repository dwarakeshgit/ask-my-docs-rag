from pathlib import Path

from backend.app.evaluation.evaluator import RAGEvaluator


def main():
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

    evaluation = evaluator.evaluate_all()

    print()
    print("=" * 60)
    print("DETAILED FAILED CASES")
    print("=" * 60)

    failed_cases = [
        result
        for result in evaluation["results"]
        if not result["passed"]
    ]

    if not failed_cases:
        print("No failed cases.")
    else:
        for result in failed_cases:
            print()
            print(f"ID: {result['id']}")
            print(f"Question: {result['question']}")

            print()
            print("Expected answer:")
            print(result["expected_answer"])

            print()
            print("Actual answer:")
            print(result["actual_answer"])

            print()
            print("Expected sources:")
            print(result["expected_sources"])

            print()
            print("Actual sources:")
            print(result["actual_sources"])

            print()
            print(
                f"Answer match: "
                f"{result['answer_match']:.4f}"
            )

            print(
                f"Source found: "
                f"{result['source_found']}"
            )

            print(
                f"Sufficient: "
                f"{result['sufficient']}"
            )

            print(
                f"Passed: "
                f"{result['passed']}"
            )

            print("-" * 60)

    print()
    print("=" * 60)
    print("RAG EVALUATION SUMMARY")
    print("=" * 60)

    print(
        f"Total cases : "
        f"{evaluation['total_cases']}"
    )

    print(
        f"Passed      : "
        f"{evaluation['passed_cases']}"
    )

    print(
        f"Failed      : "
        f"{evaluation['failed_cases']}"
    )

    print(
        f"Pass rate   : "
        f"{evaluation['pass_rate']:.2%}"
    )

    print("=" * 60)

    if evaluation["failed_cases"] > 0:
        raise SystemExit(1)

    raise SystemExit(0)


if __name__ == "__main__":
    main()