"""
Script d'évaluation des résultats de benchmark.

Ce script analyse les résultats du benchmark et calcule les métriques
d'évaluation pour chaque stratégie selon la grille définie.

Auteur: Patricia
Date: 27/06/2026
"""
import csv
import json
import logging
import re
import unicodedata
from collections import defaultdict  # noqa: F401
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    "hallucination": 0.20,     # 20% - Pas d'informations inventées
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
    question_type: str
    exactitude_score: float      # 0-1
    pertinence_score: float      # 0-1
    hallucination_score: float   # 0-1 (1 = pas d'hallucination)
    latence_score: float         # 0-1
    aveu_ignorance_score: float  # 0-1 (uniquement pour questions hors sujet)
    score_global: float          # Score pondéré final
    details: dict[str, Any]      # Détails supplémentaires


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
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger les données
        self.benchmark_results = self._load_benchmark_results()
        self.golden_set = self._load_golden_set()
        
        # Index le golden set par ID pour accès rapide
        self.golden_index = {q["id"]: q for q in self.golden_set}
        
        # Résultats d'évaluation
        self.evaluations: list[QuestionEvaluation] = []
    
    def _load_benchmark_results(self) -> list[dict[str, Any]]:
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
    
    def _load_golden_set(self) -> list[dict[str, Any]]:
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
        # Joindre les caractères filtrés pour reformer le texte sans accents
        text_join = "".join(text_filtered) 
        # Enlever les autres caractères non alphanumériques (ponctuation, etc.)
        text_cleaned = re.sub(r'[^a-z0-9\s]', "", text_join)
        return text_cleaned
        
       
    
    def evaluate_exactitude(
        self, 
        answer: str, 
        expected_keywords: list[str]
    ) -> tuple[float, dict[str, Any]]:
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
    ) -> tuple[float, dict[str, Any]]:
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
    ) -> tuple[float, dict[str, Any]]:
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
        answer_cleaned = answer.strip()
        answer_normalized = self._normalize_text(answer_cleaned)
        
        expression_normalized = [ self._normalize_text(expr) 
                                  for expr in EXPRESSIONS_IGNORANCE 
        ]
        
        # Evaluer l'absence d'hallucination sur les questions de type "hors_sujet"
        if question_type == "hors_sujet" :
            
            has_ignorance = any(expr in answer_normalized for expr in expression_normalized)
            
            score = 1.0 if has_ignorance else 0.0
            
            return score, {
                            "hallucination" :("aveu d'ignorance détecté" 
                                              if has_ignorance
                                              else "réponse avec contenu inventé") ,
                            "has_ignorance" : has_ignorance,
                            "score_hallucination" : score
            }
            
        # 2. Pour les autres types de questions, on peut comparer la réponse à un résumé attendu
        score = 0.8  # Score par défaut (bénéfice du doute)
        suspects_phone = []
        suspects_url = []
        amounts_suspects = set()
        dates_suspects = set()
        
        # Vérifier le numéro de téléphone au format incorrect (ex: 123-456-7890)
        phones_found = re.findall(r'\b0\d[\d\s.\-]{7,}\d\b', answer_cleaned) 
        for number in phones_found:
            chiffre = re.sub(r'\D', "", number)  # Retirer les caractères non numériques
            if len(chiffre) != 10 :
                suspects_phone.append(number)
                score -= 0.1
                
        # Vérifier les URLs au format incorrect (ex: http://example.com)
        urls_found = re.findall(r'\b[\w-]+\.(?:fr|gouv\.fr|com|org|net)\b', answer_cleaned)
        urls_found_expected = re.findall(r'\b[\w-]+\.(?:fr|gouv\.fr|com|org|net)\b', expected_summary)
        for url in urls_found:
            if url not in urls_found_expected:
                suspects_url.append(url)
                score -= 0.1
                
        # Vérifier les montants au format incorrect (ex: 1000€, 1000 $)
        amounts_found = re.findall(r'\b\d*[.,]?\d+\s*€\b', answer_cleaned)
        amounts_expected_found = re.findall(r'\b\d+[.,]?\d*\s*€\b', expected_summary)
        
        if amounts_found and amounts_expected_found:
            amounts = set(amounts_found) 
            amounts_expected = set(amounts_expected_found)
            amounts_suspects = amounts - amounts_expected
            score -= 0.1 * len(amounts_suspects)
            
            
        # Vérifier les dates au format incorrect (ex: 31/02/2025)
        dates_found = re.findall(r'\b\d+(?:jour|mois|semaine|année)s?\b', answer_cleaned)
        dates_expected_found = re.findall(r'\b\d+(?:jour|mois|semaine|année)s?\b', expected_summary)
        
        if dates_found and dates_expected_found:
            dates = set(dates_found) 
            dates_expected = set(dates_expected_found)
            dates_suspects = dates - dates_expected
            score -= 0.1 * len(dates_suspects)
            
        # 3. score et details
        return max(score, 0.0), {
                    "suspects_phone": suspects_phone,
                    "suspects_url": suspects_url,
                    "suspects_amounts": sorted(amounts_suspects),
                    "suspects_dates": sorted(dates_suspects),
                    "score_hallucination": max(score, 0.0)
               }
    
    
    
    def evaluate_latence(self, latency_ms: float) -> tuple[float, dict[str, Any]]:
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
        # Comparer la latence aux seuils définis dans LATENCY_THRESHOLDS et attribuer un score
        
        if latency_ms < LATENCY_THRESHOLDS["excellent"]:
            score = 1.0
        elif latency_ms < LATENCY_THRESHOLDS["bon"]:
            score = 0.8
        elif latency_ms < LATENCY_THRESHOLDS["acceptable"]:
            score = 0.5
        else:
            score = 0.2

        return score, {"latency_ms": latency_ms, 
                       "score_latence": score
        }
        
    
        
    def evaluate_aveu_ignorance(
        self, 
        answer: str, 
        question_type: str
    ) -> tuple[float, dict[str, Any]]:
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
        # Evaluation de l'aveu d'ignorance pour les questions "hors sujet"
        if  question_type != "hors_sujet":
            details = {
                "applicable": False,
                "type": question_type,
                "has_ignorance": False,
                "matched_expressions": None,
                "reason": "Non applicable pour les questions de type differents de 'hors_sujet'",                
            }
            return 1.0, details
        
        # Détection des phrases d'aveu d'ignorance
        normalized_answer = self._normalize_text(answer)
        normalized_expressions = [
            self._normalize_text(phrase)
            for phrase in EXPRESSIONS_IGNORANCE
        ]
        matched_expression = next(
            (phrase for phrase in normalized_expressions
                if phrase in normalized_answer),
            None
    )
        ignorance_detected = matched_expression is not None
        score = 1.0 if ignorance_detected else 0.0 
        details = { 
                    "applicable": True,
                    "type": question_type,
                    "has_ignorance": ignorance_detected,
                    "matched_expression": matched_expression,
                    "reason": ("Aveu d'ignorance détecté !" if ignorance_detected else "la question n'est pas reconnu comme hors-sujet")
        }
        return score, details
            
                             
    def evaluate_single_result(
        self, 
        result: dict[str, Any]
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
        # Recupérer les informations du résultat
        question_id = result.get("question_id")
        answer = result.get("answer", "")
        latency_ms = result.get("latency_ms", 0.0)
        strategy = result.get("strategy", "unknown")
        question_type = result.get("question_type", "unknown")
        
        # Récupérer la question correspondante dans le golden set
        golden_question = self.golden_index.get(question_id)
        if golden_question is None:
            golden_question = self.golden_index.get(str(question_id))
        
        if golden_question is None:
            raise ValueError(f"La question avec l'ID {question_id} est introuvable dans le golden set.")
        
        question_id = str(golden_question.get("id"))
        question = str(golden_question.get("question"))
        question_type = str(golden_question.get("type"))
        expected_answer = str(golden_question.get("expected_answer_summary"))
        expected_keywords = golden_question.get("expected_keywords", [])
            
        exactitude_score, exactitude_details = self.evaluate_exactitude(
                                                answer = answer, 
                                                expected_keywords=expected_keywords
                                            )
        pertinence_score, pertinence_details = self.evaluate_pertinence(
                                                answer = answer, question=question, 
                                                question_type = question_type
                                            )
        hallucination_score, hallucination_details = self.evaluate_hallucination(
                                                answer = answer, 
                                                expected_summary=expected_answer, 
                                                question_type = question_type
                                            )
        latence_score, latence_details = self.evaluate_latence(
                                                latency_ms = latency_ms
                                    )
        aveu_ignorance_score, aveu_ignorance_details = self.evaluate_aveu_ignorance(
                                                        answer = answer, 
                                                        question_type = question_type
                                                    )
        
        # Calcul du score  pondéré pour chaque question
        score_global = (exactitude_score*WEIGHTS["exactitude"] 
                        + pertinence_score*WEIGHTS["pertinence"] 
                        + hallucination_score*WEIGHTS["hallucination"] 
                        + latence_score*WEIGHTS["latence"] 
                        + aveu_ignorance_score*WEIGHTS["aveu_ignorance"]
                    )
        
        question_evaluation = QuestionEvaluation(
                question_id = question_id,
                strategy = strategy,
                question_type = question_type,
                exactitude_score = exactitude_score,
                pertinence_score = pertinence_score,
                hallucination_score = hallucination_score,
                latence_score = latence_score,
                aveu_ignorance_score = aveu_ignorance_score,
                score_global = score_global,
                details = {
                    "exactitude": exactitude_details,
                    "pertinence": pertinence_details,
                    "hallucination": hallucination_details,
                    "latence": latence_details,
                    "aveu_ignorance": aveu_ignorance_details
                }     
        )
        return question_evaluation
    
    def run_evaluation(self) -> list[QuestionEvaluation]:
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
        # Éviter de recalculer si l'évaluation a déjà été faite
        if self.evaluations:
            return self.evaluations
        
        # Récupérer la liste des résultats déjà chargés
        results = self.benchmark_results
        
        for result in results:
            try:
                evaluation = self.evaluate_single_result(result=result)
                self.evaluations.append(evaluation)
                logger.info(
                    "Evaluation terminée pour la question avec l'ID %s et la stratégie correspondante est %s",
                    result.get('question_id'),
                    result.get('strategy')
                )
                
            except (KeyError, TypeError, ValueError) as e:
                logger.error(
                    "Erreur lors de l'évaluation de la question avec l'ID %s: %s",
                    result.get('question_id'),
                    e
                )
        return self.evaluations
    
    def generate_strategy_scores(self) -> dict[str, dict[str, float]]:
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
        
        strategy_scores: dict[str, dict[str, list[float]]] = {}
                
        # récuperer la listes des resultats
        evaluations = self.evaluations or self.run_evaluation()
        for evaluation in evaluations:
            
        # grouper les évaluations par stratégie
            strategy = evaluation.strategy
            if strategy not in strategy_scores: 
                strategy_scores[strategy] = {
                    "exactitude": [],
                    "pertinence": [],
                    "hallucination": [],
                    "latence": [],
                    "aveu_ignorance": [],
                }
            strategy_scores[strategy]["exactitude"].append(evaluation.exactitude_score)
            strategy_scores[strategy]["pertinence"].append(evaluation.pertinence_score)
            strategy_scores[strategy]["hallucination"].append(evaluation.hallucination_score)
            strategy_scores[strategy]["latence"].append(evaluation.latence_score)
            strategy_scores[strategy]["aveu_ignorance"].append(evaluation.aveu_ignorance_score)
            
        # calculer la moyenne globale des scores de chaque stratégie
        scores_global_by_criterion: dict[str, dict[str, float]] = {}
        for strategy , criteria in strategy_scores.items():
            for criterion, scores in criteria.items():
                avg_score_criterion = sum(scores) / len(scores)
                if strategy not in scores_global_by_criterion:
                    scores_global_by_criterion[strategy] = {}      
                scores_global_by_criterion[strategy][criterion] = avg_score_criterion
                
        # calculer le score global moyen pour chaque stratégie
        scores_global: dict[str, dict[str, float]] = {}
        for strategy, items_scores in scores_global_by_criterion.items():
            avg_global_score = sum(items_scores[criterion] * WEIGHTS[criterion] for criterion in WEIGHTS) / sum(WEIGHTS.values())
            scores_global[strategy] = {
                        **items_scores,
                        "avg_global_score" : avg_global_score,
                    }
        return scores_global                   
        
             
        
    def generate_recommendation(self) -> dict[str, Any]:
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
        # Calculer les scores par stratégie
        strategy_scores = self.generate_strategy_scores()
        if not strategy_scores:
            return {
                "stratégie_recommandée": None,
                "justification": (
                    "Aucune stratégie n'a été évaluée." 
                    "Car aucun score disponible."
                ),
                "scores_comparatifs":{},
                "points_forts_faibles":{}
            }
            
        # Identifier la stratégie avec le meilleur score global
        best_strategy = None
        best_score = float('-inf')
        for strategy, score_items in strategy_scores.items():
            avg_score = score_items.get("avg_global_score", 0.0)
            if avg_score > best_score:
                best_score = avg_score
                best_strategy = strategy
                
        # Analyser les points forts/faibles de chaque stratégie 
        strengths_and_weaknesses: dict[str, dict[str, list[str]]] = {}
        
        for strategy, scores in strategy_scores.items():
            strengths = []
            weaknesses = []
            for criterion, score in scores.items():
                if criterion == "avg_global_score":
                    continue
                if score >= 0.8:
                    strengths.append(criterion)
                elif score < 0.5 :
                    weaknesses.append(criterion)
                    
            strengths_and_weaknesses[strategy] = {
                "points-forts": strengths,
                "points-faibles": weaknesses
            }
        
        return {
            "stratégie_recommandée": best_strategy,
            "justification": (
                f"La stratégie '{best_strategy}' est recommandée."
                f"Car elle a obtenu le meilleur score global moyen,"
                f"pondéré :{best_score:.2f}."
            ),
            "scores_comparatifs": strategy_scores,
            "points_forts_faibles": strengths_and_weaknesses,
        }
         
    
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
        # définir le chemin du fichier de sortie
        output_path = self.output_dir / filename
        
        # Récupérer les évaluations
        evaluations = self.evaluations or self.run_evaluation()
        
        # Définir les colonnes du CSV
        colonnes = [
            "question_id", 
            "strategy", 
            "question_type",
            "exactitude", 
            "pertinence", 
            "hallucination", 
            "latence", 
            "aveu_ignorance", 
            "score_global"
        ]

        # Écrire les résultats dans le fichier CSV
        with open(output_path, "w", newline="", encoding="utf-8") as filecsv:
            
            writer = csv.DictWriter(filecsv, fieldnames=colonnes)
            
            writer.writeheader()
            for evaluation in evaluations:
                writer.writerow({
                    "question_id": evaluation.question_id,
                    "strategy": evaluation.strategy,
                    "question_type": evaluation.question_type,
                    "exactitude": evaluation.exactitude_score,
                    "pertinence": evaluation.pertinence_score,
                    "hallucination": evaluation.hallucination_score,
                    "latence": evaluation.latence_score,
                    "aveu_ignorance": evaluation.aveu_ignorance_score,
                    "score_global": evaluation.score_global
                })
                
        return output_path
    
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
        # Définir le fichier de sortie
        output_path = self.output_dir / filename
        
        # Creer la liste des evaluations detaillees
        evaluations = self.evaluations or self.run_evaluation()
        
        # Crééer les scores par stratégie
        payload = {
            "metadata" : {
                "date": datetime.now(timezone.utc).strftime(
                         "%Y-%m-%d %H:%M:%S UTC"
                ),
                
                "benchmark_results": str(
                            self.benchmark_results_path
                ),
                
                "golden_set": str(
                    self.golden_set_path                                  
                ),
                
                "evaluation_results_csv" : str(
                    self.output_dir / "evaluation_results.csv"
                )
        },
            "scores_par_strategie": (
                self.generate_strategy_scores()
            ),
            
            "recommandation": self.generate_recommendation(),
            
            "evaluations_detaillees": [
                asdict(evaluation)
                for evaluation in evaluations
            ]  # self.evaluations contient le detail des evaluations
        }
        
        # Créer un fichier qui contient le rapport complet "
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            json.dump(
                payload, 
                f, 
                ensure_ascii=False, 
                indent=4
            )
        return output_path
    

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
    from pathlib import Path

    # Vérifier les arguments
    if len(sys.argv) < 2:
        print("Usage: python evaluate_results.py <benchmark_results.json>")
        print("Exemple: python evaluate_results.py results/benchmark_20250115_143022.json")
        
        sys.exit(1)
    
    benchmark_results_path = sys.argv[1]
    
    if not Path(benchmark_results_path).exists():
        logger.error(
            "Le fichier de résultats du benchmark %s n'existe pas.",
             benchmark_results_path,
        )
        
        sys.exit(1)
   
    # Configuration des chemins
    project_root = Path(__file__).resolve().parents[2]
    golden_set_candidates = [
        project_root / "data" / "golden_set.json",
        project_root / "data" / "Golden_Set.json",
    ]
    golden_set_path = next(
        (path for path in golden_set_candidates if path.exists()),
        golden_set_candidates[0],
    )
    output_dir = project_root / "results"
    
    # 1. Créer l'évaluateur
    benchmarkEvaluator = BenchmarkEvaluator(
            benchmark_results_path, 
            golden_set_path,
            output_dir
    )
    
    # 2. Lancer l'évaluation
    benchmarkEvaluator.run_evaluation()  
     
    # 3. Exporter les résultats
    csv_path = benchmarkEvaluator.export_csv()
    
    json_path =benchmarkEvaluator.export_report()
    
    # 4. Afficher la recommandation
    recommendation = (
        benchmarkEvaluator.generate_recommendation()
    )
    print("\n========Recommandation========")
    print(f"Stratégie recommandée: {recommendation['stratégie_recommandée']}")
    print(f"Justification: {recommendation['justification']}")
    
    logger.info("Chemin du fichier CSV des résultats détaillés : %s", csv_path)
    logger.info("Chemin du fichier JSON du rapport complet : %s", json_path)
    logger.info("Évaluation terminée.")


if __name__ == "__main__":
    main()