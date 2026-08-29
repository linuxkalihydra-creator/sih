"""Correlation helpers for IP and wallet associations."""

from __future__ import annotations

from typing import Any


def ip_to_wallets(records: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Map IP addresses to the wallets observed with them."""
    mapping: dict[str, set[str]] = {}
    for record in records:
        for ip_key in ("src_ip", "dst_ip"):
            ip_value = str(record.get(ip_key, "")).strip()
            if not ip_value:
                continue
            wallets = record.get("input_addresses", []) + record.get("output_addresses", [])
            mapping.setdefault(ip_value, set()).update(str(wallet) for wallet in wallets)
    return {key: sorted(values) for key, values in mapping.items()}


def ip_wallet_correlation_score(ip_address: str, wallet_address: str, ip_wallet_map: dict[str, list[str]]) -> float:
    """Return a simple 0..1 score for an IP-wallet association."""
    related_wallets = set(ip_wallet_map.get(ip_address, []))
    if not related_wallets:
        return 0.0
    return 1.0 if wallet_address in related_wallets else 0.0
