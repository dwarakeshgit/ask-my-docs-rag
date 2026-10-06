from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile

from backend.app.api.schemas import UploadResponse


router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)


UPLOAD_DIR = Path("backend/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "/",
    response_model=UploadResponse,
)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
):
    file_path = UPLOAD_DIR / file.filename

    contents = await file.read()
    file_path.write_bytes(contents)

    # Get the single shared RAG service created when FastAPI started.
    rag_service = request.app.state.rag_service

    # Process and index the uploaded document.
    chunks = rag_service.index_document(
        file_path=str(file_path)
    )

    return {
        "message": "File uploaded and indexed successfully.",
        "filename": file.filename,
        "chunks_indexed": len(chunks),
    }