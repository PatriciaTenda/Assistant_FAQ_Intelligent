from fastapi import APIRouter, status
from src.api.schemas.question_validated import (QuestionRequest,
                                                QuestionResponse)

router = APIRouter()

@router.post(
    "/ask/", 
    tags=["Question"], 
    status_code=status.HTTP_200_OK,
    summary="Poser une question à l'assistant FAQ intelligent",
    response_model=QuestionResponse,
)
def ask_question(request: QuestionRequest) -> QuestionResponse:
    return QuestionResponse(
        answer=f"Question reçue: {request.question}"
    )