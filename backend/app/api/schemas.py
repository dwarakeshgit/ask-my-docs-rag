from typing import List, Optional

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sufficient: bool
    reason: str
    citations: List[str]


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_indexed: int


class DocumentSummary(BaseModel):
    filename: str
    file_type: Optional[str] = None
    chunks: int


class DocumentsResponse(BaseModel):
    documents: List[DocumentSummary]
    count: int