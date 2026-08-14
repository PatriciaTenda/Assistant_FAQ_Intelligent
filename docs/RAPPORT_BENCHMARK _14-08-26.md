# Rapport de Benchmark - Stratégies FAQ Intelligent

**Étudiant(s)** : [Patricia Tenda]

**Date** : 14/08/2026

**Version** : 1.1

---

## Résumé exécutif

Le benchmark compare 3 approches (A, B, C) sur 30 questions du golden set, soit 90 exécutions. Les mesures automatiques montrent une meilleure performance globale de la stratégie A selon la grille pondérée actuelle, malgré un taux d'erreur runtime plus élevé que la stratégie C. La stratégie C reste la plus robuste en production (0 erreur), mais son score global est plus faible sur les critères d'exactitude et de pertinence dans cette évaluation.

**Recommandation** : Stratégie A - LLM seul (sur la base du score pondéré automatique actuel)

---

## 1. Protocole d'évaluation

### 1.1 Critères d'évaluation

| Critère | Description | Méthode de mesure | Poids |
|---------|-------------|-------------------|-------|
| Exactitude | Présence des informations clés attendues | Matching automatique de mots-clés (golden set) | 30% |
| Pertinence | Adéquation de la réponse à la question | Heuristique automatique (longueur + recouvrement lexical) | 20% |
| Hallucinations | Absence d'informations non attendues | Détection heuristique (URLs, montants, dates, patterns) | 20% |
| Latence | Temps de réponse | Mesure automatique | 15% |
| Aveu d'ignorance | Gestion des questions hors sujet | Détection d'expressions d'ignorance | 15% |

### 1.2 Jeu de test (Golden Set)

- **Nombre de questions** : 30 questions
- **Répartition** :
  - Direct match : 10
  - Reformulation : 10
  - Hors sujet : 5
  - Complexe : 5

### 1.3 Conditions de test

- **Date des tests** : 30/06/2026
- **Environnement** : Local (Windows, Python 3.10)
- **Modèle LLM utilisé** : `meta-llama/Llama-3.1-8B-Instruct` (A et B)
- **Modèle d'embeddings** : `sentence-transformers/all-MiniLM-L6-v2` (B et C)
- **Modèle Q&A** : `deepset/roberta-base-squad2` (C)
- **Nombre d'exécutions par question** : 1

---

## 2. Résultats par stratégie

### 2.1 Stratégie A - LLM seul

**Configuration** :
- Modèle : `meta-llama/Llama-3.1-8B-Instruct`
- Paramètres : `temperature=0.5`, `max_tokens=220`

**Résultats** :

| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| Exactitude | 47.94% | Score moyen `0.4794` |
| Pertinence moyenne | 1.62/2 | Score moyen `0.8095` |
| Absence d'hallucinations | 79.33% | Score moyen `0.7933` |
| Latence moyenne | 1.930 s | 1930.11 ms |
| Taux d'erreur runtime | 36.67% | 11 erreurs/30 |
| Complexité | Faible | Architecture simple |

**Observations qualitatives** :
- Réponses souvent bien formulées et complètes quand l'appel API réussit.
- Sensible aux pannes/quota côté service externe.

**Exemples de réponses** :

| Question | Réponse | Évaluation |
|----------|---------|------------|
| Comment obtenir un acte de naissance ? | Réponse détaillée, procédures bien expliquées, mais quelques éléments génériques | ⚠️ |
| Quels sont les horaires de la déchetterie ? | Réponse prudente orientant vers la mairie, manque d'ancrage local précis | ⚠️ |

---

### 2.2 Stratégie B - Recherche sémantique + LLM

**Configuration** :
- Modèle LLM : `meta-llama/Llama-3.1-8B-Instruct`
- Modèle embeddings : `sentence-transformers/all-MiniLM-L6-v2`
- Top-K documents : 2

**Résultats** :

| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| Exactitude | 69.72% | Meilleur score d'exactitude |
| Pertinence moyenne | 1.00/2 | Score moyen `0.5011` |
| Absence d'hallucinations | 63.67% | Score moyen `0.6367` |
| Latence moyenne | 0.890 s | 889.76 ms |
| Taux d'erreur runtime | 20.00% | 6 erreurs/30 |
| Complexité | Moyenne | Pipeline retrieval + génération |

**Observations qualitatives** :
- Bon ancrage factuel via le contexte récupéré.
- Pertinence variable selon la qualité des documents top-k.

**Exemples de réponses** :

