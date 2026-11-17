"""Multilingual retrieval: FAISS + English BM25 + RRF + optional reranking.

No database or query history is persisted.
RRF scores are rank-based, dense similarity is cosine,
and reranker scores are raw logits, not probabilities.
"""

import re
import unicodedata

import numpy as np

from .config import (
    EMBEDDING_MODEL,
    RERANKER_MODEL,
    RERANK_ENABLED,
    RERANK_CANDIDATES,
    RRF_CONSTANT,
    MIN_DENSE_SIMILARITY,
)


TRANSLATION_MODELS = {
    "fr": "Helsinki-NLP/opus-mt-fr-en",
    "ar": "Helsinki-NLP/opus-mt-ar-en",
}


STOPWORDS = set("""
a an the and or but if to of in on at for from by
with without as is are was were be been being
do does did have has had i you he she it we they
me my your our their this that these those there
here what which who whom why how can could would
should will may might about into than then just
now please tell give want need much many one two
aint am its it's im i've i'm not no yes so also
very really
""".split())


def tokenize(text):
    """English lexical tokens with stopword removal."""

    text = unicodedata.normalize(
        "NFKC", text
    ).casefold()

    tokens = re.findall(
        r"[^\W_]+",
        text,
        flags=re.UNICODE
    )

    cleaned = []

    for token in tokens:

        if token in STOPWORDS or len(token) < 2:
            continue

        if token in (
            "proteins",
            "muscles",
            "exercises",
            "athletes",
            "calories"
        ):
            token = token[:-1]

        cleaned.append(token)

    return cleaned


def rrf(rankings, constant=RRF_CONSTANT):
    """Reciprocal Rank Fusion."""

    scores = {}

    for ranking in rankings:
        for rank, idx in enumerate(
            ranking, start=1
        ):
            scores[idx] = (
                scores.get(idx, 0.0)
                + 1.0 / (constant + rank)
            )

    ranked = sorted(
        scores,
        key=lambda i: (-scores[i], i)
    )

    return ranked, scores


