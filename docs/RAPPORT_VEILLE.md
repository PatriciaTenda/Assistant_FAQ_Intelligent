Projet : Assistant FAQ Intelligent pour Collectivité Territoriale

# Cadrage de la veille technique et production d'un rapport de veille

## Objectif de la veille
L'objectif de la veille est d'identifier et d'analyser les approches techniques (modeles IA, embeddings, strategie de reponse, outillage API/tests) pour une solution de FAQ intelligente orientee service public local.

La veille doit permettre de comparer 3 strategies:
- Strategie A: LLM seul
- Strategie B: Recherche semantique + LLM (RAG simplifie)
- Strategie C: Q&A extractif

Le choix final doit equilibrer performance, fiabilite, latence, maitrise des hallucinations, cout d'exploitation et maintenabilite.

## La cle de la veille : decision a prendre
Choisir la strategie technique la plus adaptee au contexte de collectivite en tenant compte:
- de la qualite des reponses
- de la robustesse en production
- des contraintes de cout/quota provider
- de la simplicite d'industrialisation (API + tests + CI)

## Perimetre de la veille
La veille couvre les axes suivants:
- Selection de modeles open source pour generation en francais administratif
- Etude des 3 approches A/B/C
- Selection d'un modele d'embeddings adapte FAQ FR
- Etude des methodes d'evaluation (golden set, erreurs, latence, hallucinations)
- Outils d'industrialisation: FastAPI, pytest, GitHub Actions

## Hors perimetre de la veille
- APIs commerciales proprietaires payantes hors ecosysteme open source vise
- UI de demonstration (Streamlit/Gradio)
- Deploiement production final

## Questions cles de la veille technique

### Questions liees aux modeles IA
- Quels modeles open source sont compatibles avec notre endpoint `chat_completion` ?
- Quels modeles restent exploitables sous contrainte de quota ?
- Quels modeles donnent le meilleur compromis qualite/latence pour FAQ administrative ?

### Questions liees aux strategies A/B/C
- Quelles limites d'un LLM seul sur des questions factuelles ?
- Quel gain de fiabilite apporte le contexte RAG ?
- Quand privilegier une approche extractive ?

### Questions liees aux outils techniques
- Quel modele d'embeddings convient le mieux a une FAQ FR ?
- Comment limiter les risques de cout/API dans le pipeline ?

