# Procedure to build POC

## 1. On Windows

### 1.1 Build
```
(my_env) PS C:\Users\eyamr\PycharmProjects\gelc_lmda> $env:PYTHONPATH = "$PWD\poc\src"
(my_env) PS C:\Users\eyamr\PycharmProjects\gelc_lmda> pyinstaller --name lmda_poc --icon=LAEL.ico --paths poc/src --collect-all spacy --collect-all en_core_web_sm run_lmda_poc.py

<omitted>

=============================================================
A RecursionError (maximum recursion depth exceeded) occurred.
For working around please follow these instructions
=============================================================

1. In your program's .spec file add this line near the top::

     import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

2. Build your program by running PyInstaller with the .spec file as
   argument::

     pyinstaller myprog.spec

3. If this fails, you most probably hit an endless recursion in
   PyInstaller. Please try to track this down as far as possible,
   create a minimal example so we can reproduce and open an issue at
   https://github.com/pyinstaller/pyinstaller/issues following the
   instructions in the issue template. Many thanks.

Explanation: Python's stack-limit is a safety-belt against endless recursion,
eating up memory. PyInstaller imports modules recursively. If the structure
how modules are imported within your program is awkward, this leads to the
nesting being too deep and hitting Python's stack-limit.

With the default recursion limit (1000), the recursion error occurs at about
115 nested imported, with limit 2000 at about 240, with limit 5000 at about
660.

(my_env) PS C:\Users\eyamr\PycharmProjects\gelc_lmda> pyinstaller lmda_poc.spec

<omitted>

273189 INFO: Build complete! The results are available in: C:\Users\eyamr\PycharmProjects\gelc_lmda\dist
(my_env) PS C:\Users\eyamr\PycharmProjects\gelc_lmda> 
```

### 1.2. Run
```
PS C:\Users\eyamr\Downloads> .\lmda_poc\lmda_poc --input .\data\fixture_corpus --output .\artefacts_poc
2025-09-03 06:48:15 | INFO | Logging initialized
2025-09-03 06:48:15 | INFO | PoC run started at 2025-09-03T09:48:15Z
2025-09-03 06:48:15 | INFO | spaCy preflight OK: spacy=3.8.7, model=en_core_web_sm
2025-09-03 06:48:15 | INFO | Discovered 6 candidate files
2025-09-03 06:48:15 | INFO | Ingestion summary: scanned=6, processed=6, errors=0
2025-09-03 06:48:16 | INFO | Wrote artefacts_poc\docs.csv (6 rows)
2025-09-03 06:48:16 | INFO | Wrote artefacts_poc\tokens.csv (45 rows)
2025-09-03 06:48:16 | INFO | Wrote artefacts_poc\run_poc.json
2025-09-03 06:48:16 | INFO | Action Items:
- Review artefacts_poc\run_poc.json
- Inspect artefacts_poc\docs.csv and artefacts_poc\tokens.csv
- Check log at artefacts_poc\logs\poc_run.log
Processed 6 docs across 3 categories in 0.38s. Artifacts at artefacts_poc. See logs/poc_run.log.
PS C:\Users\eyamr\Downloads> 
PS C:\Users\eyamr\Downloads> .\lmda_poc\lmda_poc
usage: lmda_poc [-h] --input INPUT --output OUTPUT [--encoding ENCODING] [--include-patterns INCLUDE_PATTERNS]
                [--exclude-patterns EXCLUDE_PATTERNS] [--keep-stopwords KEEP_STOPWORDS] [--content-pos CONTENT_POS]
                [--lowercase LOWERCASE] [--batch-size BATCH_SIZE] [--dry-run] [--log-level LOG_LEVEL] [--fail-on-decode-error]
lmda_poc: error: the following arguments are required: --input, --output
PS C:\Users\eyamr\Downloads> 
PS C:\Users\eyamr\Downloads> .\lmda_poc\lmda_poc --help
usage: lmda_poc [-h] --input INPUT --output OUTPUT [--encoding ENCODING] [--include-patterns INCLUDE_PATTERNS]
                [--exclude-patterns EXCLUDE_PATTERNS] [--keep-stopwords KEEP_STOPWORDS] [--content-pos CONTENT_POS]
                [--lowercase LOWERCASE] [--batch-size BATCH_SIZE] [--dry-run] [--log-level LOG_LEVEL] [--fail-on-decode-error]

PoC: Ingest .txt corpus and preprocess English with spaCy to produce docs and tokens tables.

options:
  -h, --help            show this help message and exit
  --input INPUT         Input directory (corpus root) (default: None)
  --output OUTPUT       Output directory for PoC artifacts (default: None)
  --encoding ENCODING   Default file encoding (default: utf-8) (default: utf-8)
  --include-patterns INCLUDE_PATTERNS
                        Comma-separated glob patterns to include (default: *.txt)
  --exclude-patterns EXCLUDE_PATTERNS
                        Comma-separated glob patterns to exclude (default: )
  --keep-stopwords KEEP_STOPWORDS
                        Keep stopwords (true/false) (default: False)
  --content-pos CONTENT_POS
                        Comma-separated POS tags to keep as content words (default: NOUN,VERB,ADJ,ADV)
  --lowercase LOWERCASE
                        Lowercase lemmas (true/false) (default: True)
  --batch-size BATCH_SIZE
                        spaCy nlp.pipe batch size (default: 64) (default: 64)
  --dry-run             List what would be processed; do not write artifacts (default: False)
  --log-level LOG_LEVEL
                        Logging level (DEBUG, INFO, WARN, ERROR) (default: INFO)
  --fail-on-decode-error
                        Exit non-zero on decoding error (default: False)

Examples: lmda_poc --input data/fixture_corpus --output artefacts_poc --encoding utf-8 python -m lmda_poc.cli --input
data/fixture_corpus --output artefacts_poc
PS C:\Users\eyamr\Downloads> 
```

