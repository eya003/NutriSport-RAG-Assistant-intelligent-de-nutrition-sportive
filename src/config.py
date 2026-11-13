from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DEFAULT_CORPUS = DATA / "curated_evidence.json"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# 180 words ~ 240-300 tokens in English; section-first splitting to keep evidence coherent.
CHUNK_WORDS = 180
CHUNK_OVERLAP = 35
RRF_CONSTANT = 60
