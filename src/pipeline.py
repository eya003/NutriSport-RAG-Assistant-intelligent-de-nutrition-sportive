"""NutriSport RAG orchestration.

No database or persistent user history.
"""

import os
import time

from .answer import (
    generate,
    is_unsafe_request,
    safety_answer
)

from .config import DEFAULT_CORPUS
from .corpus import load_corpus

from .query import (
    detect_language,
    is_followup,
    normalize_query
)

from .search import HybridRetriever


class NutriSport:

    def __init__(
        self,
        corpus_path=None,
        backend="faiss"
    ):

        start = time.perf_counter()

        path = (
            corpus_path
            or os.getenv("NUTRISPORT_CORPUS_PATH")
            or DEFAULT_CORPUS
        )

        print(
            f"\n[INIT] Loading corpus: {path}",
            flush=True
        )

        self.docs = load_corpus(path)

        print(
            f"[INIT] {len(self.docs)} chunks loaded",
            flush=True
        )

        self.retriever = HybridRetriever(
            self.docs,
            backend=backend
        )

        index_size = (
            self.retriever.index.ntotal
            if self.retriever.index is not None
            else len(self.docs)
        )

        print(
            f"[INIT] {index_size} vectors ready in "
            f"{time.perf_counter() - start:.2f}s",
            flush=True
        )

    def ask(
        self,
        question,
        topic="all",
        language="fr",
        mode="hybrid",
        top_k=3,
        provider="auto",
        history=None
    ):

        question = question.strip()

        print(
            f"\n[QUESTION] {question}",
            flush=True
        )

        start = time.perf_counter()

        actual_language = detect_language(
            question,
            fallback=language
        )

        if actual_language != language:
            print(
                f"[LANGUAGE] Auto-detected "
                f"{actual_language} (UI: {language})",
                flush=True
            )

        # Safety check before retrieval
        if is_unsafe_request(question):

            print(
                "[SAFETY] Skipping retrieval "
                "for an extreme diet prescription",
                flush=True
            )

            return dict(
                answer=safety_answer(
                    actual_language
                ),
                status="unsafe_request",
                passages=[]
            )

        # Normalize informal questions
        search_question = normalize_query(
            question,
            actual_language
        )

        # Lightweight context for follow-up questions
        if is_followup(question) and history:

            previous = (
                history[-1].get("question", "")
                if isinstance(
                    history[-1], dict
                )
                else ""
            )

            if previous:

                previous_language = detect_language(
                    previous,
                    actual_language
                )

                previous_query = normalize_query(
                    previous,
                    previous_language
                )

                search_question = (
                    previous_query
                    + " "
                    + search_question
                )

                print(
                    "[CONTEXT] Using last user question "
                    "for elliptical follow-up",
                    flush=True
                )

        if search_question != question:
            print(
                f"[QUERY] Normalized retrieval query: "
                f"{search_question}",
                flush=True
            )

        print(
            f"[RETRIEVAL] Mode: {mode}, "
            f"Top-K: {top_k}",
            flush=True
        )

        retrieved = self.retriever.search(
            search_question,
            mode=mode,
            top_k=top_k,
            topic=topic,
            language=actual_language
        )

        print(
            "[RETRIEVAL] Completed in "
            f"{time.perf_counter() - start:.2f}s",
            flush=True
        )

        for p in retrieved:

            log = (
                f"  Rank {p['rank']} "
                f"| {p['chunk_id']} "
                f"| score={p['score']:.6f}"
            )

            if p.get("dense_similarity") is not None:
                log += (
                    f" | cosine="
                    f"{p['dense_similarity']:.4f}"
                )

            if p.get("rerank_score") is not None:
                log += (
                    f" | rerank_logit="
                    f"{p['rerank_score']:.3f}"
                )

            print(
                log,
                flush=True
            )

        print(
            "[AUGMENTATION] Preparing cited evidence",
            flush=True
        )

        model = (
            os.getenv("OPENROUTER_MODEL")
            or os.getenv("XAI_MODEL")
            or "openrouter/free"
        )

        print(
            f"[GENERATION] Model: {model} "
            f"| Provider: {provider}",
            flush=True
        )

        llm_start = time.perf_counter()

        response, status = generate(
            question,
            retrieved,
            language=actual_language,
            provider=provider,
            history=history
        )

        print(
            f"[GENERATION] Status: {status}",
            flush=True
        )

        print(
            "[GENERATION] Time: "
            f"{time.perf_counter() - llm_start:.2f}s",
            flush=True
        )

        print(
            f"[TOTAL] "
            f"{time.perf_counter() - start:.2f}s\n",
            flush=True
        )

        return dict(
            answer=response,
            status=status,
            passages=retrieved
        )