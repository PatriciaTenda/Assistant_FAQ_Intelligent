# python -m pytest src/tests/test_question_endpoint.py -v

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from src.api.main import app

# créer un client de test pour l'application FastAPI
client = TestClient(app)

def test_question_vide_retourne_422():
    """ 
        TestClient → simule l’utilisateur
        client.post → envoie la requête
        assert → vérifie le résultat
    """
    
    # exécuter une requete POST avec une question vide
    reponse = client.post(
        "/ask/",
        json={"question": ""}
    )
    
    # vérifier que le code de statut de la réponse est 422 (Unprocessable Entity)
    assert reponse.status_code == 422
    
    
    
def test_champ_supplementaire_retourne_422():
    # exécuter une requete POST avec un champ supplémentaire non défini dans le schéma
    reponse = client.post(
        "/ask/",
        json={"question": "quelles sont les horaires de la décheterie ?", "ville": "Paris"}
    )
    
    # Vérifier que le code statut de la réponse est 422 (Unprocessable Entity)
    assert reponse.status_code == 422
    
    
def test_question_valide_retourne_200():
    with patch(
        "src.api.routers.question_endpoint.generate_answer", 
        new=AsyncMock(
            return_value= "reponse simulée"
        )
    ):
        
        # exécuter une requete POST avec une question valide
        reponse = client.post(
            "/ask/",
            json={
                "question": "Quelles sont les horaires de la decheterie?"
            }
        )        
    
        # vérifier que le code statut est 200_ok
        assert reponse.status_code == 200
        assert reponse.json() == {
            "answer": "reponse simulée"
        }
        
def test_service_llm_indisponible_retourne_503():
    with patch(
        "src.api.routers.question_endpoint.generate_answer",
        new=AsyncMock(side_effect=RuntimeError("Le service LLM est indisponible. Veuillez réessayer plus tard."))
    ):
        reponse = client.post(
            "/ask/",
            json={
                "question": "Quelles sont les horaires de la decheterie?"
            }
        )
        
        assert reponse.status_code == 503
        assert reponse.json() == {
            "detail": "Le service LLM est indisponible. Veuillez réessayer plus tard."
        }