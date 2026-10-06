from pathlib import Path
from typing import List

from backend.app.ingestion.file_detector import detect_file_type
from backend.app.ingestion.models import DocumentChunk
from backend.app.ingestion.pdf_reader import read_pdf
from backend.app.ingestion.docx_reader import read_docx
from backend.app.ingestion.txt_reader import read_txt
from backend.app.ingestion.markdown_reader import read_markdown
from backend.app.ingestion.csv_reader import read_csv
from backend.app.ingestion.excel_reader import read_excel
from backend.app.ingestion.pptx_reader import read_pptx
from backend.app.ingestion.html_reader import read_html

from backend.app.processing.text_cleaner import clean_text
from backend.app.processing.chunker import chunk_text_by_tokens


class IngestionPipeline:
    """
    Reads documents, cleans their text, and converts them
    into searchable DocumentChunk objects.
    """

    def __init__(
        self,
        chunk_size: int = 600,
        overlap: int = 100,
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def read_document(self, file_path: str):
        """
        Detect the file type and use the appropriate reader.
        """

        file_type = detect_file_type(file_path)

        readers = {
            "pdf": read_pdf,
            "docx": read_docx,
            "txt": read_txt,
            "markdown": read_markdown,
            "csv": read_csv,
            "xlsx": read_excel,
            "xls": read_excel,
            "pptx": read_pptx,
            "html": read_html,
        }

        reader = readers.get(file_type)

        if reader is None:
            raise ValueError(
                f"No reader available for file type: {file_type}"
            )

        return reader(file_path)

    def process_document(self, file_path: str) -> List[DocumentChunk]:
        """
        Process one document from file → DocumentChunk objects.
        """

        file_type = detect_file_type(file_path)

        pages = self.read_document(file_path)

        chunks: List[DocumentChunk] = []

        chunk_counter = 1

        for page in pages:

            cleaned_text = clean_text(page.text)

            if not cleaned_text:
                continue

            page_chunks = chunk_text_by_tokens(
                text=cleaned_text,
                chunk_size=self.chunk_size,
                overlap=self.overlap,
            )

            for chunk_text in page_chunks:

                chunk_id = (
                    f"{Path(file_path).stem}_"
                    f"chunk_{chunk_counter}"
                )

                metadata = dict(page.metadata)

                metadata.update(
                    {
                        "filename": Path(file_path).name,
                        "chunk_index": chunk_counter,
                    }
                )

                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        text=chunk_text,
                        source=file_path,
                        file_type=file_type,
                        page_number=page.page_number,
                        metadata=metadata,
                    )
                )

                chunk_counter += 1

        return chunks