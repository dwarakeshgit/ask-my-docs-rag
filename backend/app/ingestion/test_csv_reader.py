from backend.app.ingestion.csv_reader import read_csv


csv_path = "backend/app/ingestion/sample.csv"

pages = read_csv(csv_path)

print(f"Total document sections: {len(pages)}")

for page in pages:
    print("\n--- CSV Content ---")
    print(page.text[:1000])