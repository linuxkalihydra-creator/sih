# End-to-end pipeline

This project includes a complete offline synthetic investigation pipeline that coordinates the existing ingestion, enrichment, correlation, graph, ML, and explainability modules without requiring external services.

## Pipeline stages

1. Load a local dataset from CSV, JSON, or XML.
2. Validate required fields and unique transaction identifiers.
3. Normalize records into the canonical internal schema.
4. Enrich records with offline GeoIP/ASN fallback data when available.
5. Build wallet/IP/transaction correlation indexes.
6. Construct a lightweight local graph representation.
7. Engineer wallet-level features without using `behavior_type` as an ML feature.
8. Run Isolation Forest anomaly detection.
9. Run DBSCAN clustering.
10. Aggregate wallet risk scores.
11. Build human-readable explanations and evidence summaries.
12. Write machine-readable results to the processed output directory.

## CLI usage

Generate 1,000 synthetic records:

```bash
uv run python scripts/generate_dataset.py --records 1000
```

Run the full pipeline:

```bash
uv run python scripts/run_analysis.py --input data/synthetic/transactions.csv --output-dir data/processed
```

Additional options:

```bash
uv run python scripts/run_analysis.py --input data/synthetic/transactions.json --contamination 0.08 --random-state 7
```

## Output files

The workflow writes a set of useful project artifacts into the output directory, including:

- `analysis_summary.json`
- `wallet_risk_scores.json`
- `wallet_features.csv`
- `wallet_clusters.csv`
- `investigative_leads.json`

## API startup

Run the local service:

```bash
uv run python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload
```

## Notes

- This pipeline is intentionally offline and synthetic.
- `behavior_type` is used only for evaluation and not as a feature in the ML models.
- Neo4j is optional and non-blocking; the pipeline continues using the local graph representation when Neo4j is unavailable.
