"""
Stratégie A : LLM Seul
Cette stratégie utilise uniquement un modèle de langage (LLM)
pour générer les réponses aux questions des citoyens.

"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
# Configurer le chemin pour le module et l'ajouter dans le repertoire parent
root_path = Path(__file__).resolve().parents[1]
print(f"Root path: {root_path}")
sys.path.insert(0, str(root_path))
from strategies.base import BaseStrategy, FAQResponse  # noqa: E402


# Chargement des variables d'environnement
load_dotenv()

token_benchmark_faq = os.getenv("token_benchmark_faq")

# Configuration du logger
logger = logging.getLogger(__name__)


class StrategyALLM(BaseStrategy):
    """
    Stratégie utilisant uniquement un LLM pour générer les réponses.
    """
    # Fonction d'initialisation de la stratégie
    def initialize(self) -> None:
        """Initialise le client LLM."""
        self.model_name = os.getenv(
            "LLM_MODEL", 
            "meta-llama/Llama-3.1-8B-Instruct"
        )
        self.api_token = token_benchmark_faq
        
        if not self.api_token:
            raise ValueError("Le token de l'API HuggingFace requis pour la stratégie LLM")
        
        self.client = InferenceClient(token=self.api_token, timeout=60)
        
        self.system_prompt = """Tu es un assistant FAQ pour une collectivité territoriale française.

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
            3. Si la question sort de ton domaine, indique-le poliment"""

        logger.info(f"StrategyALLM initialisée: {self.model_name}")
    
    # Fonction de génération de réponse
    def _generate_answer(self, question: str) -> FAQResponse:
        """Génère une réponse avec le LLM."""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question}
            ]
            
            response = self.client.chat_completion(
                model=self.model_name,
                messages=messages,
                max_tokens=220,
                temperature=0.5
            )
            
            answer_text = (response.choices[0].message.content or "").strip()     

            # Détecter les indicateurs d'incertitude pour ajuster la confiance
            if answer_text == "":
                confidence = 0.0
            else:
                confidence = self._estimate_confidence(answer_text)
            return FAQResponse(
                answer=answer_text,
                confidence=confidence,
                strategy="llm_only",
                sources=[],
                metadata={"model": self.model_name}
            )
            
        except Exception as e:
            logger.error(f"Erreur LLM: {e}")
            return FAQResponse(
                answer="Désolé, je ne peux pas répondre pour le moment.",
                confidence=0.0,
                strategy="llm_only",
                error=str(e)
            )
        
    # Fonction d'estimation de la confiance    
    def _estimate_confidence(self, response: str) -> float:
        """
        Estime un score de confiance basé sur la réponse du LLM.
        cette fonction implémente une extimation simple pour estimer la confiance.
        
        A faire :
        - Chercher des marqueurs d'incertitude ("je ne suis pas sûr", "peut-être")
        - Chercher des aveux d'ignorance ("hors de mon domaine", "je ne peux pas")
        - Vérifier que la réponse n'est pas trop courte
        
        Args:
            response: La réponse générée par le LLM
            
        Returns:
            Score entre 0.0 et 1.0
        """

        # Exemple de marqueurs d'incertitude et d'aveux d'ignorance
        ignorance_indicators = [
            "je ne peux pas répondre",
            "je ne suis pas en mesure",
            "hors de mon domaine",
        ]

        # Cette variable retourne True ou False selon la présence d'indicateurs d'incertitude 
        # correspondant à ce qui est définie comme exemple dans la liste ignorance_indicators
        is_uncertain = any(indicator in response.lower() for indicator in ignorance_indicators)

        # retourne 0.5 si un indicateur d'incertitude est détecté, sinon 0.7
        return 0.5 if is_uncertain else 0.7

# point d'entrée pour tester la stratégie
if __name__ == "__main__":

    import json
    from dotenv import load_dotenv
    load_dotenv()

    # charger les questions du faq_base
    with open("data/faq_base.json", "r", encoding="utf-8") as f:
        data_faq_base = json.load(f)
        faq_base = data_faq_base.get("faq", [])

    # Créer un objet de la strategie A
    strategy = StrategyALLM(faq_base= faq_base)

    # Tester la génération de réponse pour une question spécifique
    question = "Comment déclarer une naissance à la mairie ?"
    response = strategy.answer(question)

    print(f"Question : {question}")
    print(f"Réponse : {response.answer}")
    print(f"Confiance : {response.confidence}")
