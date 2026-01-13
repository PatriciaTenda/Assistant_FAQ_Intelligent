# Assistant FAQ Intelligent

## Présentation du projet
Ce projet vise à moderniser la gestion des questions récurrentes des citoyens en développant une **API REST** basée sur **FastAPI**, capable de fournir automatiquement des réponses à partir d’une base de FAQ.

Trois stratégies d’intelligence artificielle sont étudiées et comparées à l’aide d’un **benchmark objectif** :

- **LLM seul**
- **Recherche sémantique + LLM (RAG simplifié)**
- **Question Answering extractif**

La solution privilégie des **composants open source** et reste compatible avec un **hébergement interne à terme**, conformément aux contraintes des collectivités territoriales.

---

## Objectifs du projet

### Objectif principal
Concevoir, développer et déployer une API d’assistance FAQ intégrant un modèle de langage, en s’appuyant sur une démarche rigoureuse de benchmark afin de sélectionner la stratégie la plus adaptée.

### Objectifs spécifiques
1. Comparer objectivement trois stratégies de réponse aux questions  
2. Formuler une recommandation technique argumentée basée sur des données  
3. Implémenter une API REST fonctionnelle  
4. Industrialiser la solution (tests automatisés, CI/CD)  
5. Produire une documentation technique exploitable  

---

## Stratégies étudiées

| Stratégie | Description |
|----------|-------------|
| **A – LLM seul** | Génération directe de réponses via un prompt système |
| **B – RAG** | Recherche sémantique des FAQ puis génération de réponses contextualisées |
| **C – QA extractif** | Extraction précise de réponses depuis la base documentaire |

---

## Démarche projet

Le projet suit les étapes suivantes :

1. Cadrage du projet et veille technique  
2. Définition du protocole de benchmark  
3. Implémentation des trois stratégies  
4. Benchmark et analyse des résultats  
5. Développement de l’API REST  
6. Mise en place des tests, CI/CD et monitoring  
7. Documentation et finalisation  

---

## Livrables

-  `NOTE_CADRAGE.md` – Cadrage du projet et de la démarche de veille  
-  `RAPPORT_VEILLE.md` – Synthèse et résultats de la veille technique  
-  `RAPPORT_BENCHMARK.md` – Résultats du benchmark et recommandation finale  
-  Documentation API (OpenAPI / Swagger)  

---

## Contraintes techniques

### Technologies autorisées
- Python 3.10+
- FastAPI
- HuggingFace Inference API (gratuit)
- sentence-transformers (local)
- ChromaDB ou recherche vectorielle simple
- pytest
- GitHub Actions
- Docker

### Restrictions
- APIs payantes (OpenAI, Anthropic, etc.)
- Solutions propriétaires non auto-hébergeables
- Bases de données cloud
- Interfaces de démonstration type Streamlit ou Gradio (hors bonus)

---

## Organisation du dépôt

```text
    Assistant_FAQ_Intelligent/
        docs/
        ├── NOTE_CADRAGE.md
        ├── RAPPORT_VEILLE.md
        ├── RAPPORT_BENCHMARK.md
        src/
        tests/
        README.md
        gitignore
```
