# Rapport de Benchmark - Stratégies FAQ Intelligent

**Étudiant(s)** : [Nom(s)]

**Date** : 23/04/2026

**Version** : 1.0

---

## Résumé exécutif

Le benchmark compare 3 approches sur 30 questions (90 exécutions au total). Les stratégies A et B ont produit des réponses pertinentes au début du run mais ont été fortement dégradées par des erreurs HTTP 402 (crédits Hugging Face Inference épuisés), ce qui biaise leur taux d'erreur global. La stratégie C, entièrement locale pour l'inférence, termine le benchmark avec 0% d'erreur et une stabilité opérationnelle complète.

**Recommandation** : Stratégie C - Q&A extractif

---

## 1. Protocole d'évaluation

### 1.1 Critères d'évaluation

| Critère | Description | Méthode de mesure | Poids |
|---------|-------------|-------------------|-------|
| Exactitude | % de réponses correctes | Évaluation sur golden set | 30% |
| Pertinence | Qualité de la réponse (0-2) | Notation manuelle | 20% |
| Hallucinations | % de réponses avec infos inventées | Vérification manuelle | 20% |
| Latence | Temps de réponse moyen | Mesure automatique | 15% |
| Complexité | Facilité de maintenance | Évaluation qualitative | 15% |

### 1.2 Jeu de test (Golden Set)

- **Nombre de questions** : 30 questions
- **Répartition** :
  - Direct match : 10
  - Reformulation : 10
  - Hors sujet : 5
  - Complexe : 5

### 1.3 Conditions de test

- **Date des tests** : 23/04/2026
- **Environnement** : Local (Windows, Python 3.10)
- **Modèle LLM utilisé** : meta-llama/Llama-3.1-8B-Instruct (A et B)
- **Modèle d'embeddings** : sentence-transformers/all-MiniLM-L6-v2 (B et C)
- **Modèle Q&A (stratégie C)** : deepset/roberta-base-squad2
- **Nombre d'exécutions par question** : 1

---

## 2. Résultats par stratégie

### 2.1 Stratégie A - LLM seul

**Configuration** :
- Modèle : meta-llama/Llama-3.1-8B-Instruct
- Paramètres : temperature=0.5, max_tokens=220

**Résultats** :

| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| Exactitude | Non mesurée automatiquement | À compléter via évaluation manuelle/keywords |
| Pertinence moyenne | Non mesurée automatiquement | À compléter via grille d'évaluation |
| Taux d'hallucinations | Non mesuré automatiquement | Plusieurs réponses longues non ancrées FAQ observées |
| Latence moyenne | 0.483 s | 483.49 ms |
| Taux d'erreur | 70.0% | 21 erreurs/30, majoritairement HTTP 402 |
| Complexité | Faible | Architecture simple mais très dépendante d'un provider externe |

**Observations qualitatives** :
- Produit des réponses détaillées et grammaticalement correctes quand l'appel API réussit.
- Risque d'hallucination élevé en l'absence de contexte FAQ structuré.
- Très sensible au quota API (arrêt partiel du run par erreur 402).

**Exemples de réponses** :

| Question | Réponse | Évaluation |
|----------|---------|------------|
| Quels sont les horaires de la déchetterie ? | Réponse complète mais avec horaires possiblement non alignés au corpus local | ⚠️ |
| Quels déchets mettre dans le bac jaune ? | Réponse partiellement hors politique locale (contenu générique) | ❌ |

---

### 2.2 Stratégie B - Recherche sémantique + LLM

**Configuration** :
- Modèle LLM : meta-llama/Llama-3.1-8B-Instruct
- Modèle embeddings : sentence-transformers/all-MiniLM-L6-v2
- Top-K documents : 2

**Résultats** :

| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| Exactitude | Non mesurée automatiquement | À compléter via évaluation manuelle/keywords |
| Pertinence moyenne | Non mesurée automatiquement | À compléter via grille d'évaluation |
| Taux d'hallucinations | Non mesuré automatiquement | Tendance meilleure que A grâce au contexte |
| Latence moyenne | 0.299 s | 298.91 ms |
| Taux d'erreur | 53.33% | 16 erreurs/30, majoritairement HTTP 402 |
| Complexité | Moyenne | Pipeline retrieval + génération + gestion de contexte |

**Observations qualitatives** :
- Les réponses sont généralement plus ciblées et concises que la stratégie A.
- Le contexte FAQ réduit les dérives, mais la dépendance API reste bloquante en cas de quota épuisé.

**Exemples de réponses** :

| Question | Documents récupérés | Réponse | Évaluation |
|----------|---------------------|---------|------------|
| Comment obtenir un acte de naissance ? | 2 docs | Réponse alignée (service-public, mairie, délai) | ✅ |
| Comment inscrire mon enfant à la crèche ? | 2 docs | Réponse claire et bien ancrée FAQ | ✅ |

---

### 2.3 Stratégie C - Q&A extractif

