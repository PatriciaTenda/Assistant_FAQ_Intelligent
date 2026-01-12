# Assistant_FAQ_Intelligent
## Description du prokjet
Le projet vise à moderniser les  réponses aux questions des citoyens en mettant en place une API REST (FASTAPI) via laquelle les réponses seront fournies automatiquement à partir d'une base de FAQ.
Trois stratégies (LLM seul, recherche sémantique + LLM, QA extractif) doivent être implémentées et puis comparées par le truchement d'un benchmark objectif(exactitude, pertinence, hallucinations, latence, complexité). Les outils doivent rester open sources et intégrable en interne à terme.

## Objectifs du projets
Les objectifs du projet sont résumés comme suit:

### Objectif principal
Concevoir, développer et déployer une API d'assistance FAQ intégrant un LLM, en suivant une démarche rigoureuse de benchmark pour sélectionner la meilleure approche technique.

### Objectifs spécifiques

1. **Benchmark** : Comparer objectivement 3 stratégies de réponse aux questions
2. **Recommandation** : Formuler une préconisation argumentée basée sur des données
3. **Implémentation** : Développer l'API avec la stratégie retenue
4. **Industrialisation** : Mettre en place tests automatisés et pipeline CI/CD
5. **Documentation** : Produire une documentation technique exploitable

## Les 3 stratégies à comparer

| Stratégie | Description | Principe |
|-----------|-------------|----------|
| **A - LLM seul** | Le LLM répond directement avec un prompt système contextualisé | Simplicité maximale |
| **B - Recherche sémantique + LLM** | Recherche des FAQ pertinentes via embeddings, puis génération de réponse contextualisée | Approche RAG simplifiée |
| **C - Q&A extractif** | Recherche sémantique + modèle extractif qui pointe vers la réponse dans le document | Extraction précise |

## Livrables attendus

### Phase 1 - Cadrage & Veille (J1)
- [ ] Note de cadrage complétée
- [ ] Rapport de veille technique

### Phase 2 - Données & Conception (J2)
- [ ] Protocole de benchmark défini
- [ ] Grille d'évaluation préparée
- **JALON 1** : Validation du protocole par le formateur

### Phase 3 - Implémentation (J3-J5)
- [ ] Script stratégie A fonctionnel
- [ ] Script stratégie B fonctionnel
- [ ] Script stratégie C fonctionnel
- **JALON 2** : Démonstration des 3 stratégies

### Phase 4 - Benchmark (J6)
- [ ] Résultats d'évaluation compilés
- [ ] Rapport de benchmark avec recommandation

### Phase 5 - API (J7)
- [ ] API FastAPI fonctionnelle
- [ ] Documentation OpenAPI
- **JALON 3** : API opérationnelle validée

### Phase 6 - Tests & CI/CD (J8)
- [ ] Tests unitaires (pytest)
- [ ] Test de non-régression sur golden set
- [ ] Pipeline GitHub Actions

### Phase 7 - Monitoring & Documentation (J9)
- [ ] Logging des requêtes/réponses
- [ ] Métriques exposées
- [ ] Documentation technique complète

### Phase 8 - Finalisation (J10)
- [ ] Tous les livrables finalisés
- [ ] Présentation préparée
- [ ] Démonstration fonctionnelle

## Critères d'évaluation du benchmark

| Critère | Description | Poids |
|---------|-------------|-------|
| **Exactitude** | % de réponses correctes sur le golden set | 30% |
| **Pertinence** | Score 0-2 sur la qualité de la réponse | 20% |
| **Hallucinations** | % de réponses contenant des informations inventées | 20% |
| **Latence** | Temps de réponse moyen (secondes) | 15% |
| **Complexité** | Difficulté de maintenance et évolution | 15% |

## Contraintes techniques

