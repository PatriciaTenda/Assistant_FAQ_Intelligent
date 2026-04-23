"""
Stratégie B : RAG Simplifié
Cette stratégie combine une recherche sémantique simple dans la FAQ avec une génération de réponse par un LLM.
- Recherche sémantique : Utilise un modèle d'embeddings pour trouver les FAQ les plus similaires à la question posée.
- Génération LLM : Fournit les FAQ similaires comme contexte à un modèle de langage pour générer une réponse plus complète et adaptée à la question de l'utilisateur.   
Le code de cette stratégie se trouve dans `src/strategies/strategy_B_RAG.py` et est implémenté dans la classe `StrategyBRAG`.

args: 
- `EMBEDDING_MODEL` : nom du modèle d'embeddings à utiliser (ex. "sentence-transformers/all-MiniLM-L6-v2")
- `LLM_MODEL` : nom du modèle de langage à utiliser pour la génération (ex. "mistralai/Mistral-7B-Instruct-v0.2")
- `HF_API_TOKEN` : token d'authentification pour Hugging Face (nécessaire pour les appels au LLM)
- `TOP_K_RESULTS` : nombre de FAQ similaires à récupérer pour le contexte (ex. 3)
- `CONFIDENCE_THRESHOLD` : seuil de confiance pour décider si les FAQ similaires sont suffisamment pertinentes pour être utilisées dans la génération (ex. 0.5)
- `FAQ_BASE_PATH` : chemin vers la base de données FAQ (ex. "data/faq_base.json")  

returns:
- `FAQResponse` : un objet contenant la réponse générée, le score de confiance, la stratégie utilisée, les sources (FAQ similaires) et les éventuelles erreurs.
"""

import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer, util
from huggingface_hub import InferenceClient

from pathlib import Path
import sys

root_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_path))
from strategies.base import BaseStrategy, FAQResponse #noqa: E402

# Chargement des variables d'environnement
load_dotenv()

# Set up les variables d'environnement nécessaires
token_benchmark_faq = os.getenv("token_benchmark_faq")

