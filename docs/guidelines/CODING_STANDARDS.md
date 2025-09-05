# Coding Standards (Slice v0)

## Environment
- Python 3.12.11
- Use condavenv environment (no other package managers).
- All randomness controlled via a single seed in config.

## Style
- PEP 8, type hints, and docstrings (Google or NumPy style).
- Keep functions small and composable; one responsibility each.
- Prefer pure functions and explicit dependencies via parameters.

## Logging
- Use structured, human-readable logs with context:
    - stage, doc_id (if applicable), action, counts, duration
- Log at INFO for pipeline steps; DEBUG for details; WARN for recoverable issues; ERROR for unrecoverable.

## Error Handling
- Fail fast with actionable messages that suggest remediation.
- Wrap file/IO with clear context (path, encoding, line if known).
- Avoid silent fallbacks; warn explicitly.

## Configuration
- All behavior controlled via a config file and CLI flags.
- No magic constants in code; document defaults in CLI help and README.

## Data Structures & Performance
- Prefer sparse matrices where applicable.
- Cache preprocessing and intermediate artifacts; verify cache keys include config and seed.
- Keep memory proportional to K and number of docs; avoid materializing unnecessary intermediates.

## Testing Contracts
- Unit tests for critical functions.
- Integration test for end-to-end pipeline on a toy corpus.
- Determinism tests: same inputs → identical outputs (hash compare).
