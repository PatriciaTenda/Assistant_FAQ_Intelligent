"""
Script d'évaluation des résultats de benchmark.

Ce script analyse les résultats du benchmark et calcule les métriques
d'évaluation pour chaque stratégie selon la grille définie.

Auteur: Patricia
Date: 27/06/2026
"""
import unicodedata
import json 
import csv  # noqa: F401
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple # noqa: F401
from dataclasses import dataclass
from collections import defaultdict # noqa: F401

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pondérations des critères d'évaluation
WEIGHTS = {
    "exactitude": 0.30,        # 30% - Informations clés présentes
    "pertinence": 0.20,        # 20% - Réponse en rapport avec la question
    "absence_hallucination": 0.20,  # 20% - Pas d'informations inventées
    "latence": 0.15,           # 15% - Temps de réponse
    "aveu_ignorance": 0.15     # 15% - Reconnaît ne pas savoir (hors sujet)
}

# Seuils de latence (en millisecondes)
LATENCY_THRESHOLDS = {
    "excellent": 500,    # < 500ms = score max
    "bon": 1000,         # < 1000ms = score moyen
    "acceptable": 2000,  # < 2000ms = score faible
    # > 2000ms = score minimal
}

# Liste des phrases d'aveu d'ignorance (hors sujet)
EXPRESSIONS_IGNORANCE = [
    "je ne sais pas",
    "je ne peux pas répondre",
    "hors de mon périmètre",
    "je n'ai pas d'information",
    "désolé, je ne peux pas",
    # ...
]

@dataclass
class QuestionEvaluation:
    """Évaluation d'une réponse sur une question."""
    question_id: str
    strategy: str
    exactitude_score: float      # 0-1
    pertinence_score: float      # 0-1
    hallucination_score: float   # 0-1 (1 = pas d'hallucination)
    latence_score: float         # 0-1
    aveu_ignorance_score: float  # 0-1 (uniquement pour questions hors sujet)
    score_global: float          # Score pondéré final
    details: Dict[str, Any]      # Détails supplémentaires


