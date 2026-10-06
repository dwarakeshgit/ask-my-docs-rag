from typing import Optional

from pydantic import BaseModel, Field


class DocumentPage(BaseModel):

    text: str

    source: str

    file_type: str

    page_number: Optional[int] = None

    metadata: dict = Field(default_factory=dict)


class DocumentChunk(BaseModel):

    chunk_id: str

    text: str

    source: str

    file_type: str

    page_number: Optional[int] = None

    metadata: dict = Field(default_factory=dict)