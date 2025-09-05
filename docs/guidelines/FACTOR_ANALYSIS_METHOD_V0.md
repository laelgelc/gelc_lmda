# Factor Analysis Method (v0)

## Inputs
- DFM normalized per-thousand (float64)
- K selected lemmas (Top-K by log-likelihood across categories)
- Parameters: N (default 6), global seed

## Estimation
- Extraction: Exploratory Factor Analysis (EFA)
- Rotation: Varimax
- Convergence: document default tolerance and max iterations
- Determinism: fix random_state/seed

## Outputs
- Loadings (K × N), Scores (docs × N), Explained variance (length N)
- Scree plot saved to file
- Log eigenvalues and cumulative variance

## Validation
- Sanity checks:
    - N ≤ K and N ≤ (docs − 1) when applicable
    - No NaNs/Infs in inputs/outputs
- Re-run reproducibility check (hash compare)