# Configuration du logger
logging.basicConfig(
    level = logging.INFO,
    format= "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ===== Classe de mise en œuvre de la stratégie B RAG =====
class StrategyBRAG(BaseStrategy):
    """
    Stratégie RAG : Recherche sémantique + Génération LLM.
    """
    
    # = = = = = Méthode d'initialisation du RAG = = = = =
    def initialize(self) -> None:
        """Initialise les modèles et l'index."""
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.llm_model_name = os.getenv(
            "LLM_MODEL",
            "meta-llama/Llama-3.1-8B-Instruct"
        )
        self.api_token = os.getenv("HF_API_TOKEN", token_benchmark_faq)
        self.top_k = int(os.getenv("TOP_K_RESULTS", 2))
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", 0.5))
        
        if not self.api_token:
            raise ValueError("HF_API_TOKEN requis")
        
        # Modèle d'embeddings (local)
        logger.info(f"Chargement embeddings: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Créer le client LLM
        self.llm_client = InferenceClient(token=self.api_token, timeout=60)
        
        # Contruire l' index
        self._build_index()
        logger.info(f"StrategyBRAG initialisée: {len(self.faq_base)} FAQ")

    # = = = = = Méthodes pour la construction de l'index = = = = =
    def _build_index(self) -> None:

        """Construit l'index des embeddings pour retrouver facillement les vecteurs dans la liste."""

        self.faq_texts = []
        for faq in self.faq_base:
            text = f"{faq['question']} {faq.get('answer', '')}"
            self.faq_texts.append(text)
        
        self.faq_embeddings = self.embedding_model.encode(
            self.faq_texts,
            convert_to_tensor=True,
            show_progress_bar=False
        )

    # = = = = = Méthodes pour la recherche de FAQ similaires = = = = =
    def _search_similar(self, question: str) -> List[Dict[str, Any]]:

        """Recherche les FAQ similaires."""

        q_emb = self.embedding_model.encode(question, convert_to_tensor=True)
        similarities = util.cos_sim(q_emb, self.faq_embeddings)[0]
        top_indices = similarities.argsort(descending=True)[:self.top_k]
        
        # Construire la liste des FAQ similaires avec leurs scores
        results = []
        for idx in top_indices:
            idx = int(idx)
            results.append({
                "faq": self.faq_base[idx],
                "score": float(similarities[idx])
            })
        return results  
    
    # = = = = = Méthodes pour la génération de réponse avec le LLM = = = = =
    def _build_context(self, similar_faqs: List[Dict[str, Any]]) -> str:
        """Construit le contexte pour le LLM."""
        parts = []
        for i, item in enumerate(similar_faqs, 1):
            faq = item["faq"]
            parts.append(f"[FAQ {i}]\nQ: {faq['question']}\nR: {faq['answer']}\n")
        return "\n".join(parts)
    
    # = = = = = Méthode pour appeler le LLM = = = = =
    def _call_llm(self, question: str, context: str) -> str:

        """Appelle le LLM avec le contexte."""

        system_prompt = """
                            Tu es un assistant FAQ pour une collectivité territoriale française.
                            Réponds UNIQUEMENT en français et en te basant sur le contexte fourni.
                            Si le contexte ne permet pas de répondre, dis-le clairement en français.
                            citer uniquement des éléments présents dans le contexte.
                            Si une information est absente, dire simplement "je ne sais pas".
                            Demande une réponse sous forme de bullet points extraits du contexte.
                        """

        user_prompt = f"""
                          Contexte (FAQ officielles): {context}
                          Question: {question}
                          Réponds de manière claire et concise.
                      """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.llm_client.chat_completion(
            model=self.llm_model_name,
            messages=messages,
            max_tokens=220,
            temperature=0.3
        )        
        return (response.choices[0].message.content or "").strip()
    

    #= = = = = Interface principale de la stratégie = = = = =
    def _generate_answer(self, question: str) -> FAQResponse:
        """Génère une réponse avec RAG."""
        try:
            similar_faqs = self._search_similar(question)
            best_score = similar_faqs[0]["score"] if similar_faqs else 0
            
            if best_score < self.confidence_threshold:
                return FAQResponse(
                    answer="Je n'ai pas trouvé d'information pertinente dans notre FAQ.",
                    confidence=best_score,
                    strategy="rag",
                    sources=[]
                )
            
            context = self._build_context(similar_faqs)
            answer_text = self._call_llm(question, context)
            
            sources = [
                {
                    "id": item["faq"].get("id"),
                    "question": item["faq"]["question"],
                    "score": round(item["score"], 3)
                }
                for item in similar_faqs
            ]
            
            return FAQResponse(
                answer=answer_text,
                confidence=best_score,
                strategy="rag",
                sources=sources
            )
            
        except Exception as e:
            logger.error(f"Erreur RAG: {e}")
            return FAQResponse(
                answer="Désolé, une erreur s'est produite.",
                confidence=0.0,
                strategy="rag",
                error=str(e)
            )
        


if __name__ == "__main__":
    print("Stratégie B (RAG)")

    import json
    from dotenv import load_dotenv
    load_dotenv()

    token_benchmark_faq = os.getenv("token_benchmark_faq")

    # charger les questions du faq_base
    with open("data/faq_base.json", "r", encoding="utf-8") as f:
        data_faq_base = json.load(f)
        faq_base = data_faq_base.get("faq", [])

    # Créer un objet de la strategie B
    strategy = StrategyBRAG(faq_base= faq_base)

    # Tester la génération de réponse pour une question spécifique
    question = "Comment déclarer une naissance à la mairie ?"
    similar_faqs = strategy._search_similar(question)  # Récuperer les top-k FAQ similaires pour une question spécifique
    response = strategy.answer(question)


    print(f"Question : {question}")
    print(f"Réponse : {response.answer}")
    print(f"top-k : {similar_faqs}")
    print(f"Confidence : {response.confidence}")
