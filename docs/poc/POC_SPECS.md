# PoC Specs

CLI: lmda poc-preprocess

Purpose: Ingest folder of .txt files, derive categories from subfolders, preprocess English with spaCy, filter to content-word lemmas, and write simple artefacts.

Arguments
- --input PATH (required)
    - Directory containing .txt files; subfolders are categories.

- --output PATH (required)
    - Directory to write artifacts (created if missing).

- --encoding STR (default: utf-8)
    - File decoding; BOM handled automatically when utf-8.

- --include-patterns GLOB[,GLOB...] (default: *.txt)
    - Comma-separated glob(s) to include relative to --input.

- --exclude-patterns GLOB[,GLOB...] (default: none)
    - Comma-separated glob(s) to exclude.

- --keep-stopwords BOOL (default: false)
    - false removes spaCy stopwords from content-word counts.

- --content-pos LIST (default: NOUN,VERB,ADJ,ADV)
    - Comma-separated POS tags to keep as “content words”.

- --lowercase BOOL (default: true)
    - Lowercase text and lemmas before counting.

- --batch-size INT (default: 64)
    - Batch size for nlp.pipe.

- --dry-run BOOL (default: false)
    - List what would be processed; do not write artifacts.

- --log-level STR (default: INFO)
    - One of: DEBUG, INFO, WARN, ERROR.

- --cache-dir PATH (optional)
    - If provided, store per-doc preprocessed counters; reuse if mtime/size unchanged.

- --fail-on-decode-error BOOL (default: false)
    - If true, exit non-zero on any decoding failure; otherwise log and skip.

Exit codes
- 0 success
- 1 invalid arguments
- 2 decoding errors with --fail-on-decode-error
- 3 preprocessing errors (spaCy/model not available, etc.)

Micro-Usability (NFR-3-lite)
- Enhanced --help: include brief examples and show defaults for all options.
- Friendly errors with remediation:
    - Missing spaCy/model → instruct how to enable them in your environment.
    - Decoding errors → hint to try --encoding or --fail-on-decode-error=false.
- Deterministic summaries:
    - After ingestion: total files scanned/processed and category distribution.
    - After preprocessing: per-category token stats; empty/short docs count.
- Dry-run mode:
    - --dry-run prints planned doc_ids and category counts; does not write artifacts.
- Final success line:
    - “Processed <docs> docs across <categories> in <sec>s. Artifacts at <output>. See logs/poc_run.log.”

Preflight and Environment
- At startup, check:
    - spaCy import succeeds.
    - en_core_web_sm loads; print model name/version.
- If checks fail:
    - Exit code 3 with a clear message to enable the required packages in your environment.
- Log detected Python and spaCy versions in run_poc.json.environment and in logs/poc_run.log.

Cross-Platform Compatibility (NFR-7-v0)
- Use pathlib for all paths and globs; avoid OS-specific separators. Normalize doc_id via Path(relative_path).as_posix().
- Do not rely on shell-only features; provide commands/examples that work in common shells. Prefer Python utilities for setup tasks.
- Handle encodings/newlines robustly; do not assume LF. Default to UTF-8; retry with "utf-8-sig" on UnicodeDecodeError per FR-2-v0 policy.
- Keep spaCy processing single-process (n_process=1) for determinism and Windows compatibility.
- Avoid symlinks/xattrs/chmod-specific logic.

Python Version Compatibility (NFR-8-v0)
- Target runtime: Python 3.12.11.
- Preflight prints python_version and spacy/model versions; record them in run_poc.json.environment.
- Dependencies limited to those required for FR-1..FR-7-v0 to keep the PoC lean and compatible.

Windows notes (PoC)
- Use Python-based helpers for setup (e.g., creating the fixture corpus) to avoid shell incompatibilities.
- Example invocation (PowerShell):
  lmda poc-preprocess --input data/fixture_corpus --output artefacts_poc --encoding utf-8

Deterministic identifiers
- doc_id: relative path from --input using forward slashes (e.g., blogs/blog_001.txt).
- category: first path segment (before first slash) under --input; if the file is directly under --input, category = uncategorized.

Source Code Isolation (PoC)
- Goal: Prevent PoC code from mixing with Slice v0 implementation while enabling easy demo and later migration.
- Layout:
    - poc/
        - src/lmda_poc/{__init__.py, cli.py, ingestion.py, preprocessing.py, io_artifacts.py, logging_setup.py}
        - tests/{test_ingestion.py, test_preprocessing.py, test_cli_integration.py}
        - config.poc.yaml (PoC defaults)
        - README_POC.md (PoC usage)
    - artefacts_poc/ (PoC outputs; ignored by VCS)
