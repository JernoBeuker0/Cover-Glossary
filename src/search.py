"""Standalone fuzzy search over the JSON glossary (no Django imports)."""
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "definitions.json"


def normalize(value):
    """Lowercase, remove accents and normalize punctuation/spacing."""
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^\w]+", " ", value).split())


def similarity(query, text):
    """Prioritize exact matches, beginnings of words, then typos."""
    text = normalize(text)
    if not text:
        return 0
    if query == text:
        return 1.0
    if text.startswith(query):
        return 0.95
    if any(word.startswith(query) for word in text.split()):
        return 0.87
    if query in text:
        return 0.83
    return max(
        [SequenceMatcher(None, query, text).ratio()]
        + [SequenceMatcher(None, query, word).ratio() * 0.92 for word in text.split()]
    )


def find_terms(query, data_file=DATA_FILE):
    """Return at most five matching words, with definitions and related terms."""
    query = normalize(query[:120])
    if not query:
        return []

    # With ~100 entries, re-reading JSON is cheap and enables live edits.
    with Path(data_file).open(encoding="utf-8") as file:
        entries = json.load(file)

    matches = []
    for word, info in entries.items():
        score = similarity(query, word)
        for alias in info.get("aliases", []):
            alias_score = similarity(query, alias)
            score = max(score, 0.99 if normalize(alias) == query else alias_score * 0.96)
        if score >= (0.85 if len(query) < 3 else 0.78):
            matches.append((score, word))

    matches.sort(key=lambda item: (-item[0], item[1].casefold()))
    chosen = [word for _, word in matches[:5]]
    related = set()

    # Fill empty spots with curated related terms from the strongest match.
    if matches:
        for word in entries[matches[0][1]].get("related", []):
            if len(chosen) == 5:
                break
            if word in entries and word not in chosen:
                chosen.append(word)
                related.add(word)

    return [
        {
            "word": word,
            "definition": entries[word]["definition"],
            "related": word in related,
        }
        for word in chosen
    ]
