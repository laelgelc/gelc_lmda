# Python
from __future__ import annotations
import argparse
import logging
import platform
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def _str2bool(v: str) -> bool:
    if isinstance(v, bool):
        return v
    val = v.strip().lower()
    if val in {"1", "true", "yes", "y", "on"}:
        return True
    if val in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected boolean value, got: {v}")

from .logging_setup import setup_logging
from .ingestion import ingest_corpus
from .preprocessing import build_pipeline, preflight_spacy, content_counts_for_doc
from .io_artifacts import (
    write_docs_csv,
    write_tokens_csv,
    write_errors_csv,
    write_run_poc_json,
)


def parse_args(argv: List[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        prog="lmda poc-preprocess",
        description="PoC: Ingest .txt corpus and preprocess English with spaCy to produce docs and tokens tables.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=(
            "Examples:\n"
            "  lmda poc-preprocess --input data/fixture_corpus --output artefacts_poc --encoding utf-8\n"
            "  python -m lmda_poc.cli --input data/fixture_corpus --output artefacts_poc\n"
        ),
    )
    ap.add_argument("--input", required=True, help="Input directory (corpus root)")
    ap.add_argument("--output", required=True, help="Output directory for PoC artifacts")
    ap.add_argument("--encoding", default="utf-8", help="Default file encoding (default: utf-8)")
    ap.add_argument("--include-patterns", default="*.txt", help="Comma-separated glob patterns to include")
    ap.add_argument("--exclude-patterns", default="", help="Comma-separated glob patterns to exclude")
    ap.add_argument("--keep-stopwords", type=_str2bool, default=False, help="Keep stopwords (true/false)")
    ap.add_argument("--content-pos", default="NOUN,VERB,ADJ,ADV", help="Comma-separated POS tags to keep as content words")
    ap.add_argument("--lowercase", type=_str2bool, default=True, help="Lowercase lemmas (true/false)")
    ap.add_argument("--batch-size", type=int, default=64, help="spaCy nlp.pipe batch size (default: 64)")
    ap.add_argument("--dry-run", action="store_true", help="List what would be processed; do not write artifacts")
    ap.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARN, ERROR)")
    ap.add_argument("--fail-on-decode-error", action="store_true", help="Exit non-zero on decoding error")
    return ap.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    log_path = setup_logging(output_dir, level=args.log_level)

    started_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    logging.info("PoC run started at %s", started_at)

    include_patterns = [p.strip() for p in args.include_patterns.split(",") if p.strip()]
    exclude_patterns = [p.strip() for p in args.exclude_patterns.split(",") if p.strip()]
    content_pos = [p.strip().upper() for p in args.content_pos.split(",") if p.strip()]

    # Preflight: spaCy + model
    try:
        spacy_version, model_name = preflight_spacy("en_core_web_sm")
    except Exception as e:
        logging.error("Preflight failed: %s", e)
        print("ERROR: spaCy model 'en_core_web_sm' not available. Please enable it in your environment.", file=sys.stderr)
        return 3

    # Ingestion
    t0 = time.perf_counter()
    try:
        docs, errors = ingest_corpus(
            input_dir=input_dir,
            encoding=args.encoding,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            fail_on_decode_error=args.fail_on_decode_error,
        )
    except UnicodeDecodeError as e:
        logging.error("Decoding error with --fail-on-decode-error: %s", e)
        print("ERROR: Decoding failed. Try --encoding utf-8 or --fail-on-decode-error=false to skip bad files.", file=sys.stderr)
        return 2
    t_ing = time.perf_counter() - t0
    if args.dry_run:
        for d in docs[:10]:
            logging.info("DRY-RUN doc: %s (%s)", d.doc_id, d.category)
        cat_counts = defaultdict(int)
        for d in docs:
            cat_counts[d.category] += 1
        for cat in sorted(cat_counts):
            logging.info("DRY-RUN category: %s = %d", cat, cat_counts[cat])
        logging.info("DRY-RUN: scanned=%d processed=%d errors=%d", len(docs) + len(errors), len(docs), len(errors))
        print("Dry run complete. No artifacts written.")
        return 0

    # Preprocessing
    t1 = time.perf_counter()
    nlp = build_pipeline("en_core_web_sm", add_sentencizer=True)

    docs_rows: List[Dict[str, object]] = []
    tokens_rows: List[Dict[str, object]] = []

    for d in docs:
        n_sentences, n_tokens_raw, n_tokens_content, counts, n_types_content = content_counts_for_doc(
            nlp=nlp,
            text=d.text,
            content_pos=content_pos,
            lowercase=args.lowercase,
            keep_stopwords=args.keep_stopwords,
        )
        docs_rows.append(
            {
                "doc_id": d.doc_id,
                "category": d.category,
                "path": str(d.path),
                "n_chars": d.n_chars,
                "n_sentences": n_sentences,
                "n_tokens_raw": n_tokens_raw,
                "n_tokens_content": n_tokens_content,
                "n_types_content": n_types_content,
                "encoding_used": d.encoding_used,
                "warnings": "",
            }
        )
        for (lemma, pos), count in counts.items():
            tokens_rows.append({"doc_id": d.doc_id, "lemma": lemma, "pos": pos, "count": int(count)})

    t_pre = time.perf_counter() - t1

    # Artifacts
    docs_csv = write_docs_csv(output_dir, docs_rows)
    tokens_csv = write_tokens_csv(output_dir, tokens_rows)
    errors_csv = write_errors_csv(output_dir, [
        {"path": str(p), "stage": stg, "error_type": "UnicodeDecodeError", "message": msg}
        for (p, stg, msg) in [(e[0], e[1], e[2]) if len(e) == 3 else (e[0], "ingestion", str(e[1])) for e in errors]
    ])

    # Environment + Provenance
    environment = {
        "started_at": started_at,
        "python": platform.python_version(),
        "packages": {
            "spacy": spacy_version,
            "model": model_name,
        },
    }
    config_snapshot = {
        "input": {
            "corpus_dir": str(input_dir),
            "encoding": args.encoding,
            "include_patterns": include_patterns,
            "exclude_patterns": exclude_patterns,
        },
        "preprocessing": {
            "language": "en",
            "keep_stopwords": bool(args.keep_stopwords),
            "content_pos": content_pos,
            "lowercase": bool(args.lowercase),
            "batch_size": int(args.batch_size),
        },
        "output": {"output_dir": str(output_dir)},
    }
    inputs = {
        "documents_scanned": len(docs) + len(errors),
        "documents_processed": len(docs),
        "categories": sorted({d.category for d in docs}),
    }
    artifacts = {
        "docs_csv": {"path": str(docs_csv)},
        "tokens_table": {"path": str(tokens_csv)},
        "errors_csv": {"path": str(errors_csv) if errors_csv else None},
        "log_file": {"path": str(log_path)},
    }
    timings_sec = {
        "ingestion": round(t_ing, 3),
        "preprocessing": round(t_pre, 3),
        "export": 0.0,
    }
    run_json = write_run_poc_json(output_dir, environment, config_snapshot, inputs, artifacts, timings_sec)

    total = timings_sec["ingestion"] + timings_sec["preprocessing"]
    # Final Action Items in log
    logging.info("Action Items:\n- Review %s\n- Inspect %s and %s\n- Check log at %s",
                 run_json, docs_csv, tokens_csv, log_path)
    print(
        f"Processed {len(docs)} docs across {len(inputs['categories'])} categories in {total:.2f}s. "
        f"Artifacts at {output_dir}. See logs/poc_run.log."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