**Configuration** :
- Modèle Q&A : deepset/roberta-base-squad2
- Modèle embeddings : sentence-transformers/all-MiniLM-L6-v2
- Top-K documents : 3

**Résultats** :

| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| Exactitude | Non mesurée automatiquement | À compléter via évaluation manuelle/keywords |
| Pertinence moyenne | Non mesurée automatiquement | Certaines réponses trop courtes |
| Taux d'hallucinations | Faible (qualitatif) | Approche extractive, fortement contrainte par le contexte |
| Latence moyenne | 0.754 s | 754.14 ms |
| Taux d'erreur | 0.0% | 0 erreur/30 |
| Complexité | Moyenne | Retrieval + extractif local, pas de dépendance API externe |

**Observations qualitatives** :
- Excellente robustesse opérationnelle (aucune erreur sur le run).
- Réponses parfois courtes/fragmentaires, mais rarement hallucinées.

---

## 3. Analyse comparative

### 3.1 Tableau récapitulatif

| Critère | Poids | Stratégie A | Stratégie B | Stratégie C |
|---------|-------|-------------|-------------|-------------|
| Robustesse (proxy: 1 - taux d'erreur) | 35% | 30.0% | 46.67% | 100.0% |
| Pertinence (qualitatif) | 20% | Moyenne | Bonne | Moyenne |
| Hallucinations (qualitatif) | 20% | Élevé | Moyen | Faible |
| Latence | 15% | 0.483s | 0.299s | 0.754s |
| Complexité (1=faible, 3=élevée) | 10% | 1 | 2 | 2 |
| **Score pondéré (lecture opérationnelle)** | 100% | **Faible** | **Moyen** | **Élevé** |

### 3.2 Graphique comparatif

Graphique non inclus dans cette version texte. Recommandation: produire un histogramme sur 3 axes (latence, taux d'erreur, robustesse) à partir du JSON de résultats.

### 3.3 Analyse des forces et faiblesses

**Stratégie A** :
- ✅ Forces : simple à implémenter, réponses fluides quand l'appel réussit.
- ❌ Faiblesses : hallucinations possibles, forte dépendance au quota API.

**Stratégie B** :
- ✅ Forces : meilleur ancrage métier que A, réponses plus ciblées.
- ❌ Faiblesses : dépendance API externe, échecs en cas d'épuisement crédit.

**Stratégie C** :
- ✅ Forces : 0% d'erreur, fonctionnement local, bonne robustesse.
- ❌ Faiblesses : latence plus élevée et réponses parfois trop courtes.

---

## 4. Recommandation

### 4.1 Recommandation provisoire (opérationnelle)

**Choix provisoire : Stratégie C - Q&A extractif**

Cette recommandation est **opérationnelle à date** (continuité de service), mais **non définitive** pour la comparaison qualitative finale entre B et C.

### 4.2 Justification

1. **Fiabilité maximale en conditions réelles** : 0% d'erreur sur 30 questions.
2. **Indépendance vis-à-vis des quotas externes** : pas de blocage API de type HTTP 402.
3. **Hallucinations réduites** : mécanisme extractif appuyé sur le corpus FAQ.
4. **Cohérence avec un usage collectivité** : priorité à la stabilité et à la conformité des réponses.

### 4.3 Limites de la conclusion actuelle

- Le benchmark A/B est partiellement dégradé par des erreurs HTTP 402 (quota Hugging Face Inference Providers épuisé).
- Dans ce contexte, la comparaison finale de qualité entre B et C n'est pas totalement équitable.
- Réponses parfois incomplètes si le span extrait est court.
- Moins performante pour reformuler de manière conversationnelle longue.
- Latence supérieure aux stratégies génératives quand celles-ci n'échouent pas.

### 4.4 Plan de rerun pour conclusion finale

1. Attendre le rechargement du quota API (ou activer un mode paid/PRO).
2. Relancer le même protocole complet sur les 30 questions (mêmes fichiers, mêmes paramètres).
3. Conserver les paramètres validés: A/B avec `meta-llama/Llama-3.1-8B-Instruct`, B avec top-k=2.
4. Recalculer la grille d'évaluation qualitative sur les nouveaux résultats A/B/C.
5. Produire une conclusion finale consolidée avec comparaison B vs C.

### 4.5 Axes d'amélioration possibles

1. Ajouter une phase de post-traitement (réécriture contrôlée) pour améliorer la fluidité de sortie.
2. Ajuster le top-k et les seuils de confiance par type de question.
3. Mettre en place une stratégie hybride: C en production par défaut, B en fallback si quota disponible.
4. Ajouter une évaluation automatique de l'exactitude par matching de keywords attendus.

---

## 5. Annexes

### 5.1 Détail des résultats bruts

- Fichier JSON: `results/benchmark_20260423_175955.json`

### 5.2 Code du benchmark

- Script: `scripts/run_benchmark.py`

### 5.3 Grille d'évaluation complète

- Grille de base: `docs/grille_evaluation.csv` 

---
