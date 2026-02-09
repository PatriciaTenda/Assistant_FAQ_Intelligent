Projet : Assistant FAQ Intelligent pour Collectivité Territoriale

# Cadrage de la veille technique et production d'un rapport de veille

## Objectif de la veille
L'objectif de la veille est d'identifier et d'analyser les approches techniques (les outils et modeles IA pertinents) existantes  pour la mise en place d'une solution de FAQ intelligente basés sur des Lmodèles de langages open source. Nous pourrions de ce fait commparer trois stratégies(LLM seul, Recherche sémantique + LLM, Q&A extractif) et selectionner le contexte le plus adapté pour répondre au besoin d'une collectivité térritoriale selon les critères de **performance**, **fiabilité** et de **maintenabilité**. 

## La clé de la veille : décision à prendre
La décison à prendre à l'issue de la veille est de choisir la meilleur stratégie technique parmi les  trois proposées qui va offrir le meilleur comprimis entre l'**exactitude des réponses**, la **pertinence**, la **minimisation des hallucinations**, la **latence**, la **complexité technique** et la **capacité d'ébergement en interne**.

## Périmètre de la veille 
le périmètre de la veille technique couvre les aspects ci- dessous :
- Identifier un ou deux modèles de LLM open source performants utilisable pour des FAQ administratives et correspondant aux besoins des collectivités térritoriales.
- Explorer et comprendre les diffèrentes approches de génération de réponses (LLM seul, RAG, Q&A extractif).
- Explorer et identifier les techniques de recherche sémantique et les outils d'embeddings adaptés aux FAQ.
- Explorer les solutions de stockage vectorielles et locales open source 
- Explorer et identifier les methodes d'évaluation et de benchmark existantes pour les systèmes de question-réponses.
- Identifier et selectionner les outils d'industrialisation adaptés au projets (API REST, tests automatisés, CI/CD, monitoring).

## Hors périmètre de la veille:
- APIs commerciales payantes
- Solutions propriétaires non auto-hébergeables
- Interfaces graphiques de démonstration (Streamlit, Gradio)

## Les questions clès de la veille technique

### Questions liées aux modèles IA

- Quels modèles de langage open source sont les plus adaptés aux réponses administratives en français ?

- Quels modèles présentent le moins de risques d’hallucinations dans un contexte factuel ?

### Questions liées aux stratégies A/B/C

- Quelles sont les forces et limites d’un LLM utilisé seul pour une FAQ ?

- En quoi une approche RAG améliore-t-elle la fiabilité des réponses ?

- Quels sont les cas d’usage pertinents pour un modèle de QA extractif ?

### Questions liées aux outils techniques

- Quels embeddings open source offrent de bonnes performances pour des FAQ en français ?

- Quels sont les avantages et limites d’un vector store comme ChromaDB ?

- Quels impacts ces choix ont-ils sur la latence et la complexité du système ?

### Questions liées à l’évaluation

- Quelles métriques sont recommandées pour évaluer un assistant FAQ IA ?

- Comment mesurer objectivement les hallucinations ?

# Résultat attendu de la veille

## Une synthèse des approches existantes
(ce que tu as appris sur les modèles candidats et les stratégies A / B / C)

## Analyse comparative des stratégies A, B et C
(ce que la veille dit sur A / B / C, ce que ça implique pour ton benchmark)

### stratégies A
Deux LLM open source performants pour des FAQ administratives en français sont :

- **Qwen/Qwen2.5-7B-Instruct** : 
- **mistralai/Mistral-7B-Instruct-v0.2** :

### stratégies B 
### Sstratégies C

## Des recommandations techniques pour la phase de benchmark
(ce que ça implique pour ton benchmark : modèles à tester, outils à utiliser, métriques à mesurer, etc.)

## Les premières hypothèses techniques
( ce que tu penses pouvoir faire en phase d’implémentation, en te basant sur ta veille)

# Sources de la veille structurée

## Documentation officielle des bibliothèques et frameworks

## Plateforme Hugging Face

## Blogs techniques et articles spécialisés IA

## Expérience de projets similaires

## Forums techniques (en complément)


Livrables de la veille : **NOTE_CADRAGE.md** et **RAPPORT_VEILLE.md**
