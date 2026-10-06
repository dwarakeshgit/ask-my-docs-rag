from backend.app.llm.ollama_client import OllamaClient


def main():
    print("=" * 60)
    print("OLLAMA CLIENT TEST")
    print("=" * 60)

    client = OllamaClient()

    prompt = "Say exactly: Python connected to Qwen successfully."

    print("\nSending prompt to Qwen3 4B...")
    response = client.generate(
        prompt=prompt,
        temperature=0.0,
    )

    print("\nQwen response:")
    print(response)

    print("\n" + "=" * 60)
    print("OLLAMA CLIENT TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()