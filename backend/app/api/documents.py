from fastapi import APIRouter, Request

from backend.app.api.schemas import DocumentsResponse


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "/",
    response_model=DocumentsResponse,
)
def get_documents(request: Request):
    """
    Return all documents currently indexed in the RAG system.
    """

    rag_service = request.app.state.rag_service

    documents = rag_service.list_documents()

    return {
        "documents": documents,
        "count": len(documents),
    }