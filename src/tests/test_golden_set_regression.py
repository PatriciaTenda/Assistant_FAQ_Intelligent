# commande pour tester manuellement au moment venu de l'execution du script
# $env:RUN_LLM_REGRESSION="1"
# python -m pytest src/tests/test_golden_set_regression.py -v

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any

import pytest
from src.api.services.llm_service import generate_answer
from src.scripts.evaluate_results import BenchmarkEvaluator


async def run_single_question_golden_set(golden_set_element: dict[str, Any]) -> dict[str, Any]:
    """
        Cette fonction exécute une question unique du golden set et retourne un dictionnaire avec les résultats de l'exécution.
        
        Args:
            golden_set_element (dict): Un dictionnaire contenant les informations de la question du golden set.
            
        Returns:
            dict[str, Any]: Un dictionnaire contenant les résultats de l'exécution de la question.
    """
    
    # recupérer les informations de la question du golden set
    question_type = str(golden_set_element.get("type", "unknown"))
    question_id = str(golden_set_element.get("id", "unknown"))
    question = str(golden_set_element.get("question", ""))
    
    #  calculer le temps de latence
    try:
        start_time = time.perf_counter()
        
        answer = await generate_answer(question) # appeler la fonction de traitement de la question pour obtenir la réponse
        
        latency_ms = (time.perf_counter() - start_time) *1000  # Convertir en millisecondes
        
        # calculer le taux de confiance des résultats de la question
        ignorance_indicators = [
                    "je ne peux pas répondre",
                    "je ne suis pas en mesure",
                    "hors de mon domaine",
                ]
        is_uncertain = any(indicator in answer.lower() for indicator in ignorance_indicators)
        confidence =0.5 if is_uncertain else 0.7
            
        result = {
            "question_id": question_id,
            "question": question,
            "question_type": question_type,
            "strategy": "strategy_a_llm",
            "answer": answer,
            "latency_ms": round(latency_ms, 2),
            "confidence": confidence,
            "error": None,
        }
    except RuntimeError as e:
        cause = e.__cause__
        result = {
            "question_id": question_id,
            "question": question,
            "question_type": question_type,
            "strategy": "strategy_a_llm",
            "answer": "",
            "latency_ms": 0.0,
            "confidence": 0.0,
            "error": f"{e} | Cause : {cause!r}",
        }
    
    return result


async def run_golden_set(golden_set: list[dict[str, Any]])-> list[dict[str, Any]]:
    """
    Cette fonction exécute l'ensemble du golden_set et retourne une liste de dictionnaires avec les résultats de l'exécution.

    Args:
        golden_set (list[dict[str, Any]]): Une liste de dictionnaires contenant les informations des questions du golden set.

    Returns:
        list[dict[str, Any]]: Une liste de dictionnaires contenant les résultats de l'exécution des questions.
    """
    results: list[dict[str, Any]] = []
    for golden_set_element in golden_set:
        result = await run_single_question_golden_set(golden_set_element)
        results.append(result)
    return results

@pytest.mark.skipif(
    os.getenv("RUN_LLM_REGRESSION") != "1",
    reason="Test LLM réel désactivé par défaut",
)
def test_non_regression_golden_set(tmp_path):
    """
        Cette fonction teste la non-régression du golden_set afin de comparer le score fixé comme seuil avec le score attendu.
        Args:
            tmp_path: Le chemin temporaire pour stocker les résultats du test.
        Returns:
            None
    """
    # définir le chemin du dossier temporaire pour stocker les résultats du benchmark et de l'évaluation
    benchmark_results_path = tmp_path / "benchmark_results.json"
    output_dir = tmp_path 
    
    # charger le golden_set à partir du fichier JSON
    project_root = Path(__file__).resolve().parents[2]
    golden_set_path = project_root / "data" / "Golden_Set.json"
    with open(golden_set_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        golden_set = data["golden_set"]
    
    # exécuter le golden_set et obtenir les résultats
    results = asyncio.run(run_golden_set(golden_set))
    errors = [
            result for result in results
            if result["error"] is not None
        ]
    payload = {
        "results": results
    }

    # vérifier qu'il n'y a pas d'erreurs LLM dans les résultats du benchmark
    assert not errors, f"Erreurs LLM détectées : {errors}"
        
    # sauvegarder les résultats du benchmark dans le fichier JSON
    with open(benchmark_results_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
        
    # creer une instance de BenchmarkEvaluator pour évaluer les résultats du benchmark
    runner_benchmark_evaluation = BenchmarkEvaluator(
        golden_set_path=golden_set_path, 
        benchmark_results_path=benchmark_results_path, 
        output_dir=output_dir
    )
    
    # recupérer les resultats de l'valution des resultats du benchmark
    runner_benchmark_evaluation.run_evaluation()
    
    # génerer les scores d'evaluation dans un dictionnaire
    MIN_GLOBAL_SCORE = 0.65
    scores = runner_benchmark_evaluation.generate_strategy_scores()
    score_global = scores["strategy_a_llm"]["avg_global_score"]
    
    # verifier que le score obtenu est supérieur ou égal au score attendu
    assert score_global >= MIN_GLOBAL_SCORE, (
        f"Régression détectée : score={score_global:.3f}, "
        f"seuil={MIN_GLOBAL_SCORE:.3f}"
    )
    
    
   