# Determinism and Tie-Breaking (Slice v0)

## Ranking Strategy (Top-K)
- Sort by:
    1) score (descending)
    2) lemma (ascending, case-normalized)
    3) POS (ascending; if included)
- Document this policy in exports (metadata column: selection_method).

## Floating Point Stability
- Use consistent dtype (e.g., float64).
- When exporting, round to a fixed precision (e.g., 6 decimal places).

## Randomness
- Single global seed passed to all stochastic components.
- Record seed in run.json and in each artifact header (where applicable).

## Tests
- Verify identical Top-K when input order is permuted.
- Verify identical outputs on repeated runs with the same seed and inputs.