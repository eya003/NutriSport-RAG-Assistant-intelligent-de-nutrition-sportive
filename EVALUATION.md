# Rapport de validation P2 / P3 — interprétation rigoureuse

## P2 : retrieval

- Unité : chunk étiqueté `C001`–`C026`, sans doublons d'ID.
- Questions : `eval/questions.json`, 16 answerables + 4 hors corpus. Pertinence annotée à la main ; **jeu de petite taille, non indépendant du corpus**.
- Comparaisons : FAISS / BM25 / FAISS+BM25(RRF), k=3 et k=5, Hit@k, Recall@k, MRR@k.
- Exécution hors ligne possible avec `--proxy` mais c'est TF-IDF et non un résultat FAISS. Ne pas confondre les deux.
- Attention : le classement dense utilise les passages entiers et une représentation multilingue ; le lexical utilise une tokenisation Unicode simple.

## P3 : génération

- Trois critères : (1) citations valides / récupérées ; (2) fidélité réponse–passages (évaluer chaque affirmation) ; (3) abstention pertinente sur 4 questions hors corpus.
- `run_p3.py` mesure automatiquement (1) et un test contrôlé de (3). `faithfulness_manual` reste `NOT_RATED`. Faire annoter au moins 10 réponses par deux étudiants puis calculer l'accord.
- Les questions sans réponse sont pré-marquées dans ce script et alimentées avec une liste de passages vide : **pas une détection autonome de la non-réponse**. Pour le produit, un vrai système d'abstention doit être validé sur des scores de pertinence calibrés.
- Sans API, `offline_answer` ne produit que des extraits anglais et ne constitue pas une évaluation de qualité LLM ni de multilinguisme.

## Critères suggérés, à annoncer comme objectifs et non comme résultats

- Retrieval : Hit@3 >= 0.75 (échantillon trop petit pour conclusion générale), Recall@5 vs Recall@3.
- P3 : 100% citations appartenant aux passages récupérés ; >= 90% affirmations factuelles réellement soutenues (annotation manuelle) ; bonne gestion des questions absentes.
- Noter erreurs, exemples d'hallucination, temps de réponse, et limitations de la langue arabe.

## Améliorations appliquées

- Déduplication, extraction selon sections, suppression d'éléments de navigation, liens sources conservés.
- Embeddings normalisés pour FAISS cosine, fusion RRF indépendante des échelles de score.
- Métadonnées `topic` pour limiter le domaine; documents généraux partagés aux deux objectifs.
- Séparation stricte entre synthèses initiales et documents intégralement téléchargés.
- Deux modes : réel API (LLM) et démo extractive clairement annoncée, aucune réponse factice présentée comme modèle.
- Tests unitaires pour cleaning, overlap, Unicode arabe, RRF, citations et refus faute de source.