class HybridRetriever:

    def __init__(
        self,
        corpus,
        model_name=EMBEDDING_MODEL,
        backend="faiss"
    ):

        if not corpus:
            raise ValueError("Empty corpus")

        if backend not in ("faiss", "numpy"):
            raise ValueError(
                "backend must be 'faiss' or 'numpy'"
            )

        self.corpus = corpus
        self.model_name = model_name
        self.backend = backend

        self.texts = [
            p["text"] for p in corpus
        ]

        self._translators = {}
        self._translation_cache = {}

        self._reranker = None
        self._reranker_failed = False

        from rank_bm25 import BM25Okapi
        from sentence_transformers import SentenceTransformer

        # BM25 index
        self.lex_tokens = [
            tokenize(text)
            for text in self.texts
        ]

        self.bm25 = BM25Okapi(
            self.lex_tokens
        )

        # Dense embeddings
        self.encoder = SentenceTransformer(
            model_name
        )

        self.vectors = np.asarray(
            self.encoder.encode(
                self.texts,
                normalize_embeddings=True,
                show_progress_bar=False
            ),
            dtype="float32"
        )

        # FAISS index
        self.index = None

        if backend == "faiss":
            import faiss

            self.index = faiss.IndexFlatIP(
                self.vectors.shape[1]
            )

            self.index.add(
                self.vectors
            )

            print(
                f"[FAISS] Indexed "
                f"{self.index.ntotal} vectors",
                flush=True
            )

    def _translate_to_english(
        self,
        query,
        language
    ):
        """Translate query for English lexical retrieval."""

        if language == "en":
            print(
                "[TRANSLATION] English query: "
                "no translation",
                flush=True
            )
            return query

        if language not in TRANSLATION_MODELS:
            print(
                f"[TRANSLATION] Unsupported "
                f"language {language}",
                flush=True
            )
            return None

        cache_key = (language, query)

        if cache_key in self._translation_cache:
            result = self._translation_cache[
                cache_key
            ]

            print(
                f"[TRANSLATION] Cached query: "
                f"{result}",
                flush=True
            )

            return result

        if language not in self._translators:

            model_name = TRANSLATION_MODELS[
                language
            ]

            print(
                f"[TRANSLATION] Loading {model_name}",
                flush=True
            )

            try:
                from transformers import (
                    AutoTokenizer,
                    AutoModelForSeq2SeqLM
                )

                tokenizer = AutoTokenizer.from_pretrained(
                    model_name
                )

                model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name
                )

                model.eval()

                self._translators[language] = (
                    tokenizer,
                    model
                )

            except Exception as exc:
                print(
                    f"[TRANSLATION] Loading failed: "
                    f"{exc}",
                    flush=True
                )

                self._translators[language] = None

        translator = self._translators[
            language
        ]

        if translator is None:
            return None

        try:
            import torch

            tokenizer, model = translator

            encoded = tokenizer(
                query,
                return_tensors="pt",
                truncation=True,
                max_length=256
            )

            with torch.inference_mode():
                ids = model.generate(
                    **encoded,
                    max_new_tokens=96,
                    num_beams=3,
                    do_sample=False
                )

            result = tokenizer.decode(
                ids[0],
                skip_special_tokens=True
            ).strip()

            if not result:
                return None

            if len(self._translation_cache) >= 128:
                first_key = next(
                    iter(self._translation_cache)
                )
                del self._translation_cache[
                    first_key
                ]

            self._translation_cache[
                cache_key
            ] = result

            print(
                f"[TRANSLATION] {language} -> en: "
                f"{result}",
                flush=True
            )

            return result

        except Exception as exc:
            print(
                f"[TRANSLATION] Failed: {exc}",
                flush=True
            )
            return None

    def _rank_dense(
        self,
        query,
        ids
    ):
        """Rank chunks with cosine similarity."""

        q = np.asarray(
            self.encoder.encode(
                [query],
                normalize_embeddings=True
            ),
            dtype="float32"
        )

        if (
            self.index is not None
            and len(ids) == len(self.corpus)
        ):

            raw_scores, indices = (
                self.index.search(
                    q,
                    len(self.corpus)
                )
            )

            ranked = [
                int(i)
                for i in indices[0]
                if i >= 0
            ]

            similarities = {
                int(i): float(s)
                for i, s in zip(
                    indices[0],
                    raw_scores[0]
                )
                if i >= 0
            }

            return ranked, similarities

        scores = self.vectors @ q[0]

        ranked = sorted(
            ids,
            key=lambda i: (
                -float(scores[i]),
                i
            )
        )

        return ranked, {
            i: float(scores[i])
            for i in ids
        }

    def _rerank(
        self,
        english_query,
        ids
    ):
        """Rerank candidates with an English cross-encoder."""

        if (
            not RERANK_ENABLED
            or not english_query
            or len(ids) <= 1
        ):
            return None

        if self._reranker_failed:
            return None

        if self._reranker is None:
            try:
                from sentence_transformers import (
                    CrossEncoder
                )

                print(
                    f"[RERANK] Loading "
                    f"{RERANKER_MODEL}",
                    flush=True
                )

                self._reranker = CrossEncoder(
                    RERANKER_MODEL
                )

            except Exception as exc:
                self._reranker_failed = True

                print(
                    f"[RERANK] Unavailable: {exc}; "
                    "keeping RRF order",
                    flush=True
                )

                return None

        try:

            pairs = [
                (
                    english_query,
                    self.texts[i]
                )
                for i in ids
            ]

            logits = np.asarray(
                self._reranker.predict(
                    pairs,
                    batch_size=8,
                    show_progress_bar=False
                )
            ).reshape(-1)

            return {
                i: float(value)
                for i, value in zip(
                    ids,
                    logits
                )
            }

        except Exception as exc:

            print(
                f"[RERANK] Failed: {exc}; "
                "keeping RRF order",
                flush=True
            )

            return None

    def search(
        self,
        query,
        mode="hybrid",
        top_k=3,
        topic="all",
        pool=20,
        language="fr"
    ):
        """Retrieve relevant chunks."""

        if mode not in (
            "dense",
            "bm25",
            "hybrid"
        ):
            raise ValueError(
                "mode must be 'dense', "
                "'bm25' or 'hybrid'"
            )

        if top_k < 1 or pool < 1:
            raise ValueError(
                "top_k and pool must be positive"
            )

        # Topic filtering
        ids = [
            i
            for i, p in enumerate(
                self.corpus
            )
            if topic == "all"
            or p["topic"] in (
                topic,
                "general"
            )
        ]

        if not ids:
            return []

        candidate_n = min(
            pool,
            len(ids)
        )

        dense_pool = []
        sparse_pool = []

        dense_scores = {}
        lexical_scores = None
        english_query = None

        # Dense retrieval
        if mode in (
            "dense",
            "hybrid"
        ):

            print(
                "[FAISS] Searching with "
                "original multilingual query",
                flush=True
            )

            dense, dense_scores = (
                self._rank_dense(
                    query,
                    ids
                )
            )

            dense_pool = dense[
                :candidate_n
            ]

            print(
                f"[FAISS] Best cosine: "
                f"{dense_scores[dense[0]]:.4f}",
                flush=True
            )

        # Lexical retrieval
        if mode in (
            "bm25",
            "hybrid"
        ):

            english_query = (
                self._translate_to_english(
                    query,
                    language
                )
            )

            if english_query:

                tokens = tokenize(
                    english_query
                )

                if tokens:
                    lexical_scores = (
                        self.bm25.get_scores(
                            tokens
                        )
                    )
                else:
                    lexical_scores = np.zeros(
                        len(self.corpus)
                    )

                sparse = sorted(
                    ids,
                    key=lambda i: (
                        -float(
                            lexical_scores[i]
                        ),
                        i
                    )
                )

                sparse_pool = [
                    i
                    for i in sparse
                    if lexical_scores[i] > 0
                ][:candidate_n]

                print(
                    f"[BM25] Query: "
                    f"{english_query}",
                    flush=True
                )

                print(
                    f"[BM25] Tokens: "
                    f"{tokens}",
                    flush=True
                )

                print(
                    "[BM25] Positive-score documents: "
                    f"{len(sparse_pool)}",
                    flush=True
                )

                for i in sparse_pool[:3]:
                    print(
                        f"[BM25] "
                        f"{self.corpus[i]['chunk_id']} "
                        f"| Raw score: "
                        f"{lexical_scores[i]:.4f}",
                        flush=True
                    )

            else:
                print(
                    "[BM25] Translation unavailable; "
                    "no lexical candidates",
                    flush=True
                )

        # Preliminary relevance screening
        if mode in (
            "dense",
            "hybrid"
        ):

            best_dense = (
                dense_scores[dense_pool[0]]
                if dense_pool else -1.0
            )

            if (
                best_dense < MIN_DENSE_SIMILARITY
                and not sparse_pool
            ):
                print(
                    "[FILTER] No convincing semantic "
                    "or lexical match; abstaining",
                    flush=True
                )
                return []

        rerank_scores = None

        # Ranking selection
        if mode == "dense":

            ranked = dense_pool

            scores = {
                i: 1.0 / (rank + 1)
                for rank, i in enumerate(
                    ranked
                )
            }

            print(
                "[SEARCH] FAISS only",
                flush=True
            )

        elif mode == "bm25":

            ranked = sparse_pool

            scores = {
                i: 1.0 / (rank + 1)
                for rank, i in enumerate(
                    ranked
                )
            }

            print(
                "[SEARCH] BM25 only",
                flush=True
            )

        elif not sparse_pool:

            ranked = dense_pool

            scores = {
                i: 1.0 / (rank + 1)
                for rank, i in enumerate(
                    ranked
                )
            }

            print(
                "[RRF] No useful BM25 results: "
                "FAISS fallback",
                flush=True
            )

        else:

            ranked, scores = rrf([
                dense_pool,
                sparse_pool
            ])

            print(
                "[RRF] Combining FAISS and BM25",
                flush=True
            )

            candidates = ranked[
                :min(
                    RERANK_CANDIDATES,
                    len(ranked)
                )
            ]

            rerank_scores = self._rerank(
                english_query,
                candidates
            )

            if rerank_scores:

                ranked = sorted(
                    candidates,
                    key=lambda i: (
                        -rerank_scores[i],
                        -scores[i],
                        i
                    )
                )

                print(
                    "[RERANK] Cross-encoder "
                    "reordered candidates",
                    flush=True
                )

        # Build output
        results = []

        for rank, i in enumerate(
            ranked[:top_k],
            start=1
        ):

            p = dict(
                self.corpus[i]
            )

            p.update(
                score=round(
                    float(scores[i]),
                    6
                ),
                rank=rank,
                dense_similarity=(
                    round(
                        dense_scores[i],
                        4
                    )
                    if i in dense_scores
                    else None
                ),
                bm25_score=(
                    round(
                        float(
                            lexical_scores[i]
                        ),
                        4
                    )
                    if lexical_scores is not None
                    else None
                ),
                rerank_score=(
                    round(
                        rerank_scores[i],
                        4
                    )
                    if rerank_scores
                    and i in rerank_scores
                    else None
                )
            )

            results.append(p)

        return results