# Note de Cadrage - Projet FAQ Intelligent

**Étudiant(s)** : DJOUALA TENDA Patricia

**Date** : 23/04/2026

**Version** : 1.0

---

## 1. Contexte et objectifs

### 1.1 Contexte du projet
Le projet consiste à concevoir et développer une API REST d'assistant FAQ intelligent pour une collectivité territoriale (contexte Centre-Val de Loire Numerique). L'API doit répondre automatiquement aux questions des citoyens sur des demarches administratives (etat civil, urbanisme, dechets, elections, action sociale, etc.).

La demarche retenue repose sur une comparaison de trois strategies de reponse (A, B, C) afin d'identifier l'approche la plus adaptee selon des criteres techniques et metier: exactitude, pertinence, hallucinations, latence, robustesse operationnelle et complexite de maintenance.

Dans cette note de cadrage, les elements presentes ci-dessous sont des hypotheses de travail a valider par la veille puis par le benchmark.


### 1.2 Objectifs du projet

- Faire une veille technique sur les LLM open source et les variantes de strategie de reponse FAQ.
- Comparer objectivement les trois strategies proposees (LLM seul, RAG, Q&A extractif) via un benchmark rigoureux.
- Formuler une recommandation technique basee sur les resultats de benchmark.
- Concevoir et developper une API REST fonctionnelle integrant la strategie retenue.

**Objectif principal** :
Developper une API REST d'assistance FAQ intelligente, adossee a un benchmark comparatif, permettant de selectionner la meilleure approche technique et d'atteindre un niveau de qualite exploitable en conditions reelles.

**Objectifs secondaires** :
- [x] Choix et justification des modeles IA identifies
- [x] Conception du golden set de questions FAQ pour le benchmark (30 questions)
- [x] Test des strategies et recommandation provisoire de strategie (A, B ou C)
- [x] Implementation complete de l'API REST
- [x] Tests automatises et pipeline CI/CD finalises

### 1.3 Périmètre

**Dans le périmètre** :

- Le choix et l'integration de modeles open source pour les strategies benchmarkees.
- L'implementation des 3 strategies A, B et C pour l'evaluation.
- Une API REST fonctionnelle integrant la strategie retenue et documentee via OpenAPI.
- Des tests unitaires/integration avec pytest et un pipeline CI (GitHub Actions).


**Hors périmètre** :
- Support multilingue (seulement le français est pris en compte)
- Interface utilisateur graphique (seulement une API REST sera développée)
- Deploiement en production (une API de reference sera livree)

---

## 2. Compréhension des 3 stratégies

### 2.1 Stratégie A - LLM seul

**Principe** :
La question utilisateur est envoyee directement a un modele de langage sans phase de recuperation explicite dans la base FAQ locale. Le LLM produit une reponse generee a partir de son entrainement general et des consignes du prompt systeme.

**Avantages attendus** :

- Architecture simple et rapide a implementer.
- Reponses potentiellement fluides et conversationnelles.
- Peu de composants a maintenir.

**Inconvénients attendus** :

- Risque d'hallucinations possiblement plus eleve (reponse non ancree dans la FAQ).
- Dependance potentielle a un provider externe et a son quota.
- Qualite pouvant etre moins stable pour les questions metier precises.

**Schéma simplifié** :
```
Question -> Prompt systeme -> LLM -> Reponse
```

### 2.2 Stratégie B - Recherche sémantique + LLM

**Principe** :
La question est d'abord vectorisee puis comparee aux embeddings de la FAQ pour recuperer les passages les plus pertinents (top-k). Ces passages sont injectes comme contexte dans un prompt, puis le LLM genere la reponse en s'appuyant sur ce contexte.

**Avantages attendus** :

- Ancrage metier potentiellement meilleur que la strategie A grace au contexte FAQ.
- Reduction attendue des hallucinations par rapport au LLM seul.
- Bon compromis precision/expressivite attendu quand l'API LLM est disponible.

**Inconvénients attendus** :

- Pipeline plus complexe (retrieval + generation).
- Dependance potentielle au quota API du provider LLM.
- Qualite potentiellement sensible a la pertinence des documents recuperes.

**Schéma simplifié** :
```
Question -> Embeddings + recherche semantique (top-k) -> Contexte + LLM -> Reponse
```

### 2.3 Stratégie C - Q&A extractif

**Principe** :
Comme pour B, une etape de recherche semantique identifie les FAQ les plus proches. Ensuite, au lieu d'un LLM generatif, un modele Q&A extractif extrait la meilleure portion de texte dans le contexte pour repondre a la question.

**Avantages attendus** :

- Robustesse operationnelle attendue (inference locale possible selon le setup).
- Hallucinations potentiellement limitees car la reponse est extraite du corpus.
- Trajectoire de cout potentiellement mieux maitrisee que les appels LLM externes.

**Inconvénients attendus** :

