# Python
from __future__ import annotations
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


def write_docs_csv(
        output_dir: Path,
        rows: List[Dict[str, object]],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "docs.csv"
    fields = [
        "doc_id",
        "category",
        "path",
        "n_chars",
        "n_sentences",
        "n_tokens_raw",
        "n_tokens_content",
        "n_types_content",
        "encoding_used",
        "warnings",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    logging.info("Wrote %s (%d rows)", path, len(rows))
    return path


def write_tokens_csv(
        output_dir: Path,
        rows: List[Dict[str, object]],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "tokens.csv"
    fields = ["doc_id", "lemma", "pos", "count"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    logging.info("Wrote %s (%d rows)", path, len(rows))
    return path


def write_errors_csv(output_dir: Path, rows: List[Dict[str, object]]) -> Optional[Path]:
    if not rows:
        return None
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "errors.csv"
    fields = ["path", "stage", "error_type", "message"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    logging.info("Wrote %s (%d rows)", path, len(rows))
    return path


def write_run_poc_json(
        output_dir: Path,
        environment: Dict[str, object],
        config_snapshot: Dict[str, object],
        inputs: Dict[str, object],
        artifacts: Dict[str, Dict[str, str]],
        timings_sec: Dict[str, float],
) -> Path:
    path = output_dir / "run_poc.json"
    doc = {
        "run": {
            "started_at": environment.get("started_at"),
            "finished_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "status": "success",
            "seed": None,
        },
        "environment": environment,
        "config_snapshot": config_snapshot,
        "inputs": inputs,
        "artifacts": artifacts,
        "timings_sec": timings_sec,
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    logging.info("Wrote %s", path)
    return path
