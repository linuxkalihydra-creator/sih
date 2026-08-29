"""Correlation helpers for wallet-to-transaction relationships.

This layer does not assert ownership or identity. It only records synthetic
correlation patterns that later phases may use as investigative signals.
"""

from __future__ import annotations

from typing import Any


def wallet_to_transactions(records: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Map wallet addresses to the transactions in which they appear."""
    mapping: dict[str, list[str]] = {}
    for record in records:
        for wallet in record.get("input_addresses", []) + record.get("output_addresses", []):
            mapping.setdefault(str(wallet), []).append(str(record.get("txid", "")))
    return mapping


def transaction_to_wallets(record: dict[str, Any]) -> dict[str, list[str]]:
    """Return the wallet graph associated with a single transaction."""
    wallets = list(record.get("input_addresses", [])) + list(record.get("output_addresses", []))
    unique_wallets = list(dict.fromkeys(str(wallet) for wallet in wallets if wallet))
    return {"input_wallets": [str(wallet) for wallet in record.get("input_addresses", [])], "output_wallets": [str(wallet) for wallet in record.get("output_addresses", [])], "all_wallets": unique_wallets}


def wallet_correlation_score(source_wallet: str, target_wallet: str, wallet_links: dict[str, list[str]]) -> float:
    """Compute a simple overlap score for how often two wallets appear in the same transactions."""
    source_txs = set(wallet_links.get(source_wallet, []))
    target_txs = set(wallet_links.get(target_wallet, []))
    if not source_txs or not target_txs:
        return 0.0
    overlap = len(source_txs & target_txs)
    union = len(source_txs | target_txs)
    if union == 0:
        return 0.0
    return round(overlap / union, 4)