- Reponses potentiellement plus courtes ou moins naturelles.
- Peut etre moins performante pour reformuler de longues explications.
- Peut rater des cas complexes si le passage pertinent n'est pas bien recupere.

**Schéma simplifié** :
```
Question -> Embeddings + recherche semantique (top-k) -> Modele Q&A extractif -> Reponse
```

---

## 3. Stack technique envisagée

### 3.1 Composants principaux

| Composant | Technologie choisie | Justification |
|-----------|---------------------|---------------|
| Langage | Python 3.10.11 | Ecosysteme ML mature, bibliotheques NLP compatibles, bonne productivite |
| Framework API | FastAPI | Rapide a mettre en oeuvre, validation Pydantic, doc OpenAPI automatique |
| LLM | meta-llama/Llama-3.1-8B-Instruct (tests A/B) | Compatible avec endpoint chat utilise; bonnes capacites instruction-following |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 | Bon compromis performance/latence pour retrieval FAQ |
| Tests | pytest | Standard Python, lisible, integre facilement aux fixtures API |
| CI/CD | GitHub Actions | Natif GitHub, simple pour lint/tests/quality gate |

### 3.2 Modeles IA pre-selectionnes (hypotheses de cadrage)

| Usage | Modèle | Source | Raison du choix |
|-------|--------|--------|-----------------|
| LLM (generation) | Mistral-7B-Instruct-v0.2 (candidat) | HuggingFace | Bon rapport qualite/vitesse dans la litterature, reference courante en open source |
| LLM (generation) | Llama-3.1-8B-Instruct (candidat) | HuggingFace | Bonne capacite instructionnelle, compatibilite observee sur endpoint chat |
| LLM (generation) | Qwen2.5-7B-Instruct (candidat) | HuggingFace | Alternative instruction en 7B, utile pour comparaison multicandidats |
| Embeddings | all-MiniLM-L6-v2 | sentence-transformers | Rapide et performant pour la recherche semantique FAQ |
| Q&A extractif | roberta-base-squad2 | HuggingFace | Modele leger et robuste pour extraction de reponses |

Important: cette section de cadrage presente une pre-selection de candidats et non un choix final. La decision definitive sur les modeles et la strategie retenue est documentee dans le rapport de benchmark.

---

## 4. Planning prévisionnel

| Jour | Phase | Objectifs | Livrables |
|------|-------|-----------|-----------|
| J1 | Cadrage | Comprendre le brief, organiser le projet | Note de cadrage |
| J2 | Veille | Étudier RAG, embeddings, Q&A | Rapport de veille |
| J3 | Implémentation | Développer stratégie A (LLM seul) | Script stratégie A |
| J4 | Implémentation | Développer stratégie B (RAG) | Script stratégie B |
| J5 | Implémentation | Développer stratégie C (Q&A) | Script stratégie C |
| J6 | Benchmark  | Executer benchmark et analyser les resultats | Rapport_BENCHMARK.md |
| J7 | API | Développer l'API FastAPI | API + doc OpenAPI |
| J8 | Tests | Écrire tests unitaires et intégration | Tests pytest |
| J9 | CI/CD | Configurer pipeline GitHub Actions | Workflow CI |
| J10| Soutenance | Finaliser docs, préparer démo | Présentation |

---

## 5. Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Quota API HuggingFace epuise (HTTP 402) | Elevee | Eleve | Prevoir fallback local (strategie C), limiter max_tokens, planifier rerun quota recharge |
| Hallucinations en mode generatif | Moyenne | Eleve | Renforcer prompts, privilegier RAG/QA, ajouter garde-fous et evaluation manuelle |
| Delais de developpement serres | Moyenne | Moyen | Prioriser MVP API + tests critiques, decouper en jalons journaliers |
| Drift de qualite sur reformulations complexes | Moyenne | Moyen | Enrichir golden set, ajuster top-k/seuils, iterer apres benchmark |

---

## 6. Questions en suspens

- [ ] Faut-il privilegier une recommandation strictement operationnelle (robustesse) ou une recommandation ciblee "qualite maximale" apres rerun quota recharge ?
- [ ] Le niveau de detail attendu pour la section CI/CD est-il minimal (lint + tests) ou complet (quality gates + coverage minimum) ?

---

## 7. Ressources consultées (Veille J1)

| Source | URL | Pertinence | Notes |
|--------|-----|------------|-------|
| FastAPI Documentation | https://fastapi.tiangolo.com/ | Elevee | Reference API, validation, documentation OpenAPI |
| Hugging Face Inference Providers | https://huggingface.co/docs/inference-providers/index | Elevee | Contraintes quota/provider, endpoint chat completions |
| Sentence-Transformers Documentation | https://www.sbert.net/ | Elevee | Principes embeddings et recherche semantique |
| Transformers Pipeline (Q&A) | https://huggingface.co/docs/transformers/main_classes/pipelines | Elevee | Utilisation pipeline question-answering |
| Pytest Documentation | https://docs.pytest.org/ | Moyenne | Strategie de tests unitaires/integration |

---
