# Testing Guide (Slice v0)

## Test Levels
- Unit: core logic (tokenization/lemmatization filter, keyword scoring, tie-breaking, normalization).
- Integration: full pipeline run on toy corpus.
- CLI: argument parsing and run exit codes.

## Fixtures
- Tiny fixture corpus (few docs across 2–3 categories) with known expected:
    - Token counts, per-thousand normalization
    - Top-K keywords with deterministic ties
    - Factor extraction with fixed seed (N factors) and stable scree

## Determinism
- Re-run the same config and inputs → identical outputs:
    - Hash CSV/JSON artifacts and compare
    - Store hashes in run.json

## Performance
- Smoke test to ensure end-to-end run completes within a small local budget on the fixture corpus.

## How to Run
- One command to run all tests (document in CLI guide or Makefile).
- CI replicates local runs and publishes artifacts from the fixture run.
