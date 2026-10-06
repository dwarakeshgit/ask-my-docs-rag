import pymupdf
import pytesseract
from PIL import Image

from .models import DocumentPage


def read_pdf(file_path: str) -> list[DocumentPage]:
    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text().strip()

        if not text:
            pixmap = page.get_pixmap(dpi=200)

            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples,
            )

            text = pytesseract.image_to_string(image).strip()

        pages.append(
            DocumentPage(
                text=text,
                source=file_path,
                file_type="pdf",
                page_number=page_number,
                metadata={
                    "ocr_used": not bool(page.get_text().strip())
                },
            )
        )

    document.close()

    return pages