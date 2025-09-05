# Data Handling (Slice v0)

## Encodings
- Default UTF-8; detect BOM; report decoding errors with file path and offset (if available).
- Provide an option to override encoding per-run.

## Corpus Ingestion
- Input folder:
    - Files: one text per file
    - Subfolders: treated as categories (metadata)
- Deterministic file ordering (e.g., lexicographic path order).

## Metadata
- Capture category from subfolder name.
- Record source file path and derived document ID.

## Privacy & Locality
- Local-only processing; do not send data over network.
- Redact or avoid PII in exports; warn if suspicious fields are found.

## Temporary Files
- Use local temp directories; clean up on success and on failure (best effort).
