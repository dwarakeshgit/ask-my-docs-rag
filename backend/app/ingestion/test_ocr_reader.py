from backend.app.ingestion.ocr_reader import read_image


image_path = "backend/app/ingestion/sample_ocr.png"

pages = read_image(image_path)

print(f"Total OCR pages: {len(pages)}")

for page in pages:
    print("--- OCR Content ---")
    print(page.text)