### Questions liees a l'evaluation
- Quelles metriques automatiques utiliser (latence, taux d'erreur) ?
- Quelles metriques manuelles completer (exactitude, pertinence, hallucinations) ?

# Resultat de la veille

## 1. Synthese des approches existantes

### Strategie A - LLM seul
- Points forts: architecture simple, reponses fluides
- Limites: hallucinations possibles, forte dependance provider/quota

### Strategie B - Recherche semantique + LLM
- Points forts: meilleur ancrage metier grace au contexte FAQ
- Limites: dependance API maintenue, complexite superieure a A

### Strategie C - Q&A extractif
- Points forts: robuste, peu d'hallucinations, independance relative au quota LLM externe
- Limites: reponses parfois courtes, moins conversationnelles

## 2. Tests LLM effectues (faits en pratique)

Des tests ont ete executes en appel direct `InferenceClient.chat_completion` avec le token de projet.

| Modele teste | Statut | Observation |
|---|---|---|
| meta-llama/Llama-3.1-8B-Instruct | OK | Repond correctement sur test court |
| Qwen/Qwen2.5-7B-Instruct | OK | Compatible sur test court |
| Qwen/Qwen2.5-3B-Instruct | KO | `model_not_supported` sur provider actif |
| mistralai/Mistral-7B-Instruct-v0.2 | KO | `model_not_supported` sur provider actif |
| mistralai/Mistral-Nemo-Instruct-2407 | KO | Non disponible sur providers actifs |
| google/gemma-2-2b-it | KO | Non disponible sur providers actifs |
| HuggingFaceH4/zephyr-7b-beta | KO | Non disponible sur providers actifs |
| google/flan-t5-large | KO | Non disponible sur providers actifs |

### Conclusion technique des tests LLM
- La compatibilite reelle depend du provider active sur le compte, pas seulement de la popularite du modele.
- Un modele peut etre valide ponctuellement puis devenir indisponible en pratique si le quota est epuise.

## 3. Analyse benchmark et implications

### Resultats consolides de tous les runs benchmark

Les resultats ci-dessous regroupent les differents runs executes au cours de la session, pour eviter un biais d'interpretation base uniquement sur le dernier fichier.

| Run | Fichier | Signal modele observe | A (lat / erreur) | B (lat / erreur) | C (lat / erreur) | Lecture |
|---|---|---|---|---|---|---|
| Run 1 | `results/benchmark_20260423_165234.json` | `mistralai/Mistral-7B-Instruct-v0.2` non supporte (vu dans erreurs B) | 2745.15 ms / 0.0% | 60.19 ms / 80.0% | 1114.53 ms / 0.0% | B massivement en echec (`model_not_supported`) |
| Run 2 | `results/benchmark_20260423_173741.json` | Pas de `model_not_supported` dominant dans le resume | 2798.36 ms / 36.67% | 752.57 ms / 33.33% | 753.98 ms / 0.0% | A/B partiellement operationnelles, C toujours stable |
| Run 3 | `results/benchmark_20260423_175437.json` | `Qwen/Qwen2.5-3B-Instruct` non supporte | null / 100.0% | 27.09 ms / 80.0% | 795.58 ms / 0.0% | Echec quasi complet A/B pour incompatibilite modele |
| Run 4 | `results/benchmark_20260423_175955.json` | `meta-llama/Llama-3.1-8B-Instruct` fonctionne mais erreurs 402 en cours de run | 483.49 ms / 70.0% | 298.91 ms / 53.33% | 754.14 ms / 0.0% | A/B utiles au debut puis penalisees par quota, C robuste |

### Resultat de reference retenu pour la decision provisoire
Fichier principal de reference: `results/benchmark_20260423_175955.json`

| Strategie | Latence moyenne | Taux d'erreur |
|---|---:|---:|
| A (LLM seul) | 483.49 ms | 70.0% |
| B (RAG + LLM) | 298.91 ms | 53.33% |
| C (Q&A extractif) | 754.14 ms | 0.0% |

### Interpretation correcte
- A et B ont montre une qualite utile sur les requetes reussies.
- Sur l'historique des runs, les echecs A/B proviennent de deux causes distinctes: incompatibilite modele (`model_not_supported`) puis limite de credits (HTTP 402).
- Les erreurs majoritaires A/B sur le run de reference proviennent d'un probleme operationnel externe: HTTP 402 (credits mensuels Hugging Face epuises), et non uniquement d'un probleme algorithmique.
- C reste la plus robuste dans le contexte actuel, car elle termine sans erreur.

## 4. Recommandations techniques pour la phase benchmark/API

1. Conserver une recommandation provisoire operationnelle: Strategie C.
2. Relancer un benchmark complet A/B/C apres recharge quota pour une conclusion qualitative definitive.
3. Garder les parametres de sobriete token sur A/B:
- `max_tokens` reduit
- `top_k` modere en RAG
4. Completer la grille manuelle (`docs/grille_evaluation.csv`) pour exactitude/pertinence/hallucinations.
5. Mettre en place une logique explicite de gestion quota (ex: detection 402 + message de statut).

## 5. Premieres hypotheses techniques de mise en oeuvre

- API FastAPI avec endpoint principal `/api/v1/answer`
- Strategie par defaut en phase MVP: C (robustesse)
- Option de bascule vers B quand quota/API disponible
- Tests pytest unitaires + integration
- CI de base: lint + tests

# Sources de veille structuree

## Documentation officielle des bibliotheques
- FastAPI: https://fastapi.tiangolo.com/
- Transformers: https://huggingface.co/docs/transformers
- Sentence-Transformers: https://www.sbert.net/
- Pytest: https://docs.pytest.org/

## Plateforme Hugging Face
- Inference Providers / compatibilite endpoint:
	https://huggingface.co/docs/inference-providers
- Model Hub (verification disponibilite modele)

## Documents projet utilises
- `docs/NOTE_CADRAGE.md`
- `docs/RAPPORT_BENCHMARK.md`
- `results/benchmark_20260423_175955.json`

Livrables de la veille: **NOTE_CADRAGE.md** et **RAPPORT_VEILLE.md**
