# NutriSport RAG — Nutrition sportive & gestion du poids

Projet universitaire de recherche augmentée (RAG), **information éducative non médicale**.

## État réel des fonctionnalités

- **P1 corpus :** 26 synthèses originales, attribuées à cinq sources reconnues. Elles sont **des paraphrases éditoriales**, et NON des extraits de documents originaux. Provenance indiquée dans chaque enregistrement. Téléchargeur facultatif pour créer un corpus à partir des textes HTML originaux.
- **P2 :** Sentence-Transformers multilingue + FAISS (produit scalaire sur vecteurs normalisés ≈ cosine), BM25 et RRF; modes dense/BM25/hybride, top-3/top-5.
- **P3 :** prompting sourcé, réponses FR/EN/AR avec l’API Grok de xAI; sans clé, mode **extraits documentaires**, qui n'est PAS un LLM.
- **Interface :** nouvel accueil orienté utilisateur (bandeau sport, suggestions de questions, cartes d'objectif, discussion, conseils sourcés, historique et favoris de session). Réglages RAG dans un panneau avancé fermé par défaut ; voir `INTERFACE.md`.
- **Évaluation :** jeu de 20 questions annotées; scripts P2/P3; noter les limitations ci-dessous.

## Installation (Python 3.11 conseillé)

```bash
python -m venv .venv
# Linux/macOS : source .venv/bin/activate
# Windows : .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```

Le premier démarrage **télécharge le modèle d'embeddings** (~ centaines de Mo), sauf s'il est déjà en cache. Prévoir Internet. Les poids du modèle et la clé API ne sont pas inclus dans le ZIP.

## API LLM facultative

Copier `.env.example` vers `.env` et renseigner `XAI_API_KEY`. Le fichier `.env` est chargé automatiquement par `src/answer.py` lorsque l'application démarre. Sinon choisir le mode « Extraits seulement » : ce mode n'est **pas une génération LLM**.

## Récupération des documents entiers (Internet requis)

```bash
python -m src.ingest
```

Le script produit `data/full_text/downloaded_chunks.json`. **Inspecter les passages** (bibliographies, mentions légales, sections non pertinentes), puis utiliser un corpus contrôlé avec :

```python
from src.pipeline import NutriSport
app = NutriSport(corpus_path='data/full_text/downloaded_chunks.json')
```

La version livrée se lance sur le petit corpus de synthèses pour un mode démonstration reproductible; pour une soutenance rigoureuse, préférer le corpus intégral nettoyé et faire réannoter le jeu de test (IDs changés).

## Décisions techniques

- **Chunk = 180 mots, overlap 35 mots**, découpé après segmentation en sections HTML ; pour ce corpus éducatif, cela limite la troncature de recommandations et fournit un contexte compact. À valider empiriquement avec `Recall@3/5` ; ce n'est pas une taille universellement optimale.
- **`paraphrase-multilingual-MiniLM-L12-v2`** : modèle d'embeddings multilingue raisonnablement léger, adapté à FR/EN/AR. Le téléchargement est requis. Une alternative plus puissante est `intfloat/multilingual-e5-small`, mais elle nécessite les préfixes query/passage et un benchmark comparatif.
- **FAISS `IndexFlatIP`** : exact sur petit corpus, vecteurs L2-normalisés ⇒ proximité cosinus.
- **BM25** : tokenisation Unicode simple. Les questions AR/FR face à un corpus EN peuvent mal fonctionner lexiquement ; FAISS multilingue compense partiellement. Une traduction de requête via LLM ou corpus réellement multilingue peut améliorer ce point.
- **RRF** : somme 1/(60+rang) sur deux listes de candidats, évite de fusionner des scores incompatibles. Scores affichés ne sont **pas** des probabilités.
- **Source-first** : chaque chunk conserve URL, titre, section, thème et provenance.

## Évaluation

```bash
python -m eval.run_p2               # réelle : modèle + FAISS + BM25
python -m eval.run_p2 --proxy       # hors-ligne : TF-IDF (PAS des embeddings FAISS)
python -m eval.run_p3 --provider offline --fixture  # test documenté sans modèle ni FAISS
python -m eval.run_p3 --provider offline  # P2 réel requis ; PAS un test LLM
python -m eval.run_p3 --provider auto     # API requise
```

P2 produit CSV + JSON pour Hit@k, Recall@k et MRR@k sur **16 questions répondues** annotées manuellement. Les 4 questions sans réponse servent à P3 et ne sont pas incluses dans la moyenne de recherche.

P3 vérifie les identifiants des citations. **La fidélité des réponses n'est pas mesurée automatiquement** ; compléter les colonnes `faithfulness_manual` et `helpfulness_manual` du CSV après lecture des sources. Les quatre cas sans réponse sont explicitement injectés avec aucun passage (*oracle gating*) : le résultat **ne prouve pas** qu'un RAG sait détecter tout seul les questions hors corpus.

Pour l'évaluation de l'abstention en conditions réelles, créer un seuil de pertinence calibré sur un jeu de validation indépendant puis tester sur un jeu séparé. Ne pas utiliser le score RRF comme probabilité.

## Limites et sécurité

Aucune prescription individualisée, diagnostic, régime restrictif ou calories journalières personnalisées. L'app ne fournit pas de calculateur calorique non vérifié. Les conversations et les conseils enregistrés ne persistent que pendant la session Streamlit. Les sources sont principalement anglophones et des positions scientifiques de dates différentes. L'application peut citer des sections non optimales ; validation humaine nécessaire pour les usages santé.

## Répartition sur 4 étudiants

1. **P1 — Corpus :** télécharger, nettoyer, contrôler les sources, valider 180/35, vérifier le JSON.
2. **P2 — Retrieval :** FAISS, BM25, RRF, top-k, expériences et figures d'évaluation.
3. **P3 — LLM :** prompting, citations, français/arabe/anglais, tests de fidélité et refus.
4. **P4 — Produit :** UI Streamlit, intégration, tests, README, démonstration.

Tous participent aux tests de bout en bout, au rapport et à la soutenance.

## Nouvelle interface (P4)

L'accueil de l'application a été redessiné : conseils nutritionnels sourcés, objectifs cliquables, suggestions de questions, historique de la session, réponses sauvegardées et langues FR/EN/AR. L'illustration est incluse localement dans `assets/`. Les choix internes FAISS / BM25 / RRF et top-k restent disponibles pour la soutenance sous **Les coulisses du RAG**. Voir `INTERFACE.md` pour les limites et le parcours utilisateur.

## Structure

```
app.py
assets/hero_nutrition.webp
src/{config,corpus,ingest,search,answer,pipeline,ui_content,ui_theme}.py
data/{sources.json,curated_evidence.json}
eval/{questions.json,run_p2.py,run_p3.py}
tests/test_core.py
results/          # mesures obtenues, datées dans le rapport
```

## Sources

Les cinq URLs exactes figurent dans `data/sources.json`. Pas de téléchargement automatique ni de données personnelles.
