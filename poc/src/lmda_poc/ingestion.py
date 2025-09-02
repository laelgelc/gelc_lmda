# Python
from __future__ import annotations
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class DocRecord:
    doc_id: str
    category: str
    path: Path
    text: str
    encoding_used: str
    n_chars: int


def _derive_category(rel_path: Path) -> str:
    parts = rel_path.parts
    return parts[0] if len(parts) > 1 else "uncategorized"


def list_candidate_files(
        input_dir: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
) -> List[Path]:
    include_patterns = include_patterns or ["*.txt"]
    exclude_patterns = exclude_patterns or []
    files: set[Path] = set()
    for pat in include_patterns:
        files.update(input_dir.rglob(pat))
    for pat in exclude_patterns:
        for p in list(files):
            if p.match(pat):
                files.discard(p)
    kept = [p for p in files if p.is_file()]
    kept.sort(key=lambda p: p.relative_to(input_dir).as_posix())
    logging.info("Discovered %d candidate files", len(kept))
    return kept


def read_text_with_encoding(path: Path, encoding: str = "utf-8") -> Tuple[str, str]:
    # First attempt: provided encoding (default utf-8)
    try:
        text = path.read_text(encoding=encoding, errors="strict")
        return text, encoding
    except UnicodeDecodeError:
        pass
    # Retry UTF-8 with BOM handling
    try:
        text = path.read_text(encoding="utf-8-sig", errors="strict")
        return text, "utf-8-sig"
    except UnicodeDecodeError as e:
        logging.error("Decoding failed for %s: %s", path, e)
        raise


def ingest_corpus(
        input_dir: Path,
        encoding: str = "utf-8",
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        fail_on_decode_error: bool = False,
) -> Tuple[List[DocRecord], List[Tuple[Path, str, str]]]:
    paths = list_candidate_files(input_dir, include_patterns, exclude_patterns)
    docs: List[DocRecord] = []
    errors: List[Tuple[Path, str, str]] = []

    for path in paths:
        rel = path.relative_to(input_dir)
        doc_id = rel.as_posix()
        category = _derive_category(rel)
        try:
            text, enc_used = read_text_with_encoding(path, encoding)
        except UnicodeDecodeError as e:
            msg = f"UnicodeDecodeError: {e}"
            errors.append((path, "ingestion", msg))
            if fail_on_decode_error:
                raise
            else:
                continue
        record = DocRecord(
            doc_id=doc_id,
            category=category,
            path=path,
            text=text,
            encoding_used=enc_used,
            n_chars=len(text),
        )
        docs.append(record)

    logging.info(
        "Ingestion summary: scanned=%d, processed=%d, errors=%d",
        len(paths),
        len(docs),
        len(errors),
    )
    return docs, errors
