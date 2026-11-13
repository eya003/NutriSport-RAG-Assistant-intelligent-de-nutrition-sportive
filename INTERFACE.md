# NutriSport RAG — Interface utilisateur (P4)

Cette version remplace l'interface technique par une expérience pensée pour les sportifs et les personnes souhaitant gérer leur poids.

## Parcours utilisateur

1. **Accueil :** un bandeau nutrition/sport, un champ de question, quatre suggestions prêtes à utiliser et trois cartes d'objectif.
2. **Objectifs :** prise de muscle / gestion du poids / nutrition générale. Le choix filtre les passages du corpus recherchés par P2 pour les prochains messages.
3. **Réponse :** Grok (si `XAI_API_KEY` existe), sinon des extraits du corpus sont **explicitement identifiés comme hors ligne**.
4. **Sources :** un accordéon affiche les passages utilisés et renvoie vers les documents. Il reste fermé par défaut pour ne pas surcharger l'interface.
5. **Conseils :** un petit carrousel manuel de conseils **sourcés**, avec un lien vers la publication d'origine. Il n'effectue pas de recommandations médicales personnalisées.
6. **Conversations :** l'historique est conservé en mémoire pendant la session Streamlit.
7. **Conseils enregistrés :** l'utilisateur peut sauvegarder une réponse pendant sa session. Aucune base de données ni persistance après redémarrage n'est fournie.
8. **Langue :** français, anglais et arabe pour les libellés, questions et réponses avec Grok. Les sources sont principalement en anglais ; BM25 est lexical et le modèle d'embeddings est multilingue.

## Où sont les réglages techniques ?

Le panneau **🔬 Les coulisses du RAG** du menu latéral (fermé au démarrage) conserve les fonctions d'évaluation exigées par le professeur :

- FAISS, BM25 ou Hybride RRF ;
- top-3 / top-5 ;
- Grok ou extraits documentaires sans modèle.

Les scripts `eval/run_p2.py` et `eval/run_p3.py` restent inchangés.

## Démarrage local

```bash
python -m venv .venv
# Windows PowerShell : .venv\Scripts\Activate.ps1
# Linux/macOS : source .venv/bin/activate
pip install -r requirements.txt
# Copier .env.example vers .env et renseigner XAI_API_KEY pour Grok
streamlit run app.py
```

Le premier lancement d'une question peut nécessiter le téléchargement du modèle Sentence-Transformers. Cette étape requiert Internet.

## Emplacement des fichiers de l'interface

- `app.py` : pages et interactions Streamlit.
- `src/ui_content.py` : libellés FR/EN/AR, questions suggérées, conseils avec sources.
- `src/ui_theme.py` : thème CSS responsive et petites animations.
- `assets/hero_nutrition.webp` : illustration locale dérivée de la maquette de design, aucune image distante requise.
- `.streamlit/config.toml` : configuration du thème Streamlit.

## Limites connues

- Le corpus fourni par défaut est composé de **synthèses éditoriales sourcées**. Ce ne sont pas les passages intégraux originaux. L'ingestion des documents d'origine est disponible dans `src/ingest.py`.
- L'interface n'est pas une consultation de nutrition clinique et ne propose pas de menus médicaux individualisés.
- Aucun calculateur de calories par aliment n'est inclus dans cette version.
- Le design a été testé statiquement ; l'exécution graphique et les appels Grok réels doivent être validés sur le poste de l'équipe avec les dépendances installées et une clé API valide.
