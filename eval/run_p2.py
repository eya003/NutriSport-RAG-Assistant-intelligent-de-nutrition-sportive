"""Evaluate the CURRENT NutriSport retrieval pipeline on labelled questions.

Compares FAISS, BM25 and hybrid (RRF + optional reranker) at K=3/5.
The question labels are manually curated, not an independent benchmark.
No LLM API calls and no user conversation tracking.

Run: python -m eval.run_p2
"""

import argparse
import csv
import json
import math

from src.config import ROOT
from src.corpus import load_corpus
from src.query import detect_language, normalize_query
from src.search import HybridRetriever


MODES = ("dense", "bm25", "hybrid")


def score_retrieval(retrieved, relevant, k):
    """Binary relevance metrics; return None for OOD queries."""

    if not relevant:
        return {
            "hit": None,
            "precision": None,
            "recall": None,
            "mrr": None,
            "ndcg": None,
            "ood_rejected": int(not retrieved),
        }

    ids = retrieved[:k]
    gold = set(relevant)

    hits = [
        int(chunk_id in gold)
        for chunk_id in ids
    ]

    n_hits = sum(hits)

    dcg = sum(
        hit / math.log2(rank + 2)
        for rank, hit in enumerate(hits)
    )

    ideal = sum(
        1 / math.log2(rank + 2)
        for rank in range(min(k, len(gold)))
    )

    return {
        "hit": int(n_hits > 0),
        "precision": n_hits / k,
        "recall": n_hits / len(gold),
        "mrr": next(
            (
                1 / (rank + 1)
                for rank, hit in enumerate(hits)
                if hit
            ),
            0.0,
        ),
        "ndcg": dcg / ideal if ideal else 0.0,
        "ood_rejected": None,
    }


def average(rows, field):
    values = [
        r[field]
        for r in rows
        if r[field] is not None
    ]

    return (
        round(sum(values) / len(values), 4)
        if values
        else None
    )


def evaluate(max_questions=0):

    questions_path = ROOT / "eval" / "questions.json"

    questions = json.loads(
        questions_path.read_text(
            encoding="utf-8"
        )
    )

    if max_questions > 0:
        questions = questions[:max_questions]

    corpus = load_corpus()

    known_ids = {
        item["chunk_id"]
        for item in corpus
    }

    for question in questions:
        unknown = (
            set(question["relevant_ids"])
            - known_ids
        )

        if unknown:
            raise ValueError(
                f"{question['id']}: "
                f"unknown chunk IDs {unknown}"
            )

    retriever = HybridRetriever(corpus)

    rows = []

    for n, item in enumerate(
        questions,
        start=1
    ):

        if item.get("expected_behavior") == "safety":
            print(
                f"[{n}/{len(questions)}] "
                f"{item['id']}: "
                "safety case, skipped in P2"
            )
            continue

        question = item["question"]

        language = detect_language(
            question,
            fallback="en"
        )

        normalized = normalize_query(
            question,
            language
        )

        relevant = item["relevant_ids"]
        topic = item.get("topic", "all")

        print(
            f"\n[{n}/{len(questions)}] "
            f"{item['id']} | {language} | {question}"
        )

        for mode in MODES:

            # One top-5 search, evaluated at K=3 and K=5.
            passages = retriever.search(
                normalized,
                mode=mode,
                top_k=5,
                topic=topic,
                language=language,
            )

            retrieved = [
                p["chunk_id"]
                for p in passages
            ]

            print(
                f"  {mode:6s}: {retrieved}"
            )

            for k in (3, 5):

                metrics = score_retrieval(
                    retrieved,
                    relevant,
                    k
                )

                rows.append({
                    "query_id": item["id"],
                    "question": question,
                    "language": language,
                    "mode": mode,
                    "k": k,
                    "answerable": bool(
                        item["answerable"]
                    ),
                    "retrieved_ids": "|".join(
                        retrieved[:k]
                    ),
                    "relevant_ids": "|".join(
                        relevant
                    ),
                    **metrics,
                })

    output = ROOT / "results"
    output.mkdir(exist_ok=True)

    if rows:
        csv_path = output / "p2_retrieval.csv"

        with csv_path.open(
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as stream:

            writer = csv.DictWriter(
                stream,
                fieldnames=list(rows[0])
            )

            writer.writeheader()
            writer.writerows(rows)

    report = []

    for mode in MODES:
        for k in (3, 5):

            selected = [
                r for r in rows
                if r["mode"] == mode
                and r["k"] == k
            ]

            answerable = [
                r for r in selected
                if r["answerable"]
            ]

            ood = [
                r for r in selected
                if not r["answerable"]
            ]

            report.append({
                "mode": mode,
                "k": k,
                "n_answerable": len(answerable),
                "n_out_of_domain": len(ood),
                "hit_at_k": average(
                    answerable, "hit"
                ),
                "precision_at_k": average(
                    answerable, "precision"
                ),
                "recall_at_k": average(
                    answerable, "recall"
                ),
                "mrr_at_k": average(
                    answerable, "mrr"
                ),
                "ndcg_at_k": average(
                    answerable, "ndcg"
                ),
                "ood_rejection_rate": average(
                    ood, "ood_rejected"
                ),
            })

    summary = {
        "kind": "real_pipeline_retrieval",
        "n_questions": len(questions),
        "note": (
            "Manual reference labels; small, "
            "non-independent dataset. "
            "OOD rejection only measures whether "
            "retrieval returned zero chunks. "
            "Thresholds and gold labels require "
            "human validation."
        ),
        "metrics": report,
    }

    (output / "p2_retrieval.json").write_text(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("\n=== P2 SUMMARY ===")

    print(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        )
    )

    print(
        "\nSaved: results/p2_retrieval.csv "
        "+ results/p2_retrieval.json"
    )

    return summary


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--max-q",
        type=int,
        default=0,
        help="Evaluate the first N questions (0 = all)."
    )

    args = parser.parse_args()

    evaluate(
        max_questions=args.max_q
    )