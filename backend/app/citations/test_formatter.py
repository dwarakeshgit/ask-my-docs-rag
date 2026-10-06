from backend.app.citations.formatter import CitationFormatter


def main():
    formatter = CitationFormatter()

    evidence = {
        "source": "backend/app/ingestion/data/sample data.pdf",
        "page_number": 1,
        "metadata": {
            "filename": "sample data.pdf",
        },
    }

    citation = formatter.format_citation(evidence)

    print("=" * 60)
    print("CITATION FORMATTER TEST")
    print("=" * 60)

    print(f"\nOriginal source:")
    print(evidence["source"])

    print(f"\nUser-facing citation:")
    print(citation)

    print("\n" + "=" * 60)
    print("CITATION FORMATTER TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()