from .models import DocumentPage


def read_txt(file_path: str) -> list[DocumentPage]:
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return [
        DocumentPage(
            text=text,
            source=file_path,
            file_type="txt",
            page_number=None,
        )
    ]