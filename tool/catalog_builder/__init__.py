"""Catalog Builder: turns pricing_data/beer_master.csv + enrichment/ into
catalog/catalog.json.

See docs/CATALOG-BUILDER-IMPLEMENTATION-DESIGN.md for the full module
architecture, docs/CATALOG-CONTRACT-1.0.md for the exact output schema,
and docs/IMPLEMENTATION-ROADMAP.md for build sequencing.

Implemented so far: models.py (data types), value_metrics.py,
benchmarks.py, value_score.py (the pure-computation layer — no file I/O,
no join, no validation). Everything else named in the implementation
design (readers, join, validation, serialization, CLIs) is not yet
implemented.
"""
