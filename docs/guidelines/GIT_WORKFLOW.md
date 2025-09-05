# Git Workflow (Slice v0)

## Strategy
- Trunk-based with short-lived branches.
- Frequent small merges to main after review and passing checks.

## Branches
- feature/<scope>, fix/<scope>, docs/<scope>, chore/<scope>

## Pull Requests
- Link to FR/NFR v0 items.
- Include acceptance checklist and evidence (logs, hashes).

## Tags & Releases
- Tag v0.x.y for Slice v0 milestones.
- Release notes: commands used, artifacts produced, notable fixes.

## Backporting
- Not applicable for v0. Keep main green; revert quickly if needed.
