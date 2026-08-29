"""High-level correlation service for wallet, IP, and temporal linkage analysis."""

from __future__ import annotations

from typing import Any

from backend.correlation.ip_wallet import ip_to_wallets, ip_wallet_correlation_score
from backend.correlation.temporal import sort_records_by_time, time_gap_seconds, wallet_temporal_score
from backend.correlation.wallet_transaction import transaction_to_wallets, wallet_correlation_score, wallet_to_transactions


def build_correlation_index(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Construct a correlation index across wallet, transaction, and IP relationships."""
    sorted_records = sort_records_by_time(records)
    wallet_map = wallet_to_transactions(sorted_records)
    ip_map = ip_to_wallets(sorted_records)
    tx_wallet_map = {str(record.get("txid", "")): transaction_to_wallets(record) for record in sorted_records}

    return {
        "sorted_records": sorted_records,
        "wallet_map": wallet_map,
        "ip_map": ip_map,
        "transaction_wallet_map": tx_wallet_map,
    }


def correlate_ip_to_wallet(ip_address: str, wallet_address: str, correlation_index: dict[str, Any]) -> float:
    """Return a numeric score for an IP-wallet association."""
    return ip_wallet_correlation_score(ip_address, wallet_address, correlation_index["ip_map"])


def correlate_wallets(source_wallet: str, target_wallet: str, correlation_index: dict[str, Any]) -> float:
    """Return a numeric score for repeated wallet overlap."""
    return wallet_correlation_score(source_wallet, target_wallet, correlation_index["wallet_map"])


def correlate_temporal_activity(wallet_address: str, records: list[dict[str, Any]]) -> float:
    """Return a temporal activity score for a wallet."""
    return wallet_temporal_score(wallet_address, records)


def get_related_transactions(wallet_address: str, correlation_index: dict[str, Any]) -> list[str]:
    """Return the transaction IDs associated with a wallet."""
    return correlation_index["wallet_map"].get(wallet_address, [])


def get_related_ips(wallet_address: str, records: list[dict[str, Any]]) -> list[str]:
    """Return IP addresses linked to the wallet in the synthetic dataset."""
    related: set[str] = set()
    for record in records:
        wallets = record.get("input_addresses", []) + record.get("output_addresses", [])
        if str(wallet_address) in {str(wallet) for wallet in wallets}:
            related.add(str(record.get("src_ip", "")))
            related.add(str(record.get("dst_ip", "")))
    return sorted(ip for ip in related if ip)


__all__ = [
    "build_correlation_index",
    "correlate_ip_to_wallet",
    "correlate_wallets",
    "correlate_temporal_activity",
    "get_related_transactions",
    "get_related_ips",
    "time_gap_seconds",
]
