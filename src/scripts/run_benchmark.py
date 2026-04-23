"""
Script de benchmark des strategies FAQ.

Ce script execute les 3 strategies sur le golden set et sauvegarde les
resultats pour une evaluation comparative.
"""

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ajouter le repertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Strategies du dossier Assistant_FAQ_Intelligent
from src.strategies.strategy_A_LLM import StrategyALLM
from src.strategies.strategy_B_RAG import StrategyBRAG
from src.strategies.strategy_C_QA import StrategyCQA

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    question_id: str
    question: str
    question_type: str
    strategy: str
    answer: str
    latency_ms: float
    confidence: Optional[float]
    error: Optional[str]
    timestamp: str


class BenchmarkRunner:
    def __init__(self, golden_set_path: str, faq_base_path: str, output_dir: str):
        self.golden_set_path = Path(golden_set_path)
        self.faq_base_path = Path(faq_base_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.golden_set = self._load_golden_set()
        self.faq_base = self._load_faq_base()

        logger.info("Golden set charge: %s questions", len(self.golden_set))
        logger.info("Base FAQ chargee: %s entrees", len(self.faq_base))

        self.strategies = self._init_strategies()
        self.results: List[BenchmarkResult] = []


    def _load_json_list(self, path: Path, key: str) -> List[Dict[str, Any]]:
        if not path.exists():
            raise FileNotFoundError(f"Fichier introuvable: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON invalide: {path} ({exc})") from exc

        items = data.get(key, [])
        if not isinstance(items, list):
            raise ValueError(f"La cle '{key}' du fichier {path} doit etre une liste")
        return items


    def _load_golden_set(self) -> List[Dict[str, Any]]:
        return self._load_json_list(self.golden_set_path, "golden_set")


    def _load_faq_base(self) -> List[Dict[str, Any]]:
        return self._load_json_list(self.faq_base_path, "faq")


    def _init_strategies(self) -> Dict[str, Any]:
        logger.info("Initialisation des strategies...")
        strategies: Dict[str, Any] = {}

        for key, cls in (
            ("strategy_a_llm", StrategyALLM),
            ("strategy_b_rag", StrategyBRAG),
            ("strategy_c_qa", StrategyCQA),
        ):
            try:
                strategies[key] = cls(faq_base=self.faq_base)
                logger.info("  OK %s", key)
            except Exception as exc:
                logger.warning("  KO %s: %s", key, exc)

        if not strategies:
            raise RuntimeError("Aucune strategie n'a pu etre initialisee")

        return strategies


    def run_single_question(self, question: Dict[str, Any], strategy_name: str) -> BenchmarkResult:
        strategy = self.strategies.get(strategy_name)
        timestamp = datetime.now().isoformat()

        if strategy is None:
            return BenchmarkResult(
                question_id=str(question.get("id", "unknown")),
                question=question.get("question", ""),
                question_type=question.get("type", "unknown"),
                strategy=strategy_name,
                answer="",
                latency_ms=0.0,
                confidence=None,
                error=f"Strategie indisponible: {strategy_name}",
                timestamp=timestamp,
            )

        try:
            start = time.perf_counter()
            response = strategy.answer(question.get("question", ""))
            latency_ms = (time.perf_counter() - start) * 1000

            if hasattr(response, "answer"):
                answer = response.answer
                confidence = response.confidence
                error = response.error if hasattr(response, "error") else None
            elif isinstance(response, dict):
                answer = str(response.get("answer", ""))
                confidence = response.get("confidence")
                error = response.get("error")
            else:
                answer = str(response)
                confidence = None
                error = None

            return BenchmarkResult(
                question_id=str(question.get("id", "unknown")),
                question=question.get("question", ""),
                question_type=question.get("type", "unknown"),
                strategy=strategy_name,
                answer=answer,
                latency_ms=round(latency_ms, 2),
                confidence=confidence,
                error=error,
                timestamp=timestamp,
            )
        except Exception as exc:
            return BenchmarkResult(
                question_id=str(question.get("id", "unknown")),
                question=question.get("question", ""),
                question_type=question.get("type", "unknown"),
                strategy=strategy_name,
                answer="",
                latency_ms=0.0,
                confidence=None,
                error=str(exc),
                timestamp=timestamp,
            )


    def run_benchmark(self) -> List[BenchmarkResult]:
        self.results = []
        total_questions = len(self.golden_set)
        strategy_names = list(self.strategies.keys())
        total_tests = total_questions * len(strategy_names)

        logger.info(
            "Demarrage benchmark: %s questions, %s strategies, %s tests",
            total_questions,
            len(strategy_names),
            total_tests,
        )

        done = 0
        for idx, question in enumerate(self.golden_set, start=1):
            q_id = question.get("id", f"Q{idx}")
            logger.info("Question %s/%s: %s", idx, total_questions, q_id)

            for strategy_name in strategy_names:
                result = self.run_single_question(question, strategy_name)
                self.results.append(result)
                done += 1

                status = "OK" if not result.error else "KO"
                logger.info(
                    "  %s %s | %.0f ms",
                    status,
                    strategy_name,
                    result.latency_ms,
                )

        logger.info("Benchmark termine: %s resultats", len(self.results))
        return self.results


    def generate_summary(self) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}
        grouped: Dict[str, List[BenchmarkResult]] = {}

        for result in self.results:
            grouped.setdefault(result.strategy, []).append(result)

        for strategy_name, items in grouped.items():
            latencies = [r.latency_ms for r in items if not r.error]
            errors = [r for r in items if r.error]

            summary[strategy_name] = {
                "nombre_questions": len(items),
                "latence_moyenne_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
                "latence_min_ms": round(min(latencies), 2) if latencies else None,
                "latence_max_ms": round(max(latencies), 2) if latencies else None,
                "nombre_erreurs": len(errors),
                "taux_erreur": round((len(errors) / len(items)) * 100, 2) if items else 0.0,
            }

        return summary


    def save_results(self, filename: Optional[str] = None) -> Path:
        if not filename:
            filename = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        path = self.output_dir / filename
        payload = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "golden_set_path": str(self.golden_set_path),
                "faq_base_path": str(self.faq_base_path),
                "strategies": list(self.strategies.keys()),
                "total_results": len(self.results),
            },
            "summary": self.generate_summary(),
            "results": [asdict(r) for r in self.results],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        logger.info("Resultats sauvegardes dans %s", path)
        return path

    def print_summary(self) -> None:
        summary = self.generate_summary()
        print("\n" + "=" * 60)
        print("RESUME DU BENCHMARK")
        print("=" * 60)
        for strategy_name, stats in summary.items():
            print(f"\n{strategy_name}:")
            print(f"  Questions: {stats['nombre_questions']}")
            print(f"  Taux d'erreur: {stats['taux_erreur']}%")
            if stats["latence_moyenne_ms"] is not None:
                print(f"  Latence moyenne: {stats['latence_moyenne_ms']} ms")
                print(f"  Latence min/max: {stats['latence_min_ms']} / {stats['latence_max_ms']} ms")
        print("=" * 60)


