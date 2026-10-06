from backend.app.ingestion.txt_reader import read_txt


txt_path = "backend/app/ingestion/sample.txt"

pages = read_txt(txt_path)

print(f"Total document sections: {len(pages)}")

for page in pages:
    print("\n--- TXT Content ---")
    print(page.text[:1000])