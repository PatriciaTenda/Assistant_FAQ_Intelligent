import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from src.api.routers.question_endpoint import router as question_router

# Configurer le logger
logging.basicConfig(level = logging.INFO,
                    format = "%(asctime)s - %(levelname)s - %(message)s" 
)

# Définir l'application FastAPI
app = FastAPI(
    title="Assistant FAQ Intelligent",
    version="1.0.0",    
)

# endpoint pour vérifier l'état de santé de l'application
@app.get("/status", tags=["Monitoring"])
def get_status():
    return {
        "status" : "healthy",
        "version": app.version
    }
# endpoint pour la page d'accueil de l'API   
@app.get("/", tags=["System"])
def accueil():
    return {
        "message": "Bienvenue sur l'API de l'assistant FAQ intelligent."
    }

# Inclure le routeur de l'endpoint de question dans l'application FastAPI
app.include_router(question_router, tags=["Answer"])

# Configurer l'instrumentation Prometheus pour la surveillance des métriques
Instrumentator().instrument(app).expose(app, endpoint="/metrics", tags=["Monitoring"])