# Ingestion v0 Checklist

- [ ] Reads files from input folder; subfolders become categories (metadata)
- [ ] Deterministic path ordering (document ID mapping)
- [ ] Encoding handling: UTF-8 default, BOM support, error reporting
- [ ] Logs summary (files read, categories counts)
- [ ] Records source path and category for each document