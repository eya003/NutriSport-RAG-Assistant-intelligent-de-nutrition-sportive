"""OPTIONAL: download and chunk the linked scientific HTML pages.

Never runs at application startup.
Generates a JSON file to review before use.
"""

import argparse
import json
import re

from collections import Counter

import requests

from bs4 import BeautifulSoup

from .config import DATA
from .corpus import clean_text, split_words


EXCLUDED_HEADINGS = re.compile(
    r"^(references|bibliography|acknowledgments?|"
    r"author (information|contributions)|"
    r"competing interests|conflicts? of interest|"
    r"supplementary (data|materials?)|"
    r"cite this|further reading|"
    r"related (articles|content)|notes?)\b",
    re.IGNORECASE
)


def extract_sections(html):
    """Extract document sections in DOM order."""

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    for tag in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        "svg"
    ]):
        tag.decompose()

    main = (
        soup.find("article")
        or soup.find("main")
        or soup
    )

    sections = []

    current_heading = "Document overview"
    paragraphs = []
    seen = set()

    stopped = False

    def push():
        if paragraphs:
            sections.append((
                current_heading,
                " ".join(paragraphs)
            ))

    for node in main.find_all([
        "h1",
        "h2",
        "h3",
        "p",
        "li"
    ]):

        if (
            node.name == "li"
            and node.find_parent("li")
        ):
            continue

        if (
            node.name == "p"
            and node.find_parent("li")
        ):
            continue

        value = clean_text(
            node.get_text(
                " ",
                strip=True
            )
        )

        if not value:
            continue

        if node.name.startswith("h"):

            if EXCLUDED_HEADINGS.match(
                value
            ):
                stopped = True
                break

            push()

            current_heading = value[:200]
            paragraphs = []

            continue

        if (
            len(value) < 45
            or value in seen
        ):
            continue

        if value.lower().startswith((
            "copyright ",
            "this article is licensed"
        )):
            continue

        seen.add(value)
        paragraphs.append(value)

    if not stopped:
        push()
    else:
        # Keep the last content section
        # before the references.
        push()

    return sections


def fetch_sources(timeout=20):

    sources = json.loads(
        (
            DATA / "sources.json"
        ).read_text(
            encoding="utf8"
        )
    )

    output = []

    session = requests.Session()

    session.headers["User-Agent"] = (
        "NutriSport-RAG/1.0 "
        "(educational document retrieval)"
    )

    for source in sources:

        try:

            response = session.get(
                source["url"],
                timeout=timeout
            )

            response.raise_for_status()

            sections = extract_sections(
                response.text
            )

            start_count = len(output)

            for section_index, (
                title,
                text
            ) in enumerate(sections):

                for part_index, chunk in enumerate(
                    split_words(text)
                ):

                    if len(chunk.split()) < 35:
                        continue

                    output.append({
                        "chunk_id": (
                            f"{source['source_id']}_"
                            f"{section_index:03}_"
                            f"{part_index:03}"
                        ),
                        "source_id": source["source_id"],
                        "source_title": source["title"],
                        "source_url": source["url"],
                        "section": title,
                        "topic": source["topic"],
                        "text": chunk,
                        "language": "en",
                        "provenance": (
                            "downloaded_html_unreviewed"
                        )
                    })

            print(
                f"{source['source_id']}: "
                f"{len(output) - start_count} chunks",
                flush=True
            )

        except (
            requests.RequestException,
            ValueError
        ) as exc:

            print(
                f"SKIPPED {source['source_id']}: "
                f"{exc}",
                flush=True
            )

    if not output:
        raise RuntimeError(
            "No pages fetched. "
            "Curated corpus is still available."
        )

    target = DATA / "full_text"

    target.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        target / "downloaded_chunks.json"
    )

    output_path.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf8"
    )

    print(
        "Wrote",
        output_path,
        len(output),
        "chunks",
        flush=True
    )

    print(
        "Sources:",
        dict(
            Counter(
                x["source_id"]
                for x in output
            )
        ),
        flush=True
    )

    print(
        "REVIEW BEFORE USE: remove citations, "
        "navigation, unrelated material.",
        flush=True
    )

    return output_path


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--timeout",
        type=int,
        default=20
    )

    args = parser.parse_args()

    fetch_sources(
        args.timeout
    )