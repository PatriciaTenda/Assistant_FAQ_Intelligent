"""
Classe de base pour les stratégies de réponse FAQ.

Ce module définit l'interface commune à toutes les stratégies.
Chaque stratégie (A, B, C) doit hériter de BaseStrategy et implémenter
les méthodes abstraites.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class FAQResponse:
    """
    Structure standardisée pour les réponses FAQ.
    
    Cette dataclass encapsule toutes les informations d'une réponse :
    - Le texte de la réponse
    - Le score de confiance
    - La stratégie utilisée
    - Les sources consultées
    - Les éventuelles erreurs
    
    Attributes:
        answer: La réponse textuelle
        confidence: Score de confiance entre 0 et 1
        strategy: Nom de la stratégie utilisée ("llm_only", "rag", "qa_extractive")
        sources: Liste des FAQ sources utilisées pour la réponse
        error: Message d'erreur si applicable
        metadata: Données supplémentaires (scores intermédiaires, etc.)
    
    Example:
        >>> response = FAQResponse(
        ...     answer="Le délai est de 5 jours ouvrés.",
        ...     confidence=0.85,
        ...     strategy="rag",
        ...     sources=[{"id": "FAQ_001", "question": "Quel délai ?"}]
        ... )
        >>> print(response.answer)
        Le délai est de 5 jours ouvrés.
    """
    answer: str
    confidence: float = 0.0
    strategy: str = ""
    sources: list[dict[str, Any]] = field(default_factory=list)
    error: str | None= None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convertit la réponse en dictionnaire."""
        return asdict(self)
    
    def __getitem__(self, key):
        """Permet l'accès par clé comme un dict (response["answer"])."""
        return getattr(self, key)
    
    def get(self, key, default=None):
        """Permet d'utiliser .get() comme un dict."""
        return getattr(self, key, default)


class BaseStrategy(ABC):
    """
    Classe abstraite définissant l'interface des stratégies FAQ.
    
    Chaque stratégie doit implémenter :
    - initialize() : Initialisation des ressources (modèles, index, etc.)
    - _generate_answer() : Logique de génération de réponse
    
    La méthode answer() est fournie et gère les erreurs automatiquement.
    
    Attributes:
        faq_base: Liste des entrées FAQ (dictionnaires avec 'question' et 'answer')
        _initialized: Flag indiquant si la stratégie est prête
    
    Example:
        >>> class MaStrategie(BaseStrategy):
        ...     def initialize(self):
        ...         self.model = charger_modele()
        ...     
        ...     def _generate_answer(self, question):
        ...         return FAQResponse(answer="...", confidence=0.8)
    """
    
    def __init__(self, faq_base: list[dict[str, Any]]):
        """
        Initialise la stratégie avec la base FAQ.
        
        Args:
            faq_base: Liste des entrées FAQ. Chaque entrée est un dict avec
                     au minimum les clés 'question' et 'answer'.
        
        Note:
            L'initialisation spécifique (chargement modèles, etc.) est déléguée
            à la méthode initialize() qui est appelée automatiquement.
        """
        # Stocker la base FAQ pour une utilisation ultérieure
        self.faq_base = faq_base

        # Flag d'initialisation - la stratégie n'est pas prête tant que initialize() n'est pas appelée
        self._initialized = False
        
        # Appeler l'initialisation spécifique de la stratégie
        self.initialize()

        # Marquer la stratégie comme initialisée après l'appel à initialize()
        self._initialized = True
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialise les ressources spécifiques à la stratégie.
        
        Cette méthode est appelée automatiquement par __init__.
        
        Utilisez-la pour :
        - Charger les modèles (embeddings, LLM, Q&A)
        - Construire les index de recherche
        - Configurer les clients API
        
        Raises:
            ValueError: Si une configuration requise est manquante
            RuntimeError: Si l'initialisation échoue
        """
        
    
    @abstractmethod
    def _generate_answer(self, question: str) -> FAQResponse:
        """
        Génère une réponse pour la question donnée.
        
        C'est la méthode principale à implémenter. Elle contient toute
        la logique spécifique de la stratégie.
        
        Args:
            question: La question posée par l'utilisateur
            
        Returns:
            FAQResponse contenant la réponse et les métadonnées
        
        Note:
            Cette méthode ne devrait pas gérer les exceptions - elles sont
            attrapées par answer() qui retourne une FAQResponse d'erreur.
        """
        
    
    def answer(self, question: str) -> FAQResponse:
        """
        Point d'entrée principal pour répondre à une question.
        
        Cette méthode :
        1. Vérifie que la stratégie est initialisée
        2. Appelle _generate_answer()
        3. Gère les exceptions et retourne une réponse d'erreur si besoin
        
        Args:
            question: La question de l'utilisateur
            
        Returns:
            FAQResponse structurée (toujours, même en cas d'erreur)
        """
        if not self._initialized:
            return FAQResponse(
                answer="Erreur: La stratégie n'est pas initialisée.",
                confidence=0.0,
                strategy=self.name,
                error="Strategy not initialized"
            )
        
        try:
            return self._generate_answer(question)
        except RuntimeError as e:
            logger.error(f"Erreur dans {self.name}: {e}")
            return FAQResponse(
                answer="Désolé, une erreur s'est produite lors du traitement.",
                confidence=0.0,
                strategy=self.name,
                error=str(e)
            )
    
    @property
    def name(self) -> str:
        """Retourne le nom de la classe de stratégie."""
        return self.__class__.__name__
    
    @property
    def description(self) -> str:
        """Retourne la docstring de la classe comme description."""
        return self.__doc__ or "Pas de description disponible"