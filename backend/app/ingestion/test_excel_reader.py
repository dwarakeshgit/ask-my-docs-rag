from backend.app.ingestion.excel_reader import read_excel


excel_path = "backend/app/ingestion/data/sample.xlsx"

pages = read_excel(excel_path)

print(f"Total sheets extracted: {len(pages)}")

for page in pages:
    print(f"\n--- Sheet: {page.metadata['sheet']} ---")
    print(page.text[:1000])