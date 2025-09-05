# Project Orchestrator Guide (Slice v0)

## Purpose
- Keep delivery on-scope, reproducible, and predictable.
- Provide a single point of coordination for planning, acceptance, and risk handling.

## Primary Objectives
- Scope discipline: enforce Slice v0 only; move extras to Backlog.
- Reproducibility: every run uses a config and produces a run.json with hashes.
- Flow: small tasks, fast reviews, weekly demos, visible progress.
- Risk management: surface blockers early; agree mitigations.

## Responsibilities
- Plan: set weekly goals; break work into small, testable tasks.
- Track: maintain a simple Kanban and status notes.
- Gatekeep: apply acceptance checklists before merging.
- Evidence: require run.json + validator PASS on PRs that touch pipeline outputs.
- Decide: document decisions (K/N defaults, tie-breaking, paths) and announce changes.
- Demo: run the fixture demo weekly and share artifacts.

## Scope Rules (Slice v0)
- Only items in FR-1..FR-26-v0 and NFR-1..NFR-9-v0.
- Anything beyond → label “Backlog” with rationale and optional due window.

## Cadence
- Daily (async): 3-line standup (Done, Next, Risks).
- Weekly (15–30 mins): demo with the fixture corpus; agree next goals.

## Core Artifacts the Orchestrator Owns
- Weekly plan (goals, tasks, owners, evidence required).
- Daily standup notes.
- Decision log (1–3 lines per decision).
- Acceptance checklists for PRs.
- Demo notes and release tag summaries.

## Evidence Standards (must be referenced in PRs)
- Config used (path or diff from config.example.yaml).
- run.json with:
  - Config snapshot, K, N, seed
  - Artifact paths + SHA-256 hashes
  - Timings per stage
- Validator PASS:
  - Command: python scripts/validate_run.py --run-json artefacts/run.json --project-root .
- Short logs snippet showing stages and summary counts.

## Lightweight Workflows

1) Weekly Planning (Orchestrator)
- Define 3–5 measurable goals.
- Create small tasks (≤1–2 days) with Definition of Done (DoD) and evidence.
- Assign owners and due dates.

Template — Weekly Plan
```
Goals:
- <measurable goal 1>
- <measurable goal 2>
- <measurable goal 3>

Tasks:
- — Owner: — Due: — Evidence: run.json + validator PASS

Risks/Mitigations:
- →

Demo plan:
- Command: lmda run --config config.example.yaml --input data/fixture_corpus --output artefacts/
- Evidence to show: artefacts/run.json, validator PASS, CSV heads, scree plot
``` 

2) Task Ticket (Creation)
```
Title: — Scope: Slice v0 (refs FR/NFR) DoD (acceptance):
- 

Inputs:
- Config:
- Data:

Outputs/Evidence:
- 
- run.json + validator PASS

Owner: Due:
``` 

3) PR Acceptance (Reviewer)
```
Scope: ✅/❌ (Slice v0 only)
Determinism: ✅/❌ (seed fixed; repeat run hashes identical)
Artifacts: ✅/❌ (run.json complete; all files + SHA-256 present)
Checklists: ✅/❌ (component checklists satisfied)
Performance note (K=1000):
Blocking:
- 

Non-blocking:
- 

Re-test:
- lmda run --config config.example.yaml --input data/fixture_corpus --output artefacts/
- python scripts/validate_run.py --run-json artefacts/run.json --project-root .
``` 

Decision Log (kept as a simple running list)
```
text YYYY-MM-DD — Decision — Rationale — Impacted docs/config
``` 

## Weekly Demo Checklist
- Fixture corpus exists and command matches plan.
- run.json passes validator.
- Show heads of vocabulary/loadings/scores; show scree plot.
- Note timings and any regressions.
- Capture follow-ups as tasks.

## Metrics to Watch (lightweight)
- PR cycle time (open → merge).
- Reproducibility: % PRs with validator PASS on first review.
- Performance drift: change in stage timings on fixture corpus.

## Backlog Handling
- New ideas → create issue labelled “Backlog”.
- Include a short value statement and dependency notes.
- Revisit during milestone planning, not during v0 execution.

## Handover (if the role rotates)
- Share current Weekly Plan, Decision Log, and open risks.
- Confirm fixture demo runs and validator PASS under the new owner’s environment.

## Contact Model
- Orchestrator posts tasks and acceptance criteria.
- Implementers respond with PRs + evidence.
- Reviewer (can be Orchestrator) uses checklists and validator output to accept.
