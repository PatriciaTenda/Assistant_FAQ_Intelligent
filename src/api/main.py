from fastapi import FastAPI
from src.api.routers.question_endpoint import router as question_router

app = FastAPI(
    title="Assistant FAQ Intelligent",
    version="1.0.0",    
)

@app.get("/")
def accueil():
    return {
        "message": "Bienvenue sur l'API de l'assistant FAQ intelligent. Utilisez les points de terminaison appropriés pour interagir avec le système."
    }

@app.get("/status")
def get_status():
    return {
        "status" : "L'API est opérationnelle et prête à recevoir des requêtes."
    }


app.include_router(question_router)