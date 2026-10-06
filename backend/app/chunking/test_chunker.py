from backend.app.ingestion.pdf_reader import read_pdf
from backend.app.chunking.chunker import chunk_document_pages


PDF_PATH = "backend/app/ingestion/data/sample data.pdf"


def main():

    print("=" * 60)
    print("CHUNKER TEST")
    print("=" * 60)

    pages = read_pdf(PDF_PATH)

    chunks = chunk_document_pages(
        pages,
        chunk_size=200,
        chunk_overlap=50,
    )

    print(f"\nPages extracted: {len(pages)}")
    print(f"Chunks created: {len(chunks)}\n")

    for chunk in chunks:

        print("-" * 60)

        print(f"Chunk ID: {chunk.chunk_id}")

        print(f"Page: {chunk.page_number}")

        print(f"File Type: {chunk.file_type}")

        print(f"Source: {chunk.source}")

        print(f"Text:\n{chunk.text}")

        print(f"Metadata: {chunk.metadata}")

    print("\n" + "=" * 60)
    print("CHUNKER TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()