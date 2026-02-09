# Rapport de Benchmark - Stratégies FAQ Intelligent

**Étudiant(s)** : [Nom(s)]

**Date** : [Date]

**Version** : 1.0

---

## Résumé exécutif

[2-3 phrases résumant les résultats et la recommandation finale]

**Recommandation** : Stratégie [A/B/C] - [Nom de la stratégie]

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

- **Nombre de questions** : [X] questions
- **Répartition** :
  - Questions faciles : [X]
  - Questions moyennes : [X]
  - Questions hors scope : [X]

### 1.3 Conditions de test

- **Date des tests** : [Date]
- **Environnement** : [Local / Cloud]
- **Modèle LLM utilisé** : [Nom du modèle]
- **Modèle d'embeddings** : [Nom du modèle]
- **Nombre d'exécutions par question** : [X]

---

## 2. Résultats par stratégie

### 2.1 Stratégie A - LLM seul

**Configuration** :
- Modèle : [X]
- Paramètres : temperature=[X], max_tokens=[X]

**Résultats** :

| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| Exactitude | [X]% | |
| Pertinence moyenne | [X]/2 | |
| Taux d'hallucinations | [X]% | |
| Latence moyenne | [X]s | |
| Complexité | [Faible/Moyenne/Élevée] | |

**Observations qualitatives** :
- [Observation 1]
- [Observation 2]

**Exemples de réponses** :

| Question | Réponse | Évaluation |
|----------|---------|------------|
| [Question 1] | [Réponse tronquée...] | ✅/⚠️/❌ |
| [Question 2] | [Réponse tronquée...] | ✅/⚠️/❌ |

---

### 2.2 Stratégie B - Recherche sémantique + LLM

**Configuration** :
- Modèle LLM : [X]
- Modèle embeddings : [X]
- Top-K documents : [X]

**Résultats** :

| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| Exactitude | [X]% | |
| Pertinence moyenne | [X]/2 | |
| Taux d'hallucinations | [X]% | |
| Latence moyenne | [X]s | |
| Complexité | [Faible/Moyenne/Élevée] | |

**Observations qualitatives** :
- [Observation 1]
- [Observation 2]

**Exemples de réponses** :

| Question | Documents récupérés | Réponse | Évaluation |
|----------|---------------------|---------|------------|
| [Question 1] | [X docs] | [Réponse...] | ✅/⚠️/❌ |
| [Question 2] | [X docs] | [Réponse...] | ✅/⚠️/❌ |

---

### 2.3 Stratégie C - Q&A extractif

**Configuration** :
- Modèle Q&A : [X]
- Modèle embeddings : [X]
- Top-K documents : [X]

**Résultats** :

| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| Exactitude | [X]% | |
| Pertinence moyenne | [X]/2 | |
| Taux d'hallucinations | [X]% | |
| Latence moyenne | [X]s | |
| Complexité | [Faible/Moyenne/Élevée] | |

**Observations qualitatives** :
- [Observation 1]
- [Observation 2]

---

## 3. Analyse comparative

### 3.1 Tableau récapitulatif

| Critère | Poids | Stratégie A | Stratégie B | Stratégie C |
|---------|-------|-------------|-------------|-------------|
| Exactitude | 30% | [X]% | [X]% | [X]% |
| Pertinence | 20% | [X]/2 | [X]/2 | [X]/2 |
| Hallucinations | 20% | [X]% | [X]% | [X]% |
| Latence | 15% | [X]s | [X]s | [X]s |
| Complexité | 15% | [1-3] | [1-3] | [1-3] |
| **Score pondéré** | 100% | **[X]** | **[X]** | **[X]** |

### 3.2 Graphique comparatif

[Insérer un graphique radar ou histogramme comparant les 3 stratégies]

### 3.3 Analyse des forces et faiblesses

**Stratégie A** :
- ✅ Forces : [...]
- ❌ Faiblesses : [...]

**Stratégie B** :
- ✅ Forces : [...]
- ❌ Faiblesses : [...]

**Stratégie C** :
- ✅ Forces : [...]
- ❌ Faiblesses : [...]

---

## 4. Recommandation

### 4.1 Stratégie recommandée

**Choix : Stratégie [X] - [Nom]**

### 4.2 Justification

[Argumenter le choix en 3-5 points]

1. [Argument 1]
2. [Argument 2]
3. [Argument 3]

### 4.3 Limites de la recommandation

[Identifier les cas où cette stratégie pourrait ne pas être optimale]

### 4.4 Axes d'amélioration possibles

[Suggérer des pistes d'optimisation pour la stratégie retenue]

---

## 5. Annexes

### 5.1 Détail des résultats bruts

[Lien vers le fichier CSV/JSON des résultats complets]

### 5.2 Code du benchmark

[Lien vers le script de benchmark]

### 5.3 Grille d'évaluation complète

[Lien vers la grille d'évaluation remplie]

---
