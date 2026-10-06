from .pdf_reader import read_pdf

PDF_PATH = "backend/app/ingestion/data/sample data.pdf"


def main():
    print("=" * 60)
    print("PDF READER TEST")
    print("=" * 60)

    print(f"\nReading: {PDF_PATH}\n")

    pages = read_pdf(PDF_PATH)

    print(f"Number of pages extracted: {len(pages)}\n")

    for page in pages:
        print("-" * 60)
        print(f"Page Number: {page.page_number}")
        print(f"Text:\n{page.text}")
        print(f"Metadata: {page.metadata}")

    print("\n" + "=" * 60)
    print("PDF READER TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()