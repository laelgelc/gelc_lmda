# CI Validation (Slice v0)

## Goals
- Ensure shape/structure of run.json is correct
- Ensure artifacts listed in run.json exist and match recorded SHA-256 hashes

## Steps (example)
1) Create/activate the environment (condavenv), install project deps.
2) Run the pipeline on the fixture corpus using config.example.yaml (or a CI-specific config).
3) Ensure artefacts/run.json is produced.
4) Validate run.json:
    - Structure and field presence
    - File existence and SHA-256 hash matches

## Commands (illustrative)
# 1) Run the pipeline (adjust to your CLI)
lmda run --config config.example.yaml --input data/fixture_corpus --output artefacts/

# 2) Validate run.json
python scripts/validate_run.py --run-json artefacts/run.json --project-root .

## Failing the build
- The validator exits non-zero if structure or hashes don’t match; CI should fail the job.

## Tips
- Keep the fixture corpus small to ensure fast CI runs.
- Store run.json and key artifacts as CI artifacts for inspection on failures.