class BenchmarkEvaluator:
    """
    Évalue les résultats d'un benchmark selon la grille de critères.
    
    Cette classe analyse les réponses des stratégies et calcule des scores
    quantitatifs pour permettre une comparaison objective.
    """
    
    def __init__(
        self, 
        benchmark_results_path: str, 
        golden_set_path: str,
        output_dir: str
    ):
        """
        Initialise l'évaluateur.
        
        Args:
            benchmark_results_path: Chemin vers les résultats du benchmark
            golden_set_path: Chemin vers le golden set (pour les réponses attendues)
            output_dir: Répertoire de sortie pour les rapports
        """
        self.benchmark_results_path = Path(benchmark_results_path)
        self.golden_set_path = Path(golden_set_path)
        self.output_dir = Path(output_dir)
        #self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger les données
        self.benchmark_results = self._load_benchmark_results()
        self.golden_set = self._load_golden_set()
        
        # Index le golden set par ID pour accès rapide
        self.golden_index = {q["id"]: q for q in self.golden_set}
        
        # Résultats d'évaluation
        self.evaluations: List[QuestionEvaluation] = []
    
    def _load_benchmark_results(self) -> List[Dict[str, Any]]:
        """
        Charge les résultats du benchmark.
        
        Returns:
            Liste des résultats du benchmark
            
         Raises:
            FileNotFoundError: si le fichier de résultats est introuvable
            ValueError: si le contenu n'est pas un JSON valide
            
        TODO:
            1. Charger le fichier JSON des résultats
            2. Extraire la liste des résultats
            3. Retourner la liste
        """
        if not self.benchmark_results_path.exists():
            logger.error(f"Fichier de résultats introuvables: {self.benchmark_results_path}")
            raise FileNotFoundError(f"Fichier de résultats introuvables: {self.benchmark_results_path}")
        try:
            # 1. Charger le fichier JSON des résultats
            with open(self.benchmark_results_path, "r", encoding="utf-8") as f:
                data = json.load(f)    
            # 2. Extraire la liste des résultats  
                results = data.get("results", [])
            # 3. Retourner la liste
            return results
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du chargement des résultats: {e}")
            raise ValueError(f"Le contenu n'est pas un json valide : {e}") from e
    
    def _load_golden_set(self) -> List[Dict[str, Any]]:
        """
        Charge le golden set avec les réponses attendues.
        
        Returns:
            Liste des questions du golden set
        
        Raises:
            FileNotFoundError: si le fichier Golden_Set.json est introuvable
            ValueError: si le contenu n'est pas un JSON valide
        """
        if not self.golden_set_path.exists():
            logger.error(f"Fichier golden_set introuvable: {self.golden_set_path}")
            raise FileNotFoundError(f"Fichier golden_set introuvable: {self.golden_set_path}")
        try:   
            with open(self.golden_set_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                golden_set = data.get("golden_set", [])
            return golden_set
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du chargement du fichier golden_set: {e}")
            raise ValueError(f"Le contenu du golden_set n'est pas un json valide : {e}") from e
        
    
    def _normalize_text(self, text: str)-> str:
        """
            Cette methode normalise les textes pour faciliter la comparaison.
            args:
                text: texte à normaliser
            returns:
                texte normalisé (miniscule, sans accents)
        
        """
        # mettre en miniscule
        text = text.lower()
        # Décomposer les carractères accentués(lettre + accents)
        text = unicodedata.normalize("NFD", text)
        # Enlever les accents
        # Mn = Mark non spacing, 
        # c'est à dire les marks qui ne prennent pas de place (ex: accents)
        text_filtered = [c for c in text if unicodedata.category(c) != "Mn"]
        return "".join(text_filtered) 
        
       
    
    def evaluate_exactitude(
        self, 
        answer: str, 
        expected_keywords: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Évalue l'exactitude d'une réponse.
        
        L'exactitude mesure la présence des mots-clés attendus dans la réponse.
        
        Args:
            answer: Réponse générée par la stratégie
            expected_keywords: Mots-clés attendus (depuis le golden set)
            
        Returns:
            Tuple (score 0-1, détails)
            
        TODO:
            1. Normaliser la réponse (minuscules, sans accents si besoin)
            2. Pour chaque mot-clé attendu:
               - Vérifier s'il est présent dans la réponse
               - Compter les mots-clés trouvés
            3. Calculer le score: nb_trouvés / nb_attendus
            4. Retourner le score et les détails (mots trouvés/manquants)
            
        Note:
            - Si expected_keywords est vide, retourner 1.0 (pas de vérification)
            - La recherche doit être insensible à la casse
        """
                
        if not expected_keywords:
            score = 1.0
            details = {
                        "keywords_found" : [],
                        "keywords_missing" : [],
                        "score_exactitude" : score
                }
            return score, details
                
        # 1. Normaliser la réponse (minuscules, sans accents si besoin)
        answer_normalized = self._normalize_text(answer)
        expected_keywords_normalized = [self._normalize_text(k) for k in expected_keywords]
        
        # 2. Pour chaque mot-clé attendu, vérifier s'il est présent dans la réponse
        keywords_found = []
        keywords_missing = []
        for keywords in expected_keywords_normalized:
            if keywords in answer_normalized:
                keywords_found.append(keywords)                    
            else:
                keywords_missing.append(keywords)
        

        # 3. Calculer le score: nb_trouvés / nb_attendus
        score = len(keywords_found) / len(expected_keywords_normalized)
        details = {
                    "keywords_found" : keywords_found,
                    "keywords_missing" : keywords_missing,
                    "score_exactitude" : score
                }
        
        # 4. Retourner le score et les détails (mots trouvés/manquants)
        return (score, details)
        
        
    def evaluate_pertinence(
        self, 
        answer: str, 
        question: str,
        question_type: str
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Évalue la pertinence d'une réponse.
        
        La pertinence mesure si la réponse est en rapport avec la question.
        
        Args:
            answer: Réponse générée
            question: Question posée
            question_type: Type de question (direct_match, reformulation, hors_sujet, complexe)
            
        Returns:
            Tuple (score 0-1, détails)
            
        TODO:
            1. Pour les questions hors_sujet:
               - Une réponse "je ne sais pas" est pertinente (score = 1)
               - Une réponse avec contenu est non pertinente (score = 0)
            2. Pour les autres types:
               - Vérifier que la réponse n'est pas vide
               - Vérifier la longueur minimale (ex: > 20 caractères)
               - Heuristique: présence de mots de la question dans la réponse
            3. Retourner le score et les détails
            
        Heuristiques suggérées:
            - Réponse trop courte (< 20 car) = score faible
            - Réponse très longue mais sans rapport = score moyen
            - Utiliser la similarité lexicale comme indicateur
        """
        
        answer_clean = answer.strip()
        answer_normalized = self._normalize_text(answer_clean)
        question_normalized = self._normalize_text(question)
        
        expression_normalized = [
                            self._normalize_text(expr) 
                            for expr in EXPRESSIONS_IGNORANCE
        ]
        
        
        # 1. cas des réponses pour des questions de type "hors_sujet"    
        if question_type == "hors_sujet" :
            
            has_ignorance = any(expr in answer_normalized for expr in expression_normalized)
            
            score = 1.0 if has_ignorance else 0.0
            
            return score, {"pertinence" : ("aveu d'ignorance détecté" 
                                           if has_ignorance 
                                           else "réponse avec contenu et non pertinente"),
                           "has_ignorance" : has_ignorance,
                           "score_pertinence" : score                        
                        }
                    
                 
        # 2. cas des réponses pour des questions de type different de "hors_sujet"
        # Vérifier que la réponse n'est pas vide
        if not answer_clean:
            return 0.0, {"pertinence" : "Réponse vide",
                            "score_pertinence": 0.0}
        
        # Vérifier la longueur minimale (ex: > 20 caractères)
        if len(answer_clean) < 20 :
            score_longueur = len(answer_clean)/20       
        else :
            score_longueur = min(len(answer_clean)/20, 1.0) 
                    
        
        # Vérifier la présence de mots de la question dans la réponse
        question_words = set(question_normalized.split())
        answer_words = set(answer_normalized.split())
        
        if not question_words:
            score_lexical = 0.0
            words_found = []
        else:
            words_found = sorted(question_words & answer_words)
            score_lexical = len(words_found) / len(question_words)
    
                    
        # 3. Retourner le score et les détails
        score = (score_longueur + score_lexical) / 2
        details = {
            "pertinence" : "Score moyen basé sur longueur et similarité lexicale",
            "score_longueur": score_longueur,
            "score_lexical": score_lexical,
            "Mots_question_trouvés" : words_found,
            "score_pertinence": score
        }                    
        return score, details
    
    
    def evaluate_hallucination(
        self, 
        answer: str, 
        expected_summary: str,
        question_type: str
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Évalue l'absence d'hallucination dans une réponse.
        
        Détecte si la réponse contient des informations manifestement fausses
        ou inventées.
        
        Args:
            answer: Réponse générée
            expected_summary: Résumé de la réponse attendue
            question_type: Type de question
            
        Returns:
            Tuple (score 0-1, détails) où 1 = pas d'hallucination
            
        TODO:
            1. Pour les questions hors_sujet:
               - Si la réponse affirme quelque chose de factuel = hallucination
               - Si la réponse avoue l'ignorance = pas d'hallucination
            2. Pour les autres types:
               - Détecter les patterns d'hallucination:
                 * Numéros de téléphone inventés (ex: formats incorrects)
                 * URLs inventées
                 * Dates/montants très différents de ceux attendus
            3. Score par défaut: 0.8 (bénéfice du doute)
            
        Note:
            Cette évaluation est complexe et approximative en automatique.
            Une évaluation manuelle est recommandée pour la validation finale.
        """
        # TODO: Implémenter la détection d'hallucination
        raise NotImplementedError("Implémenter evaluate_hallucination")
    
    def evaluate_latence(self, latency_ms: float) -> Tuple[float, Dict[str, Any]]:
        """
        Évalue le score de latence.
        
        Args:
            latency_ms: Latence en millisecondes
            
        Returns:
            Tuple (score 0-1, détails)
            
        TODO:
            1. Comparer la latence aux seuils définis dans LATENCY_THRESHOLDS
            2. Attribuer un score:
               - < 500ms: 1.0
               - 500-1000ms: 0.8
               - 1000-2000ms: 0.5
               - > 2000ms: 0.2
            3. Retourner le score et les détails
        """
        # TODO: Implémenter l'évaluation de latence
        raise NotImplementedError("Implémenter evaluate_latence")
    
    def evaluate_aveu_ignorance(
        self, 
        answer: str, 
        question_type: str
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Évalue la capacité à avouer son ignorance.
        
        Pour les questions hors sujet, le système doit reconnaître
        qu'il ne peut pas répondre.
        
        Args:
            answer: Réponse générée
            question_type: Type de question
            
        Returns:
            Tuple (score 0-1, détails)
            
        TODO:
            1. Si question_type != "hors_sujet":
               - Retourner 1.0 (non applicable, pas de pénalité)
            2. Si question_type == "hors_sujet":
               - Détecter les phrases d'aveu d'ignorance:
                 * "je ne sais pas"
                 * "je ne peux pas répondre"
                 * "cette question ne concerne pas"
                 * "hors de mon domaine"
                 * etc.
               - Si détecté: score = 1.0
               - Sinon: score = 0.0
            3. Retourner le score et les détails
        """
        # TODO: Implémenter l'évaluation d'aveu d'ignorance
        raise NotImplementedError("Implémenter evaluate_aveu_ignorance")
    
    def evaluate_single_result(
        self, 
        result: Dict[str, Any]
    ) -> QuestionEvaluation:
        """
        Évalue un résultat de benchmark unique.
        
        Args:
            result: Résultat du benchmark pour une question/stratégie
            
        Returns:
            QuestionEvaluation avec tous les scores
            
        TODO:
            1. Récupérer la question correspondante dans le golden set
            2. Appeler chaque méthode d'évaluation:
               - evaluate_exactitude()
               - evaluate_pertinence()
               - evaluate_hallucination()
               - evaluate_latence()
               - evaluate_aveu_ignorance()
            3. Calculer le score global pondéré:
               score = sum(score_i * weight_i pour i dans critères)
            4. Créer et retourner la QuestionEvaluation
        """
        # TODO: Implémenter l'évaluation d'un résultat
        raise NotImplementedError("Implémenter evaluate_single_result")
    
    def run_evaluation(self) -> List[QuestionEvaluation]:
        """
        Exécute l'évaluation complète de tous les résultats.
        
        Returns:
            Liste de toutes les QuestionEvaluation
            
        TODO:
            1. Pour chaque résultat dans self.benchmark_results:
               - Appeler evaluate_single_result()
               - Ajouter à self.evaluations
               - Logger la progression
            2. Retourner self.evaluations
        """
        # TODO: Implémenter l'évaluation complète
        raise NotImplementedError("Implémenter run_evaluation")
    
    def generate_strategy_scores(self) -> Dict[str, Dict[str, float]]:
        """
        Calcule les scores agrégés par stratégie.
        
        Returns:
            Dictionnaire {stratégie: {critère: score_moyen}}
            
        TODO:
            1. Grouper les évaluations par stratégie
            2. Pour chaque stratégie, calculer la moyenne de chaque critère
            3. Calculer le score global moyen
            4. Retourner les scores agrégés
        """
        # TODO: Implémenter le calcul des scores par stratégie
        raise NotImplementedError("Implémenter generate_strategy_scores")
    
    def generate_recommendation(self) -> Dict[str, Any]:
        """
        Génère une recommandation de stratégie basée sur les scores.
        
        Returns:
            Dictionnaire avec:
            - stratégie_recommandée
            - justification
            - scores_comparatifs
            - points_forts/points_faibles par stratégie
            
        TODO:
            1. Calculer les scores par stratégie
            2. Identifier la stratégie avec le meilleur score global
            3. Analyser les points forts/faibles de chaque stratégie
            4. Rédiger une justification
            5. Retourner la recommandation structurée
        """
        # TODO: Implémenter la génération de recommandation
        raise NotImplementedError("Implémenter generate_recommendation")
    
    def export_csv(self, filename: str = "evaluation_results.csv") -> Path:
        """
        Exporte les résultats détaillés au format CSV.
        
        Args:
            filename: Nom du fichier de sortie
            
        Returns:
            Chemin du fichier créé
            
        TODO:
            1. Définir les colonnes du CSV:
               - question_id, strategy, question_type
               - exactitude, pertinence, hallucination, latence, aveu_ignorance
               - score_global
            2. Écrire l'en-tête
            3. Écrire chaque évaluation
            4. Retourner le chemin du fichier
        """
        # TODO: Implémenter l'export CSV
        raise NotImplementedError("Implémenter export_csv")
    
    def export_report(self, filename: str = "evaluation_report.json") -> Path:
        """
        Exporte le rapport complet au format JSON.
        
        Args:
            filename: Nom du fichier de sortie
            
        Returns:
            Chemin du fichier créé
            
        TODO:
            1. Créer la structure du rapport:
               - metadata (date, fichiers sources)
               - scores_par_strategie
               - recommandation
               - evaluations_detaillees
            2. Sauvegarder le fichier JSON
            3. Retourner le chemin du fichier
        """
        # TODO: Implémenter l'export du rapport
        raise NotImplementedError("Implémenter export_report")


def main():
    """
    Point d'entrée principal du script d'évaluation.
    
    Usage:
        python evaluate_results.py <benchmark_results.json>
        
    TODO:
        1. Parser les arguments (chemin du fichier de résultats)
        2. Créer l'évaluateur
        3. Lancer l'évaluation
        4. Exporter les résultats (CSV et JSON)
        5. Afficher la recommandation
    """
    import sys
    
    # Vérifier les arguments
    if len(sys.argv) < 2:
        print("Usage: python evaluate_results.py <benchmark_results.json>")
        print("Exemple: python evaluate_results.py results/benchmark_20250115_143022.json")
        sys.exit(1)
    
    benchmark_results_path = sys.argv[1]
    
    # Configuration des chemins
    project_root = Path(__file__).parent.parent
    golden_set_path = project_root / "data" / "golden_set.json"
    output_dir = project_root / "results"
    
    # TODO: Implémenter le main
    # 1. Créer l'évaluateur
    # 2. Lancer l'évaluation
    # 3. Exporter les résultats
    # 4. Afficher la recommandation
    
    logger.info("Évaluation terminée.")


if __name__ == "__main__":
    main()