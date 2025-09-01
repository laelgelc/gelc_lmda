# Performance Guide (Slice v0)

## Defaults & Limits
- K default = 1000; recommended K ≤ 2000 for v0.
- Factors N default = 6; recommended N ≤ 10.

## Major Costs
- Preprocessing: tokenization/lemmatization/POS—cache outputs.
- Feature extraction: counting + normalization—stream to avoid large peaks.
- Modeling: EFA on K×K covariance/correlation—ensure efficient linear algebra.

## Caching
- Cache preprocessed annotations keyed by input hashes + config + seed.
- Verify cache existence & validity before recomputation.

## Practical Tips
- Avoid dense matrices when possible.
- Batch I/O for large corpora; avoid repeated disk scans.
- Log durations for each stage; flag regressions early.