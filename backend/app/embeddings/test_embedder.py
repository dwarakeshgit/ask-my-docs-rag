from backend.app.embeddings.embedder import Embedder


def main():

    print("=" * 60)
    print("EMBEDDING TEST")
    print("=" * 60)

    embedder = Embedder()

    text = (
        "Machine Learning is a subset of Artificial Intelligence "
        "that allows computers to learn patterns from data."
    )

    embedding = embedder.embed_text(text)

    print(f"\nModel: {embedder.model_name}")
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")

    print("\n" + "=" * 60)
    print("EMBEDDING TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()