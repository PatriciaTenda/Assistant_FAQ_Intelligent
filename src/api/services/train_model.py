import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# appeler la fonction load_dotenv pour charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Charger la clé du token
api_token = os.getenv("token_benchmark_faq")
if not api_token:
    raise ValueError("Le token de l'API HuggingFace requis pour la stratégie LLM")

# Configurer le client InferenceClient avec le token et un délai d'attente
client = InferenceClient(token=api_token, timeout=60)

 # definir le prompt pour le modele LLM
PROMPT_SYSTEM = """
            Tu es un assistant FAQ pour une collectivité territoriale française.

            Tu réponds aux questions des citoyens concernant :
            - L'état civil (naissance, mariage, décès, PACS...)
            - L'urbanisme (permis de construire, déclarations...)
            - Les déchets et l'environnement
            - Les transports et la petite enfance
            - L'action sociale et la vie associative
            - Les élections, le logement, la culture et le sport
            - La fiscalité locale et l'eau/assainissement

            Règles :
            1. Réponds UNIQUEMENT en français de manière claire et professionnelle
            2. Si tu n'es pas sûr, dis-le clairement
            3. Si la question sort de ton domaine, indique-le poliment
"""
    
# definir le modele
MODEL_NAME = os.getenv(
    "LLM_MODEL",
    "meta-llama/Llama-3.1-8B-Instruct"
)
       

def generate_answer(question: str) -> str:
    """
        Cette fonction recoit une question et retourne une réponse générée par le modèle LLM.
        
        args:
            question: La question posée par l'utilisateur.
        
        returns:
            La réponse générée par le modèle LLM.
    """
    
   
    # appeler modele LLM
    if not question.strip():
        raise ValueError("La question est vide. Veuillez fournir une question.")
    
    try:
        messages = [
            {"role": "system", "content": PROMPT_SYSTEM},
            {"role": "user", "content": question}
        ]

        reponse = client.chat_completion(
            model=MODEL_NAME,
            max_tokens=220,
            temperature=0.5,
            messages=messages,
        )
        
        if not reponse.choices or not reponse.choices[0].message.content:
            raise RuntimeError("Le modèle a retourné une réponse vide")
        
        answer = (reponse.choices[0].message.content or "").strip()
        
        return answer
    
    except RuntimeError as e:
        raise RuntimeError(
            "Le modele LLM n'a pas pu générer de réponse."
            " Veuillez réessayer plus tard."
        ) from e
    