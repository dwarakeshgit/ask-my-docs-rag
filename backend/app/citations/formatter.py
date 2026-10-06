from pathlib import Path
from typing import Dict, Any


class CitationFormatter:
    def format_citation(self, evidence: Dict[str, Any]) -> str:
        source = evidence.get("source", "Unknown source")
        filename = evidence.get("metadata", {}).get("filename")

        if not filename:
            filename = Path(source).name if source else "Unknown source"

        page_number = evidence.get("page_number")

        if page_number is not None:
            return f"{filename}, Page {page_number}"

        return filename