def _resolve_default_paths(project_root: Path) -> Dict[str, Path]:
    """Resolve data file defaults with support for upper/lower case names."""
    golden_candidates = [
        project_root / "data" / "Golden_Set.json",
        project_root / "data" / "golden_set.json",
    ]
    faq_candidates = [
        project_root / "data" / "FAQ_Base.json",
        project_root / "data" / "faq_base.json",
    ]

    def first_existing(candidates: List[Path]) -> Path:
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]

    return {
        "golden": first_existing(golden_candidates),
        "faq": first_existing(faq_candidates),
        "output": project_root / "results",
    }


def main() -> None:
    project_root = Path(__file__).parent.parent
    defaults = _resolve_default_paths(project_root)

    parser = argparse.ArgumentParser(description="Lancer le benchmark FAQ")
    parser.add_argument("--golden-set", default=str(defaults["golden"]))
    parser.add_argument("--faq-base", default=str(defaults["faq"]))
    parser.add_argument("--output-dir", default=str(defaults["output"]))
    parser.add_argument("--output-file", default=None)
    args = parser.parse_args()

    runner = BenchmarkRunner(
        golden_set_path=args.golden_set,
        faq_base_path=args.faq_base,
        output_dir=args.output_dir,
    )

    runner.run_benchmark()
    output_path = runner.save_results(filename=args.output_file)
    runner.print_summary()

    print("\nResultats:", output_path)


if __name__ == "__main__":
    main()
