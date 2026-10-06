import csv

from .models import DocumentPage


def read_csv(file_path: str) -> list[DocumentPage]:
    rows = []

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row_text = " | ".join(
                f"{key}: {value}" for key, value in row.items()
            )
            rows.append(row_text)

    text = "\n".join(rows)

    return [
        DocumentPage(
            text=text,
            source=file_path,
            file_type="csv",
            page_number=None,
        )
    ]