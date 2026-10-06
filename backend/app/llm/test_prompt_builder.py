from backend.app.llm.prompt_builder import GroundedPromptBuilder


def main():
    builder = GroundedPromptBuilder()

    question = "What is artificial intelligence?"

    evidence = [
        {
            "text": (
                "Artificial Intelligence (AI) is a field of computer science "
                "that focuses on creating systems capable of performing tasks "
                "that normally require human intelligence."
            ),
            "source": "sample data.pdf",
            "page_number": 1,
        }
    ]

    prompt = builder.build(
        question=question,
        evidence=evidence,
    )

    print("=" * 60)
    print("GROUNDED PROMPT TEST")
    print("=" * 60)
    print(prompt)
    print("=" * 60)


if __name__ == "__main__":
    main()