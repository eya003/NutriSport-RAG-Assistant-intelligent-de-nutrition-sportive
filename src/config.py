"""Configuration shared by the NutriSport RAG pipeline."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DEFAULT_CORPUS = DATA / "curated_evidence.json"

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
RERANK_ENABLED = os.getenv("NUTRISPORT_RERANK", "1") != "0"
RERANK_CANDIDATES = 12

# Rank-level blend: 0 = pure RRF, 1 = pure Cross-Encoder.
# This is an initial choice, not an empirically optimized value.
RERANK_WEIGHT = float(os.getenv("NUTRISPORT_RERANK_WEIGHT", "0.30"))
if not 0 <= RERANK_WEIGHT <= 1:
    raise ValueError("NUTRISPORT_RERANK_WEIGHT must be between 0 and 1")

# Preliminary rejection threshold; calibrate with labelled OOD queries.
MIN_DENSE_SIMILARITY = float(os.getenv("NUTRISPORT_MIN_SIM", "0.23"))
RRF_CONSTANT = 60
CHUNK_WORDS = 180
CHUNK_OVERLAP = 35