- Namespacing:
    - Use the lmda_poc package name; do not import from future v0 modules.
- CLI separation:
    - Expose a PoC-only entrypoint (e.g., lmda poc-preprocess or python -m lmda_poc.cli).
- Configs and artifacts:
    - PoC reads poc/config.poc.yaml (not Slice v0 configs) and writes only to artefacts_poc/.
- Tests and CI:
    - PoC tests live under poc/tests/ and are run in a separate “PoC smoke test” job.
    - The smoke test uses the fixture corpus and asserts docs.csv and tokens table exist.
- Branching:
    - Do PoC work on poc/* branches; keep separate from feature/* branches for Slice v0.
- Migration (later):
    - Copy (not import) hardened modules into Slice v0 packages; keep PoC intact until parity is confirmed, then archive/remove in a cleanup PR.

Artifacts (all under --output)
1. docs.csv

- Purpose: One row per document with metadata and summary stats.
- Columns:
    - doc_id (string): deterministic relative path identifier.
    - category (string): derived from first-level subfolder or “uncategorized”.
    - path (string): absolute or project-relative path to source file.
    - n_chars (int): length of raw text (characters).
    - n_sentences (int): sentence count (spaCy sents).
    - n_tokens_raw (int): tokens considered after basic normalization (e.g., token.is_alpha if you adopt that rule).
    - n_tokens_content (int): tokens counted after content POS filter and stopword policy.
    - n_types_content (int): unique (lemma, pos) types after filtering.
    - encoding_used (string): final encoding used to decode file.
    - warnings (string): optional note (e.g., “empty_doc”, “short_doc”, “skipped_nonalpha_tokens”); empty if none.

1. tokens.csv or tokens.parquet

- Purpose: Aggregated per-document content-word lemma counts.
- Columns:
    - doc_id (string)
    - lemma (string): lowercase if --lowercase=true.
    - pos (string): e.g., NOUN, VERB, ADJ, ADV (must be in --content-pos).
    - count (int): occurrences within the document after filtering.

- Notes:
    - Only include rows where count > 0.
    - Exclude stopwords when --keep-stopwords=false.
    - Do not include non-alpha tokens if you apply token.is_alpha (recommended for PoC).

1. errors.csv (only if any errors occurred)

- Purpose: Record decoding or processing issues and allow resumable runs.
- Columns:
    - path (string)
    - stage (string): ingestion|preprocessing
    - error_type (string): UnicodeDecodeError|EmptyDoc|SpaCyError|Other
    - message (string): short, actionable message

- If no errors, do not write this file.

1. logs/poc_run.log

- INFO summary per stage: file counts, category distribution, timings.
- WARN for recoverable issues (empty docs).
- ERROR for unrecoverable issues (only if aborting).

1. run_poc.json

- Purpose: Minimal provenance and quick inspection.
- Structure:
    - run: { started_at, finished_at, status, seed (null or int) }
    - environment: { python, packages: { spacy, pandas, numpy } }
    - config_snapshot:
        - input: { corpus_dir, encoding, include_patterns, exclude_patterns }
        - preprocessing: { language: "en", keep_stopwords, content_pos, lowercase, batch_size }
        - output: { output_dir }

    - inputs: { documents_scanned, documents_processed, categories: [..] }
    - artifacts: { docs_csv: { path }, tokens_table: { path }, errors_csv: { path or null }, log_file: { path } }
    - timings_sec: { ingestion, preprocessing, export }

Behavioral rules and defaults
- Ordering: Always process files in lexicographic order of relative path.
- Content POS: Default {NOUN, VERB, ADJ, ADV}. Make this a strict include filter.
- Normalization: Apply lowercase if --lowercase=true; filter token.is_alpha to avoid punctuation/numbers noise in PoC.
- Stopwords: Use spaCy built-in stopwords (language=en). If keep-stopwords=false, exclude those tokens from content counts.
- Sentence boundaries: Use spaCy sentencizer; if missing, add sentencizer component to pipeline.
- Determinism: Use n_process=1; do not rely on nondeterministic threading. Log the exact spaCy model name/version.

Suggested CLI help text snippets
- Example usage:
    - lmda poc-preprocess --input data/fixture_corpus --output artefacts_poc

- English-only note:
    - PoC supports English only. If the model is unavailable, the command will exit with guidance to enable it in your environment.

Validation checklist for the demo
- docs.csv has one row per input file and plausible counts.
- tokens.csv/parquet contains only POS in {NOUN, VERB, ADJ, ADV} and no stopwords when keep-stopwords=false.
- Category values match first-level subfolder names.
- Log shows:
    - totals by stage (ingestion/preprocessing), category breakdown, timings.
    - a final success line summarizing docs, categories, duration, and output path.
- run_poc.json present with config snapshot and artifact paths.
- Preflight reports spaCy and model versions; English-only confirmed.

Validation checklist additions (NFR-7-v0 and NFR-8-v0)
- Paths are constructed with pathlib; doc_id values are forward-slash normalized (as_posix).
- PoC runs cleanly on Windows and Linux with Python 3.12.11 (smoke test on fixture corpus).
- run_poc.json includes environment.python and packages.spacy entries with versions.

Validation checklist additions (Isolation)
- PoC package imports are limited to lmda_poc and allowed third-party libs (no cross-imports from v0).
- All PoC outputs are written under artefacts_poc/.
- CI runs a separate PoC smoke test that does not affect Slice v0 jobs.

Definition of Done (PoC)
- CLI runs end-to-end:
  - lmda poc-preprocess --input data/fixture_corpus --output artefacts_poc --encoding utf-8 --keep-stopwords false
- Outputs exist and are populated:
  - artefacts_poc/docs.csv, artefacts_poc/tokens.(csv|parquet), artefacts_poc/logs/poc_run.log, artefacts_poc/run_poc.json
- Determinism and rules:
  - doc_id = relative path (as_posix); category = first-level subfolder; n_process=1
  - English-only with spaCy en_core_web_sm; POS filter {NOUN, VERB, ADJ, ADV}
  - Stopword policy applied per flag; lowercase and is_alpha normalization
- Micro-usability (NFR-3-lite):
  - Preflight prints Python/spaCy/model versions; friendly errors; final success summary line
- Encodings:
  - UTF-8 default, BOM handled; decoding errors recorded or fail per flag
- Cross-platform and version:
  - Paths via pathlib; runs on Python 3.12.11; smoke test OK on Windows/Linux

Runbook (Demo Flow)
```
# Ensure fixture corpus
bash scripts/create_fixture_corpus.sh # or run the equivalent steps on your OS
# Run PoC
lmda poc-preprocess --input data/fixture_corpus --output artefacts_poc --encoding utf-8 --keep-stopwords false
# Inspect outputs
head -n 5 artefacts_poc/docs.csv head -n 5 artefacts_poc/tokens.csv # or open parquet if used tail -n 20 artefacts_poc/logs/poc_run.log
# Check run_poc.json has environment (python, spacy), config snapshot, and artifact paths
``` 

Mini Task Breakdown and Evidence
- Task 1: Ingestion & Metadata
  - Deliverables: docs.csv (doc_id, category, path, n_chars)
  - Evidence: log summary by category; sample rows in PR
- Task 2: Preprocessing (spaCy EN, lemmas, POS)
  - Deliverables: tokens table (doc_id, lemma, pos, count)
  - Evidence: log model/version; sample rows show POS filter and stopword policy
- Task 3: CLI & Usability
  - Deliverables: argparse --help; poc_run.log with stage timings; final success line
  - Evidence: paste --help in PR; tail of logs; example missing-model message
- Task 4: Provenance & Errors
  - Deliverables: run_poc.json; errors.csv when applicable
  - Evidence: show run_poc.json structure; one simulated decode error entry (optional)
- Task 5: Isolation & Cross-Platform
  - Deliverables: PoC writes only to artefacts_poc/; paths via pathlib; doc_id normalized
  - Evidence: artefacts_poc/ listing; code note that doc_id uses as_posix()

Nice-to-have if time permits
- Cache: If --cache-dir is set, store per-doc (lemma,pos,count) counters keyed by (relative_path, size, mtime). On match, reuse counts without reprocessing.
- Simple progress bar (only if logging is not enough).

Action Items
- Implement CLI parsing with the arguments above.
- Implement deterministic folder walk and metadata extraction.
- Integrate spaCy English pipeline; apply filters and compute counters.
- Write docs.csv, tokens.csv/parquet, optional errors.csv, logs, and run_poc.json.
- Test on the fixture corpus; confirm the validation checklist passes.
