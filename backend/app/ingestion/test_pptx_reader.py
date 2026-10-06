from backend.app.ingestion.pptx_reader import read_pptx


pptx_path = "backend/app/ingestion/data/sample.pptx"

slides = read_pptx(pptx_path)

print(f"Total slides extracted: {len(slides)}")

for slide in slides:
    print(f"\n--- Slide {slide.metadata['slide_number']} ---")
    print(slide.text[:1000])