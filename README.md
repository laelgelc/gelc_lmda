# GELC - Lexical Multi-Dimensional Analysis

## Quick Demo (Fixture Corpus)

This demo creates a tiny fixture corpus, runs the Slice v0 pipeline, and validates outputs. It standardizes first-run expectations for collaborators and CI.

### 1) Create the fixture corpus

Option A: Run the helper script
```
bash bash scripts/create_fixture_corpus.sh
``` 

Option B: Create it inline
```
bash mkdir -p data/fixture_corpus/{news,blogs,reports}
cat > data/fixture_corpus/news/news_001.txt << 'EOF' The central bank raised interest rates today. Markets reacted with caution. EOF cat > data/fixture_corpus/news/news_002.txt << 'EOF' Elections are scheduled next month as parties announce policy platforms. EOF
cat > data/fixture_corpus/blogs/blog_001.txt << 'EOF' I tried a new recipe today and documented each step with photos. EOF cat > data/fixture_corpus/blogs/blog_002.txt << 'EOF' Traveling by train feels slower but reveals quiet landscapes and stories. EOF
cat > data/fixture_corpus/reports/report_001.txt << 'EOF' The quarterly report outlines revenue growth and reduced operational costs. EOF cat > data/fixture_corpus/reports/report_002.txt << 'EOF' The committee recommends additional audits to ensure compliance. EOF
``` 

### 2) Run the pipeline
```
bash lmda run --config config.example.yaml --input data/fixture_corpus --output artefacts/
``` 

### 3) Validate the run.json and artifact hashes
```
bash python scripts/validate_run.py --run-json artefacts/run.json --project-root .
``` 

### 4) Inspect key outputs (optional)
```
bash head -n 5 artefacts/vocabulary.csv head -n 5 artefacts/factors_loadings.csv head -n 5 artefacts/factors_scores.csv
``` 

### Expected Artifacts (Slice v0)
- artefacts/run.json (artifact index, hashes, timings)
- artefacts/logs/run.log
- artefacts/vocabulary.csv
- artefacts/counts_raw.npz
- artefacts/counts_norm.npz
- artefacts/factors_loadings.csv
- artefacts/factors_scores.csv
- artefacts/explained_variance.csv
- artefacts/scree_plot.png  # or .svg per config

## Run the PoC (CLI and GUI)

- CLI (recommended for quick iterations)
  - python run_lmda_poc.py --help
  - python run_lmda_poc.py
- GUI (PySide6)
  - python run_lmda_poc.py --gui

For developer details, packaging (PyInstaller), and troubleshooting, see docs/poc/ADD_GUI.md.

## License

This project is licensed under the Apache License, Version 2.0. See the LICENSE file for details. A NOTICE file is included for attribution notices required by Apache-2.0.

## Citation

If you use this software in academic work, please cite:

Berber Sardinha, T., & Fitzsimmons-Doolan, S. (2025). Lexical Multi-Dimensional Analysis: Identifying Discourses and Ideologies. Cambridge University Press. https://www.cambridge.org/core/elements/lexical-multidimensional-analysis/B2321B62435360F4F7C4AF3F1CCF4E59

A machine-readable citation is provided in CITATION.cff.

## Third-party licenses

This project uses PySide6/Qt (LGPLv3). When distributing binaries:
- Bundle Qt as shared libraries (the default in common Python packagers).
- Do not add technical measures preventing users from replacing the Qt libraries.
- Include the LGPLv3 and Qt license texts in your distribution (e.g., in a licenses/ directory and reference them here).

Other Python dependencies are under permissive licenses (MIT/BSD/Apache) unless noted.
