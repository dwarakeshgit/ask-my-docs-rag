from backend.app.ingestion.pdf_reader import read_pdf


pdf_path = "backend/app/ingestion/data/scanned_sample.pdf"

pages = read_pdf(pdf_path)

print(f"Total pages: {len(pages)}")

for page in pages:
    print(f"--- Page {page.page_number} ---")
    print(f"OCR used: {page.metadata['ocr_used']}")
    print("--- Extracted Content ---")
    print(page.text)