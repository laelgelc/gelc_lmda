#!/usr/bin/env python3
"""
Validate Slice v0 run.json for structure, file existence, and SHA-256 hashes.

Usage:
  python scripts/validate_run.py --run-json artefacts/run.json --project-root .
"""

from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from typing import Dict, Any

REQUIRED_ARTIFACT_KEYS = [
    "vocabulary_csv",
    "counts_raw_npz",
    "counts_norm_npz",
    "factors_loadings_csv",
    "factors_scores_csv",
    "explained_variance_csv",
    "scree_plot_png",
    "log_file",
]

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def require(condition: bool, msg: str) -> None:
    if not condition:
        raise AssertionError(msg)

def validate_structure(doc: Dict[str, Any]) -> None:
    # Top-level keys
    for key in ["run", "environment", "config_snapshot", "inputs", "artifacts", "timings_sec"]:
        require(key in doc, f"Missing top-level key: {key}")

    # Run block
    run = doc["run"]
    for key in ["started_at", "finished_at", "status", "seed"]:
        require(key in run, f"Missing run.{key}")
    require(run["status"] in ("success", "failure"), "run.status must be 'success' or 'failure'")

    # Inputs
    inputs = doc["inputs"]
    for key in ["corpus_dir", "documents", "categories"]:
        require(key in inputs, f"Missing inputs.{key}")
    require(isinstance(inputs["documents"], int) and inputs["documents"] >= 0, "inputs.documents must be non-negative integer")
    require(isinstance(inputs["categories"], list), "inputs.categories must be a list")

    # Timings
    timings = doc["timings_sec"]
    for key in ["ingestion", "preprocessing", "features", "modeling", "export"]:
        require(key in timings, f"Missing timings_sec.{key}")
        require(isinstance(timings[key], (int, float)) and timings[key] >= 0, f"timings_sec.{key} must be non-negative number")

def validate_artifacts(doc: Dict[str, Any], project_root: str) -> None:
    artifacts = doc["artifacts"]
    for k in REQUIRED_ARTIFACT_KEYS:
        require(k in artifacts, f"Missing artifacts.{k}")
        entry = artifacts[k]
        for sub in ["path", "sha256"]:
            require(sub in entry, f"Missing artifacts.{k}.{sub}")
        abs_path = os.path.join(project_root, entry["path"])
        require(os.path.isfile(abs_path), f"Artifact not found: {abs_path}")
        actual = sha256_file(abs_path)
        require(
            actual.lower() == entry["sha256"].lower(),
            f"SHA-256 mismatch for {k}: expected {entry['sha256']}, got {actual}"
        )

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-json", required=True, help="Path to run.json")
    ap.add_argument("--project-root", default=".", help="Project root for resolving artifact paths")
    args = ap.parse_args()

    run_json_path = args.run_json
    if not os.path.isfile(run_json_path):
        print(f"ERROR: run.json not found: {run_json_path}", file=sys.stderr)
        return 1

    try:
        with open(run_json_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to read run.json: {e}", file=sys.stderr)
        return 1

    try:
        validate_structure(doc)
        validate_artifacts(doc, args.project_root)
    except AssertionError as e:
        print(f"ERROR: Validation failed: {e}", file=sys.stderr)
        return 2

    print("run.json validation passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
