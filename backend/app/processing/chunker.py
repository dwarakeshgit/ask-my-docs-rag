import tiktoken


def chunk_text(
    text: str,
    chunk_size: int = 3000,
    overlap: int = 500,
) -> list[str]:

    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def chunk_text_by_tokens(
    text: str,
    chunk_size: int = 600,
    overlap: int = 100,
) -> list[str]:

    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    tokenizer = tiktoken.get_encoding("cl100k_base")

    tokens = tokenizer.encode(text)

    chunks = []

    start = 0
    total_tokens = len(tokens)

    while start < total_tokens:
        end = start + chunk_size

        chunk_tokens = tokens[start:end]

        chunk = tokenizer.decode(chunk_tokens).strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks