import tiktoken

from backend.app.processing.chunker import chunk_text_by_tokens


text = """
Artificial Intelligence is a field of computer science.
Machine Learning allows computers to learn from data.
Deep Learning uses neural networks to learn complex patterns.
Natural Language Processing helps computers understand human language.
""" * 100


chunks = chunk_text_by_tokens(
    text,
    chunk_size=600,
    overlap=100,
)

tokenizer = tiktoken.get_encoding("cl100k_base")

print(f"Total chunks: {len(chunks)}")

for index, chunk in enumerate(chunks, start=1):
    token_count = len(tokenizer.encode(chunk))

    print(
        f"Chunk {index}: "
        f"{token_count} tokens, "
        f"{len(chunk)} characters"
    )