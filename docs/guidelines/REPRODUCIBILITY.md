# Reproducibility (Slice v0)

## Seeds
- Single global random seed specified in config and logged at start.
- Propagate to all stochastic components (factor extraction/rotation if applicable).

## Run Provenance
- Save run.json with:
    - Command and config snapshot (embedded or path + hash)
    - Dependency versions
    - Input corpus path and file count
    - Artifacts with filenames and content hashes
    - Start/end timestamps and durations
    - Global seed and any derived seeds

## Frozen Vocabulary
- Save vocabulary with ranks/scores and selection metadata (see spec).
- Reuse across runs by supplying the saved vocabulary path.

## Hashing
- Compute SHA-256 for CSV/JSON artifacts; store in run.json.
- Determinism test compares hashes across repeated runs.
