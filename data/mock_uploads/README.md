# Synthetic Mock Upload Dataset

This dataset contains synthetic test data and does not represent real Bitcoin activity. All wallets, transaction IDs, IP addresses, ASNs, countries, and observations are locally generated.

- Records: 10000
- Approximate wallets: 2500
- IP addresses: 750
- Synthetic ASNs: 10
- Countries: 12
- Seed: 42
- Behavioral profiles: EXCHANGE_LIKE, HIGH_NETWORK_DIVERSITY, LAYERING_LIKE, MIXING_LIKE, NORMAL, RAPID_TRANSFER

Regenerate with:

```text
uv run python scripts/generate_mock_uploads.py
uv run python scripts/generate_mock_uploads.py --records 1000 --seed 42
```

Files contain the same records in CSV, JSON, and XML formats for dashboard upload testing.
