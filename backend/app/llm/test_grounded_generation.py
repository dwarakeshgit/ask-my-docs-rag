from backend.app.llm.ollama_client import OllamaClient
from backend.app.llm.prompt_builder import GroundedPromptBuilder


def main():
    print("=" * 60)
    print("GROUNDED LLM GENERATION TEST")
    print("=" * 60)

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

    prompt_builder = GroundedPromptBuilder()
    ollama_client = OllamaClient()

    prompt = prompt_builder.build(
        question=question,
        evidence=evidence,
    )

    print("\nSending grounded prompt to Qwen3 4B...\n")

    answer = ollama_client.generate(
        prompt=prompt,
        temperature=0.0,
    )

    print("QWEN ANSWER:")
    print(answer)

    print("\n" + "=" * 60)
    print("GROUNDED LLM GENERATION TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()