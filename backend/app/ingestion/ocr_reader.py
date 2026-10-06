from PIL import Image
import pytesseract

from .models import DocumentPage


def read_image(file_path: str) -> list[DocumentPage]:
    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return [
        DocumentPage(
            text=text,
            source=file_path,
            file_type="image",
            page_number=None,
        )
    ]