| Question | Documents récupérés | Réponse | Évaluation |
|----------|---------------------|---------|------------|
| Comment obtenir un acte de naissance ? | 2 docs | Réponse structurée, gratuite, pièces demandées | ✅ |
| Quels sont les horaires de la déchetterie ? | 2 docs | Horaires détaillés et conditions d'accès | ✅ |

---

### 2.3 Stratégie C - Q&A extractif

**Configuration** :
- Modèle Q&A : `deepset/roberta-base-squad2`
- Modèle embeddings : `sentence-transformers/all-MiniLM-L6-v2`
- Top-K documents : 3

**Résultats** :

| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| Exactitude | 40.94% | Score moyen `0.4094` |
| Pertinence moyenne | 0.98/2 | Score moyen `0.4902` |
| Absence d'hallucinations | 64.33% | Score moyen `0.6433` |
| Latence moyenne | 0.923 s | 923.41 ms |
| Taux d'erreur runtime | 0.00% | 0 erreur/30 |
| Complexité | Moyenne | Retrieval + extractif local |

**Observations qualitatives** :
- Très robuste à l'exécution (aucune erreur).
- Réponses parfois trop courtes ou incomplètes.

---

## 3. Analyse comparative

### 3.1 Tableau récapitulatif

| Critère | Poids | Stratégie A | Stratégie B | Stratégie C |
|---------|-------|-------------|-------------|-------------|
| Exactitude | 30% | 47.94% | 69.72% | 40.94% |
| Pertinence | 20% | 1.62/2 | 1.00/2 | 0.98/2 |
| Absence d'hallucinations | 20% | 79.33% | 63.67% | 64.33% |
| Latence | 15% | 1.930 s | 0.890 s | 0.923 s |
| Aveu d'ignorance | 15% | 100.00% | 83.33% | 83.33% |
| **Score pondéré** | 100% | **0.7034** | **0.6742** | **0.5870** |

### 3.2 Graphique comparatif

Graphique non inclus dans cette version texte. Recommandation: générer un histogramme sur les 5 critères normalisés à partir de `evaluation_report.json`.

### 3.3 Analyse des forces et faiblesses

**Stratégie A** :
- ✅ Forces : meilleure pertinence moyenne, meilleur score global pondéré, excellente gestion du hors-sujet.
- ❌ Faiblesses : taux d'erreur runtime élevé, latence la plus élevée.

**Stratégie B** :
- ✅ Forces : meilleure exactitude, latence faible, bonnes réponses factuelles.
- ❌ Faiblesses : score de pertinence plus faible selon l'heuristique, dépendance API externe.

**Stratégie C** :
- ✅ Forces : robustesse opérationnelle maximale (0 erreur), architecture locale stable.
- ❌ Faiblesses : réponses courtes, exactitude et pertinence plus faibles.

---

## 4. Recommandation

### 4.1 Stratégie recommandée

**Choix : Stratégie A - LLM seul**

### 4.2 Justification

1. Meilleur score global pondéré (`0.7034`) sur la grille actuelle.
2. Meilleure pertinence moyenne (`1.62/2`) dans l'évaluation automatique.
3. Meilleure performance sur l'aveu d'ignorance (`100%`) pour les hors-sujet.
4. Qualité rédactionnelle globalement supérieure dans les exemples observés.

### 4.3 Limites de la recommandation

- La recommandation dépend d'heuristiques automatiques (pas d'annotation humaine systématique).
- Le taux d'erreur runtime de A (36.67%) pénalise son usage en production sans mécanisme de secours.
- Le critère "absence d'hallucinations" est estimé automatiquement et reste approximatif.

### 4.4 Axes d'amélioration possibles

1. Ajouter une stratégie hybride: B/C en fallback automatique en cas d'échec de A.
2. Compléter l'évaluation automatique par une notation manuelle sur un échantillon.
3. Ajuster les prompts et seuils de confiance pour réduire les réponses génériques.
4. Mettre en cache des réponses FAQ fréquentes pour diminuer latence et dépendance réseau.

---

## 5. Annexes

### 5.1 Détail des résultats bruts

- JSON benchmark: `Assistant_FAQ_Intelligent/results/benchmark_20260630_213754.json`
- CSV évaluation: `Assistant_FAQ_Intelligent/results/evaluation_results.csv`
- JSON évaluation: `Assistant_FAQ_Intelligent/results/evaluation_report.json`

### 5.2 Code du benchmark

- Script benchmark: `Assistant_FAQ_Intelligent/src/scripts/run_benchmark.py`
- Script évaluation: `Assistant_FAQ_Intelligent/src/scripts/evaluate_results.py`

### 5.3 Grille d'évaluation complète

- Grille remplie (automatique): `Assistant_FAQ_Intelligent/results/evaluation_report.json`

---
