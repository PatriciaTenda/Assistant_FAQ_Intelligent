import logging
import time

from fastapi import APIRouter, HTTPException, status
from src.api.schemas.question_validated import QuestionRequest, QuestionResponse
from src.api.services.llm_service import generate_answer

# Définir le logger
logger = logging.getLogger(__name__)

# Créer un routeur FastAPI 
router = APIRouter()

# Endpoint pour poser une question à l'assistant FAQ intelligent
@router.post(
    "/ask/", 
    tags=["Question"], 
    status_code=status.HTTP_200_OK,
    summary="Poser une question à l'assistant FAQ intelligent",
    response_model=QuestionResponse,
      responses={
        422: {"description": "Question invalide ou vide"},
        503: {"description": "Service LLM indisponible"},
    },
)
async def ask_question(request: QuestionRequest) -> QuestionResponse:
    """ Cette fonction traite la génération de réponse à une question posée par l'utilisateur. 
        Elle reçoit la question via un objet QuestionRequest et retourne la réponse générée 
        par le modèle LLM encapsulée dans un objet QuestionResponse.
        
        args:
            request: Un objet QuestionRequest contenant la question posée par l'utilisateur.
            
        returns:
            Un objet QuestionResponse contenant la réponse générée par le modèle LLM.
    """
    logger.info(
        "Nouvelle question reçue."
    )
    
    start_time = time.perf_counter()
    
    try:
        answer = await generate_answer(request.question)
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        logger.info(
            "Réponse générée avec succes | latence_ms= %.2f",
            latency_ms,
        )
        
        return QuestionResponse(
                answer=answer
            )
    except RuntimeError as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.error(
            "Erreur lors de la génération de la réponse | latency_ms= %2.f | erreur = %s",
            latency_ms,
            e
        )
        raise HTTPException(
            status_code= status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        ) from e
    
    