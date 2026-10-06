from backend.app.processing.embedder import create_embeddings


texts = [
    "Machine learning allows computers to learn from data.",
    "Deep learning uses neural networks to learn complex patterns.",
]


embeddings = create_embeddings(texts)

print(f"Number of embeddings: {len(embeddings)}")

for index, embedding in enumerate(embeddings, start=1):
    print(f"Embedding {index} dimensions: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")