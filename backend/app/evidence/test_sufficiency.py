from backend.app.evidence.sufficiency import EvidenceSufficiencyChecker


def main():
    checker = EvidenceSufficiencyChecker(
        minimum_score=0.0,
        minimum_evidence=1,
    )

    relevant_documents = [
        {
            "chunk_id": "chunk_1",
            "text": "Artificial Intelligence is a field of computer science.",
            "reranker_score": 10.23,
        }
    ]

    irrelevant_documents = [
        {
            "chunk_id": "chunk_2",
            "text": "Deep Learning uses neural networks.",
            "reranker_score": -5.05,
        }
    ]

    print("=" * 60)
    print("EVIDENCE SUFFICIENCY TEST")
    print("=" * 60)

    print("\nTest 1: Relevant evidence")

    result = checker.check(relevant_documents)

    print(f"Sufficient: {result['sufficient']}")
    print(f"Reason: {result['reason']}")
    print(f"Evidence count: {len(result['evidence'])}")

    print("\nTest 2: Insufficient evidence")

    result = checker.check(irrelevant_documents)

    print(f"Sufficient: {result['sufficient']}")
    print(f"Reason: {result['reason']}")
    print(f"Evidence count: {len(result['evidence'])}")

    print("\n" + "=" * 60)
    print("EVIDENCE SUFFICIENCY TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()