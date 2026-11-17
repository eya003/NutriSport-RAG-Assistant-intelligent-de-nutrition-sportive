"""Lightweight multilingual query normalization and language detection.

No LLM call, no user-query storage and no changes to user intent.
"""

import re
import unicodedata


_REPLACEMENTS = {
    "fr": [
        (r"\bj['’]?viens\b", "je viens"),
        (r"\bchui\b", "je suis"),
        (r"\bjsuis\b", "je suis"),
        (r"\bmuscu\b", "musculation"),
        (r"\bworkout\b", "entraînement"),
        (r"\bmtenant\b|\bmtn\b", "maintenant"),
        (r"\bvrm\b", "vraiment"),
        (r"\bqqch\b", "quelque chose"),
        (r"\bpk\b|\bprk\b", "pourquoi"),
        (r"\bprots\b", "protéines"),
        (r"\bfaut manger quoi\b", "que faut-il manger"),
        (r"\bchui ko\b|\bje suis ko\b", "je suis épuisé"),
    ],
    "en": [
        (r"\bworkout\b", "exercise session"),
        (r"\bpost[- ]workout\b", "after exercise"),
        (r"\bprots\b", "protein"),
        (r"\bpls\b", "please"),
    ],
}

_EN_WORDS = {
    "what", "why", "how", "when", "which", "should",
    "does", "do", "can", "is", "are", "eat", "after",
    "before", "muscle", "protein", "recovery",
    "training", "exercise", "food", "weight", "diet",
    "help", "much", "need", "my", "i"
}

_FR_WORDS = {
    "quel", "quelle", "quels", "quelles", "comment",
    "pourquoi", "est", "sont", "des", "les", "une",
    "apres", "avant", "quoi", "manger", "muscu",
    "musculation", "proteines", "entrainement",
    "faut", "je", "jviens", "chui", "mtn", "maintenant"
}


def _ascii(text):
    return "".join(
        c
        for c in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(c)
    )


def detect_language(question, fallback="fr"):
    """Override UI language only when query language is clear."""

    if re.search(r"[\u0600-\u06ff]", question):
        return "ar"

    words = set(
        re.findall(r"[a-z]+", _ascii(question))
    )

    en_count = len(words & _EN_WORDS)
    fr_count = len(words & _FR_WORDS)

    if en_count >= 2 and en_count >= fr_count + 2:
        return "en"

    if fr_count >= 2 and fr_count >= en_count + 1:
        return "fr"

    return (
        fallback
        if fallback in ("fr", "en", "ar")
        else "fr"
    )


def normalize_query(question, language="fr"):
    """Expand known informal expressions."""

    result = unicodedata.normalize(
        "NFKC", question
    ).strip()

    result = re.sub(r"\s+", " ", result)

    for pattern, replacement in _REPLACEMENTS.get(
        language, []
    ):
        result = re.sub(
            pattern,
            replacement,
            result,
            flags=re.IGNORECASE
        )

    if language == "fr":
        x = _ascii(result)

        if (
            "manger" in x or "repas" in x
        ) and (
            "musculation" in x
            or "entrainement" in x
            or "apres le sport" in x
        ):
            result += (
                " ; alimentation pour la récupération "
                "après l'entraînement"
            )

    return result


def is_followup(question):
    """Detect short elliptical conversational follow-ups."""

    q = _ascii(question).strip()

    return len(q.split()) <= 14 and bool(
        re.match(
            r"^(et si\b|et pour\b|et du coup\b|"
            r"what about\b|and if\b|"
            r"and what about\b|"
            r"qu'en est-il\b|sinon pour\b)",
            q
        )
    )