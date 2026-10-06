from pathlib import Path


SUPPORTED_FILE_TYPES = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".txt": "txt",
    ".md": "markdown",
    ".csv": "csv",
    ".xlsx": "xlsx",
    ".xls": "xls",
    ".pptx": "pptx",
    ".html": "html",
    ".htm": "html",
}


def detect_file_type(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension not in SUPPORTED_FILE_TYPES:
        raise ValueError(
            f"Unsupported file type: {extension or 'unknown'}"
        )

    return SUPPORTED_FILE_TYPES[extension]