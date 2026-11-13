import json
import re
from pathlib import Path
from .config import DEFAULT_CORPUS, CHUNK_WORDS, CHUNK_OVERLAP

def clean_text(value: str) -> str:
    value = re.sub(r"https?://\S+", " ", value)
    value = re.sub(r"\[\s*\d+\s*\]", " ", value)
    value = re.sub(r"(?m)^\s*(?:cookie policy|privacy policy|accept cookies|share this page|back to top)\s*$", " ", value, flags=re.I)
    value = re.sub(r"\s+", " ", value)
    return value.strip()

def split_words(text: str, size: int = CHUNK_WORDS, overlap: int = CHUNK_OVERLAP):
    if not (size > overlap >= 0):
        raise ValueError("size must exceed overlap >= 0")
    words = clean_text(text).split()
    if not words:
        return []
    out, step = [], size - overlap
    for start in range(0, len(words), step):
        part = words[start:start+size]
        if part:
            out.append(" ".join(part))
        if start+size >= len(words):
            break
    return out

def load_corpus(path=DEFAULT_CORPUS):
    data=json.loads(Path(path).read_text(encoding='utf8'))
    ids=set()
    for item in data:
        for key in ('chunk_id','text','source_title','source_url','topic'):
            if not item.get(key):
                raise ValueError(f"Missing {key}: {item}")
        if item['chunk_id'] in ids:
            raise ValueError(f"Duplicate chunk: {item['chunk_id']}")
        ids.add(item['chunk_id'])
    return data
