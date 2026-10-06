from docx import Document

from .models import DocumentPage


def read_docx(file_path: str) -> list[DocumentPage]:
    document = Document(file_path)

    text_parts = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            text_parts.append(text)

    full_text = "\n".join(text_parts)

    return [
        DocumentPage(
            text=full_text,
            source=file_path,
            file_type="docx",
            page_number=None,
        )
    ]