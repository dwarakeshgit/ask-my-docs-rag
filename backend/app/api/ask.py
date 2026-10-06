from fastapi import APIRouter, Request

from backend.app.api.schemas import AskRequest, AskResponse


router = APIRouter(
    prefix="/ask",
    tags=["Ask"],
)


@router.post(
    "/",
    response_model=AskResponse,
)
def ask_question(
    request: Request,
    ask_request: AskRequest,
):
    rag_service = request.app.state.rag_service

    result = rag_service.answer(
        question=ask_request.question
    )

    return result