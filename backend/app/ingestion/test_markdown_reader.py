from backend.app.ingestion.markdown_reader import read_markdown


markdown_path = "backend/app/ingestion/sample.md"

pages = read_markdown(markdown_path)

print(f"Total document sections: {len(pages)}")

for page in pages:
    print("\n--- Markdown Content ---")
    print(page.text[:1000])