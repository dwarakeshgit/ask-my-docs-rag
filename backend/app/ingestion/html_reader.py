from bs4 import BeautifulSoup

from .models import DocumentPage


def read_html(file_path: str) -> list[DocumentPage]:
    with open(file_path, "r", encoding="utf-8") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    text = soup.get_text(separator="\n", strip=True)

    return [
        DocumentPage(
            text=text,
            source=file_path,
            file_type="html",
            page_number=None,
        )
    ]