## 2. On macOS (Intel x86_64)

### 2.1 Build
```
(my_env) eyamrog@Rog-iMac gelc_lmda % export PYTHONPATH="$PWD/poc/src"
(my_env) eyamrog@Rog-iMac gelc_lmda % pyinstaller lmda_poc.spec

<omitted>

287930 INFO: Build complete! The results are available in: /Users/eyamrog/PycharmProjects/gelc_lmda/dist
(my_env) eyamrog@Rog-iMac gelc_lmda % 
```

### 2.2 Run
```
(my_env) eyamrog@Rog-iMac Downloads % ./lmda_poc/lmda_poc --input ./data/fixture_corpus --output ./artefacts_poc
2025-09-03 07:18:52 | INFO | Logging initialized
2025-09-03 07:18:52 | INFO | PoC run started at 2025-09-03T10:18:52Z
2025-09-03 07:18:53 | INFO | spaCy preflight OK: spacy=3.8.7, model=en_core_web_sm
2025-09-03 07:18:53 | INFO | Discovered 6 candidate files
2025-09-03 07:18:53 | INFO | Ingestion summary: scanned=6, processed=6, errors=0
2025-09-03 07:18:54 | INFO | Wrote artefacts_poc/docs.csv (6 rows)
2025-09-03 07:18:54 | INFO | Wrote artefacts_poc/tokens.csv (45 rows)
2025-09-03 07:18:54 | INFO | Wrote artefacts_poc/run_poc.json
2025-09-03 07:18:54 | INFO | Action Items:
- Review artefacts_poc/run_poc.json
- Inspect artefacts_poc/docs.csv and artefacts_poc/tokens.csv
- Check log at artefacts_poc/logs/poc_run.log
Processed 6 docs across 3 categories in 0.80s. Artifacts at artefacts_poc. See logs/poc_run.log.
(my_env) eyamrog@Rog-iMac Downloads % 
(my_env) eyamrog@Rog-iMac Downloads % ./lmda_poc/lmda_poc                                                       
usage: lmda_poc [-h] --input INPUT --output OUTPUT [--encoding ENCODING] [--include-patterns INCLUDE_PATTERNS] [--exclude-patterns EXCLUDE_PATTERNS]
                [--keep-stopwords KEEP_STOPWORDS] [--content-pos CONTENT_POS] [--lowercase LOWERCASE] [--batch-size BATCH_SIZE] [--dry-run]
                [--log-level LOG_LEVEL] [--fail-on-decode-error]
lmda_poc: error: the following arguments are required: --input, --output
(my_env) eyamrog@Rog-iMac Downloads % 
(my_env) eyamrog@Rog-iMac Downloads % ./lmda_poc/lmda_poc --help
usage: lmda_poc [-h] --input INPUT --output OUTPUT [--encoding ENCODING] [--include-patterns INCLUDE_PATTERNS] [--exclude-patterns EXCLUDE_PATTERNS]
                [--keep-stopwords KEEP_STOPWORDS] [--content-pos CONTENT_POS] [--lowercase LOWERCASE] [--batch-size BATCH_SIZE] [--dry-run]
                [--log-level LOG_LEVEL] [--fail-on-decode-error]

PoC: Ingest .txt corpus and preprocess English with spaCy to produce docs and tokens tables.

options:
  -h, --help            show this help message and exit
  --input INPUT         Input directory (corpus root) (default: None)
  --output OUTPUT       Output directory for PoC artifacts (default: None)
  --encoding ENCODING   Default file encoding (default: utf-8) (default: utf-8)
  --include-patterns INCLUDE_PATTERNS
                        Comma-separated glob patterns to include (default: *.txt)
  --exclude-patterns EXCLUDE_PATTERNS
                        Comma-separated glob patterns to exclude (default: )
  --keep-stopwords KEEP_STOPWORDS
                        Keep stopwords (true/false) (default: False)
  --content-pos CONTENT_POS
                        Comma-separated POS tags to keep as content words (default: NOUN,VERB,ADJ,ADV)
  --lowercase LOWERCASE
                        Lowercase lemmas (true/false) (default: True)
  --batch-size BATCH_SIZE
                        spaCy nlp.pipe batch size (default: 64) (default: 64)
  --dry-run             List what would be processed; do not write artifacts (default: False)
  --log-level LOG_LEVEL
                        Logging level (DEBUG, INFO, WARN, ERROR) (default: INFO)
  --fail-on-decode-error
                        Exit non-zero on decoding error (default: False)

Examples: lmda_poc --input data/fixture_corpus --output artefacts_poc --encoding utf-8 python -m lmda_poc.cli --input data/fixture_corpus --output
artefacts_poc
(my_env) eyamrog@Rog-iMac Downloads % 
```