### Stacks adéquates et autorisées
- Python 3.10+
- FastAPI pour l'API REST
- HuggingFace Inference API (gratuit)
- sentence-transformers (local)
- ChromaDB ou recherche NumPy simple
- pytest pour les tests
- GitHub Actions pour CI/CD
- Docker pour la conteneurisation

### Stacks non autorisées
- APIs payantes (OpenAI, Anthropic, etc.)
- Streamlit, Gradio (sauf bonus)
- Bases de données cloud

### Contrainte client
> Les Souhaits du client sont de déployer une solution qui puisse à terme être hébergée en interne ainsi que privilégier les composants open source.

## Etapes 1 : Cadrage de la veille technique et production du benchmark

### Objectif de la veille
L'objectif de la veille est d'identifier et d'analyser les approches techniques (les outils et modeles IA pertinents) existantes  pour la mise en place d'une solution de FAQ intelligente basés sur des Lmodèles de langages open source. Nous pourrions de ce fait commparer trois stratégies(LLM seul, Recherche sémantique + LLM, Q&A extractif) et selectionner le contexte le plus adapté pour répondre au besoin d'une collectivité térritoriale selon les critères de **performance**, **fiabilité** et de **maintenabilité**. 

### La clé de la veille : décision à prendre
La décison à prendre à l'issue de la veille est de choisir la meilleur stratégie technique parmi les  trois proposées qui va offrir le meilleur comprimis entre l'**exactitude des réponses**, la **pertinence**, la **minimisation des hallucinations**, la **latence**, la **complexité technique** et la **capacité d'ébergement en interne**.

### Périmètre de la veille 
le périmètre de la veille technique couvre les aspects ci- dessous :
- Identifier un ou deux modèles de LLM open source performants utilisable pour des FAQ administratives et correspondant aux besoins des collectivités térritoriales.
- Explorer et comprendre les diffèrentes approches de génération de réponses (LLM seul, RAG, Q&A extractif).
- Explorer et identifier les techniques de recherche sémantique et les outils d'embeddings adaptés aux FAQ.
- Explorer les solutions de stockage vectorielles et locales open source 
- Explorer et identifier les methodes d'évaluation et de benchmark existantes pour les systèmes de question-réponses.
- Identifier et selectionner les outils d'industrialisation adaptés au projets (API REST, tests automatisés, CI/CD, monitoring).

### Hors périmètre de la veille:
- APIs commerciales payantes
- Solutions propriétaires non auto-hébergeables
- Interfaces graphiques de démonstration (Streamlit, Gradio)

### Les questions clès de la veille technique

#### Questions liées aux modèles IA

- Quels modèles de langage open source sont les plus adaptés aux réponses administratives en français ?

- Quels modèles présentent le moins de risques d’hallucinations dans un contexte factuel ?

#### Questions liées aux stratégies A/B/C

- Quelles sont les forces et limites d’un LLM utilisé seul pour une FAQ ?

- En quoi une approche RAG améliore-t-elle la fiabilité des réponses ?

- Quels sont les cas d’usage pertinents pour un modèle de QA extractif ?

#### Questions liées aux outils techniques

- Quels embeddings open source offrent de bonnes performances pour des FAQ en français ?

- Quels sont les avantages et limites d’un vector store comme ChromaDB ?

- Quels impacts ces choix ont-ils sur la latence et la complexité du système ?

#### Questions liées à l’évaluation

- Quelles métriques sont recommandées pour évaluer un assistant FAQ IA ?

- Comment mesurer objectivement les hallucinations ?

### Sources de la veille

Documentation officielle des bibliothèques et frameworks

Plateforme Hugging Face

Blogs techniques et articles spécialisés IA

Retours d’expérience de projets similaires

Forums techniques (en complément)

### Résultat attendu de la veille

- Une synthèse des approches existantes

- Une analyse comparative des stratégies A, B et C

- Des recommandations techniques pour la phase de benchmark

- Une bibliographie structurée

Livrables de la veille : **NOTE_CADRAGE.md** et **RAPPORT_BENCHMARK.md**
