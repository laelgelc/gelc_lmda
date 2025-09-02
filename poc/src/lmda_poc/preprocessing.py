# Python
from __future__ import annotations
import logging
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import spacy  # runtime dependency for PoC


@dataclass(frozen=True)
class TokenCount:
    lemma: str
    pos: str
    count: int


def preflight_spacy(model_name: str = "en_core_web_sm") -> Tuple[str, str]:
    # Returns (spacy_version, model_name_loaded)
    try:
        # Prefer package import + .load() for PyInstaller-friendly behavior
        import en_core_web_sm  # type: ignore
        _ = en_core_web_sm.load()
        loaded = "en_core_web_sm"
    except Exception as e:
        logging.error("Failed to load spaCy model via package import: %s", e)
        # Fallback to spacy.load (works in dev environments)
        _ = spacy.load(model_name, disable=[])
        loaded = model_name
    spacy_version = spacy.__version__
    logging.info("spaCy preflight OK: spacy=%s, model=%s", spacy_version, loaded)
    return spacy_version, loaded

def build_pipeline(model_name: str = "en_core_web_sm", add_sentencizer: bool = True):
    try:
        import en_core_web_sm  # type: ignore
        nlp = en_core_web_sm.load()
    except Exception:
        nlp = spacy.load(model_name, disable=[])
    if add_sentencizer and "senter" not in nlp.pipe_names and "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")
    return nlp


def content_counts_for_doc(
        nlp,
        text: str,
        content_pos: List[str],
        lowercase: bool = True,
        keep_stopwords: bool = False,
) -> Tuple[int, int, int, Dict[Tuple[str, str], int], int]:
    """
    Returns:
      n_sentences, n_tokens_raw, n_tokens_content, counts[(lemma,pos)], n_types_content
    """
    doc = nlp(text)
    n_sentences = sum(1 for _ in doc.sents)
    tokens = [t for t in doc if t.is_alpha]
    n_tokens_raw = len(tokens)

    def norm_lemma(t):
        return (t.lemma_ or t.text).lower() if lowercase else (t.lemma_ or t.text)

    kept = []
    for t in tokens:
        if t.pos_ not in content_pos:
            continue
        if not keep_stopwords and t.is_stop:
            continue
        kept.append((norm_lemma(t), t.pos_))

    counter = Counter(kept)
    n_tokens_content = sum(counter.values())
    n_types_content = len(counter)
    return n_sentences, n_tokens_raw, n_tokens_content, dict(counter), n_types_content
