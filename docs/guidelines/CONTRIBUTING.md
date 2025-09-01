# Contributing Guide (Slice v0)

## Scope Discipline
- Only implement items in Slice v0 (FR-1..FR-26-v0 and NFR-1..NFR-9-v0).
- Anything else → open an issue and label "Backlog".

## Branching & Commits
- Branch naming: feature/<short-scope>, fix/<short-scope>, docs/<short-scope>, chore/<short-scope>
- Conventional commits:
    - feat: add ingestion subfolder-category mapping
    - fix: handle BOM decoding
    - docs: add CLI examples
    - chore: bump dependency pins

## Pull Requests
- Keep PRs small (<400 lines) and focused on a single stage (ingestion, preprocessing, features, modeling, export).
- PR description must include:
    - Linked FR/NFR v0 items
    - Before/after behavior (if applicable)
    - Acceptance checklist (copy relevant items from checklists)
    - Test plan and results (fixture run outputs)
- Label PRs with: area/ingestion, area/preprocessing, area/features, area/modeling, area/export, docs

## Review SLA & Process
- First review response within 24h.
- Reviews must split findings into:
    - Blocking: must fix before merge
    - Non-blocking: may follow-up
- Request a 30-minute pairing if blocked for >1 day.

## Coding & Testing
- Follow Coding Standards and Testing guidelines.
- Ensure determinism (fixed seeds) and documented tie-breaking.
- Confirm all new artifacts registered in run.json.

## CI/Checks
- Lint, unit tests, integration tests must pass locally and in CI.
- PRs must attach the hash comparison for determinism re-run (fixture corpus).

## Releases
- Tag milestones for Slice v0 as v0.x.y.
- Maintain concise release notes listing commands and artifacts produced.