from backend.app.ingestion.docx_reader import read_docx


docx_path = "backend/app/ingestion/data/sample.docx"

pages = read_docx(docx_path)

print(f"Total document sections: {len(pages)}")

for page in pages:
    print("\n--- DOCX Content ---")
    print(page.text[:1000])