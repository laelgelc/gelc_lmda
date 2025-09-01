Great—here’s a clear, minimal spec you and Junie can implement today for the PoC CLI and outputs.

CLI: lmda poc-preprocess Purpose: Ingest folder of .txt files, derive categories from subfolders, preprocess English with spaCy, filter to content-word lemmas, and write simple artifacts.

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

Deterministic identifiers
- doc_id: relative path from --input using forward slashes (e.g., blogs/blog_001.txt).
- category: first path segment (before first slash) under --input; if the file is directly under --input, category = uncategorized.

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

Validation checklist for tomorrow’s demo
- docs.csv has one row per input file and plausible counts.
- tokens.csv/parquet contains only POS in {NOUN, VERB, ADJ, ADV} and no stopwords when keep-stopwords=false.
- Category values match first-level subfolder names.
- Log shows file totals, category breakdown, and stage timings.
- run_poc.json present with config snapshot and artifact paths.

Nice-to-have if time permits
- Cache: If --cache-dir is set, store per-doc (lemma,pos,count) counters keyed by (relative_path, size, mtime). On match, reuse counts without reprocessing.
- Simple progress bar (only if logging is not enough).

Action Items
- Implement CLI parsing with the arguments above.
- Implement deterministic folder walk and metadata extraction.
- Integrate spaCy English pipeline; apply filters and compute counters.
- Write docs.csv, tokens.csv/parquet, optional errors.csv, logs, and run_poc.json.
- Test on the fixture corpus; confirm the validation checklist passes.
