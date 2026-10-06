from backend.app.ingestion.html_reader import read_html


html_path = "backend/app/ingestion/sample.html"

pages = read_html(html_path)

print(f"Total document sections: {len(pages)}")

for page in pages:
    print("\n--- HTML Content ---")
    print(page.text[:1000])