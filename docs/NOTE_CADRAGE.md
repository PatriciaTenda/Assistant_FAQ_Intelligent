# Note de Cadrage - Projet FAQ Intelligent

**Étudiant(s)** : DJOUALA TENDA Patricia

**Date** : 12/01/2026

**Version** : 1.0

---

## 1. Contexte et objectifs

### 1.1 Contexte du projet
Le contexte du projet est de concevoir et developper une API REST d'assistant FAQ intelligente pour la collectivité térritoriale du centre Val de Loire Numérique en utilisant un LLM open source. cette API devra être capable de répondre automatiquement aux questions des citoyens. L'objectif est donc de comparer trois stratégies proposées de décider laquelle serait la plus adaptée pour répondre au besoin de la collectivité en tenant compte de certains critèresd'évaluations lels que l'exactitude des réponses, la minimisation des allucinantions, la latence, la complexité technique et la capacité dhébergement en interne.


### 1.2 Objectifs du projet
 - Faire une veille technique sur les LLM open source et les differentes variantes de stratégie de réponses aux questions FAQ 
 - Comparer objectivements les trois stratégies proposées (LLM seul, RAG et QA extractif via un benchmark rigoureux)
 - Formuler les récommandations techniques basées sur les resultats du benchmark
 - Concevoir et developper une API REST fonctionnelle intégrant la stratégie qui sera choisie.

**Objectif principal** :
Developper uen API REST d'assistance FAQ intelligente qui intègre un LLM open source en suivant une démarche rigoureuse de benchmark pour selectionner la meilleure approche technique et qui produit un taux de réponse supèrieur à 80%.

**Objectifs secondaires** :
- [ ] Choix et justtification du modele IA générative selectionné
- [ ] Conception du golden set de questions FAQ pour le benchmark
- [ ] Test des stratégies et décision sur la stratégie retenue(A, B ou C)
- [ ] Implémentation de l'API REST ainsi que des tests automatisés et pipeline CI/CD

### 1.3 Périmètre

**Dans le périmètre** :
- Le choix d'un ou 2 LLM open source qu' on va inplémenter dans la stratégie choisie
- Une implémentation des 3 stratégies A, B et C pour le benchmark
- Une API REST fonctionnelle intégrant la stratégie retenue et documentée avec OpenAPI
- Des tests unitaires avec pytest  et CI/CD avec GitHub Actions


**Hors périmètre** :
- Support multilingue (seulement le français est pris en compte)
- Interface utilisateur graphique (seulement une API REST sera développée)
- Deploiement en production (seulement une API fonctionnelle sera livrée)

---

## 2. Compréhension des 3 stratégies

### 2.1 Stratégie A - LLM seul

**Principe** :
[Expliquer en vos propres mots comment fonctionne cette stratégie]

**Avantages attendus** :
- 

**Inconvénients attendus** :
- 

**Schéma simplifié** :
```
Question → [???] → Réponse
```

### 2.2 Stratégie B - Recherche sémantique + LLM

**Principe** :
[Expliquer en vos propres mots comment fonctionne cette stratégie]

**Avantages attendus** :
- 

**Inconvénients attendus** :
- 

**Schéma simplifié** :
```
Question → [???] → [???] → Réponse
```

### 2.3 Stratégie C - Q&A extractif

**Principe** :
[Expliquer en vos propres mots comment fonctionne cette stratégie]

**Avantages attendus** :
- 

**Inconvénients attendus** :
- 

**Schéma simplifié** :
```
Question → [???] → [???] → Réponse
```

---

## 3. Stack technique envisagée

### 3.1 Composants principaux

| Composant | Technologie choisie | Justification |
|-----------|---------------------|---------------|
| Langage | Python 3.10.11 | |
| Framework API |FASTAPI | |
| LLM | | |
| Embeddings | | |
| Tests |Pytest | |
| CI/CD |github action | |

### 3.2 Modèles IA identifiés

| Usage | Modèle | Source | Raison du choix |
|-------|--------|--------|-----------------|
| LLM (génération) |Qwen/Qwen2.5-7B-Instruct| HuggingFace |respecte les contraintes du client et adéquat pour une FAQ: open source, Instrcut,leger, version stable de mistral et officielle |
| Embeddings |sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |HuggingFace | Support du français  
Multilingue, Qualité sur FAQ FR, Robustesse sémantique, Latence, Usage RAG multilingue, Adapté collectivité FR  |
| Q&A extractif |AgentPublic/camembert-base-squadFR-fquad-piaf |HuggingFace |spécialisé QA extractif, français natif 🇫🇷, léger et industrialisable |

---

## 4. Planning prévisionnel

| Jour | Phase | Objectifs | Livrables |
|------|-------|-----------|-----------|
| J1   |Cadrage du projet| |Note_cadrage.md|
| J2   |Veille technique| |Rapport_Veille.md|
| J3   |Test des stratégies| |grille_evaluation.csv|
| J4   |Test des stratégies| |grille_evaluation.csv|
| J5   |Mise en oeuvre du benchmark|Prise de décision de la stratégie|Rapport_veille.md |
| J6   |Mise en Oeuvre de l'API| | |
| J7   | | | |
| J8   | | | |
| J9   | | | |
| J10  |Présentation du projet| |PowePoint de présentation|

---

## 5. Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| API HuggingFace indisponible | | | |
| Temps insuffisant pour X | | | |
| [Autre risque] | | | |

---

## 6. Questions en suspens

- [ ] [Question 1 pour le formateur]
- [ ] [Question 2]

---

## 7. Ressources consultées (Veille J1)

| Source | URL | Pertinence | Notes |
|--------|-----|------------|-------|
| | | | |
| | | | |

---
