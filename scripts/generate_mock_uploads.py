#!/usr/bin/env python3
"""Generate reproducible synthetic datasets for dashboard upload testing."""

from __future__ import annotations

import argparse
import csv
import json
import random
import xml.etree.ElementTree as ET
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.ingestion.service import load_dataset
from backend.ingestion.validator import validate_record

OUTPUT_DIR = Path("data/mock_uploads")
COUNTRIES = ("US", "DE", "NL", "SG", "IN", "GB", "FR", "CA", "JP", "AU", "BR", "ZA")
SCRIPT_TYPES = ("P2PKH", "P2SH_P2WPKH", "P2WPKH", "P2TR")
BEHAVIORS = ("NORMAL", "EXCHANGE_LIKE", "RAPID_TRANSFER", "LAYERING_LIKE", "MIXING_LIKE", "HIGH_NETWORK_DIVERSITY")
BEHAVIOR_WEIGHTS = (0.62, 0.12, 0.08, 0.06, 0.07, 0.05)
IP_NETWORKS = (IPv4Network("192.0.2.0/24"), IPv4Network("198.51.100.0/24"), IPv4Network("203.0.113.0/24"))
QUANTUM = Decimal("0.00000001")


def money(value: Decimal) -> float:
    return float(value.quantize(QUANTUM))


def make_ip_pool() -> list[str]:
    return [str(IPv4Address(int(network.network_address) + host)) for network in IP_NETWORKS for host in range(1, network.num_addresses - 1)]


def split_amount(total: Decimal, count: int) -> list[float]:
    base = (total / count).quantize(QUANTUM, rounding=ROUND_DOWN)
    values = [base] * count
    values[-1] += total - sum(values)
    return [money(value) for value in values]


def generate_records(records: int = 10000, seed: int = 42) -> list[dict[str, Any]]:
    """Generate one canonical in-memory dataset for all output formats."""
    if records <= 0:
        raise ValueError("Record count must be positive.")

    rng = random.Random(seed)
    wallets = [f"synthetic_wallet_{index:06d}" for index in range(1, 2501)]
    ips = make_ip_pool()[:750]
    wallet_ip = {wallet: ips[index % len(ips)] for index, wallet in enumerate(wallets)}
    wallet_asn = {wallet: 64512 + (index % 10) for index, wallet in enumerate(wallets)}
    wallet_country = {wallet: COUNTRIES[index % len(COUNTRIES)] for index, wallet in enumerate(wallets)}
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    generated: list[dict[str, Any]] = []

    for index in range(records):
        behavior = rng.choices(BEHAVIORS, weights=BEHAVIOR_WEIGHTS, k=1)[0]
        anomalous = behavior in {"RAPID_TRANSFER", "HIGH_NETWORK_DIVERSITY"}
        source_index = rng.randrange(0, 220 if anomalous else len(wallets))
        source = wallets[source_index]
        output_count = rng.randint(2, 4) if behavior in {"EXCHANGE_LIKE", "MIXING_LIKE", "HIGH_NETWORK_DIVERSITY"} else 1
        candidates = [wallet for wallet in wallets if wallet != source]
        targets = rng.sample(candidates, output_count)

        if anomalous:
            timestamp = start + timedelta(days=rng.randrange(21), seconds=36000 + index % 600)
        else:
            timestamp = start + timedelta(days=index % 35, seconds=rng.randrange(86400))

        input_total = Decimal(str(rng.uniform(0.05, 2.5 if not anomalous else 18.0))).quantize(QUANTUM)
        fee = Decimal(str(rng.uniform(0.00001, 0.0015))).quantize(QUANTUM)
        output_total = input_total - fee - (QUANTUM * 2)
        input_amounts = [money(input_total)]
        output_amounts = split_amount(output_total, output_count)
        dst_wallet = targets[0]
        src_ip = wallet_ip[source]
        dst_ip = wallet_ip[dst_wallet]

        generated.append({
            "timestamp": timestamp.isoformat(),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": rng.randrange(1024, 65536),
            "dst_port": 8333 if rng.random() < 0.75 else rng.choice((80, 443, 18444)),
            "txid": f"synthetic_tx_{index + 1:08d}",
            "input_addresses": [source],
            "output_addresses": targets,
            "input_amounts": input_amounts,
            "output_amounts": output_amounts,
            "fee": money(fee),
            "script_type": rng.choice(SCRIPT_TYPES),
            "geo_country": wallet_country[source],
            "asn": wallet_asn[source],
            "behavior_type": behavior,
        })

    return generated


def write_csv(records: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        for record in records:
            row = dict(record)
            for field in ("input_addresses", "output_addresses", "input_amounts", "output_amounts"):
                row[field] = json.dumps(row[field], separators=(",", ":"))
            writer.writerow(row)


def write_json(records: list[dict[str, Any]], path: Path) -> None:
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def write_xml(records: list[dict[str, Any]], path: Path) -> None:
    root = ET.Element("transactions")
    scalar_fields = ("timestamp", "src_ip", "dst_ip", "src_port", "dst_port", "txid", "fee", "script_type", "geo_country", "asn", "behavior_type")
    for record in records:
        transaction = ET.SubElement(root, "transaction")
        for field in scalar_fields:
            ET.SubElement(transaction, field).text = str(record[field])
        for field, child_name in (("input_addresses", "address"), ("output_addresses", "address"), ("input_amounts", "amount"), ("output_amounts", "amount")):
            container = ET.SubElement(transaction, field)
            for value in record[field]:
                ET.SubElement(container, child_name).text = str(value)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def validate_outputs(records: list[dict[str, Any]], paths: tuple[Path, Path, Path]) -> None:
    expected_ids = [record["txid"] for record in records]
    for path in paths:
        loaded = load_dataset(path)
        loaded_ids = [record["txid"] for record in loaded]
        if len(loaded) != len(records) or loaded_ids != expected_ids:
            raise ValueError(f"Ingestion validation failed for {path}")
        errors = [error for record in loaded for error in validate_record(record)]
        if errors:
            raise ValueError(f"Record validation failed for {path}: {errors[:3]}")


def write_readme(records: list[dict[str, Any]], seed: int, path: Path) -> None:
    wallets = {wallet for record in records for wallet in record["input_addresses"] + record["output_addresses"]}
    ips = {record["src_ip"] for record in records} | {record["dst_ip"] for record in records}
    asns = {record["asn"] for record in records}
    countries = {record["geo_country"] for record in records}
    profiles = sorted({record["behavior_type"] for record in records})
    path.write_text(
        "# Synthetic Mock Upload Dataset\n\n"
        "This dataset contains synthetic test data and does not represent real Bitcoin activity. "
        "All wallets, transaction IDs, IP addresses, ASNs, countries, and observations are locally generated.\n\n"
        f"- Records: {len(records)}\n- Approximate wallets: {len(wallets)}\n- IP addresses: {len(ips)}\n"
        f"- Synthetic ASNs: {len(asns)}\n- Countries: {len(countries)}\n- Seed: {seed}\n"
        f"- Behavioral profiles: {', '.join(profiles)}\n\n"
        "Regenerate with:\n\n```text\nuv run python scripts/generate_mock_uploads.py\nuv run python scripts/generate_mock_uploads.py --records 1000 --seed 42\n```\n\n"
        "Files contain the same records in CSV, JSON, and XML formats for dashboard upload testing.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic dashboard upload datasets.")
    parser.add_argument("--records", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    records = generate_records(args.records, args.seed)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = (
        OUTPUT_DIR / "bitcoin_transactions.csv",
        OUTPUT_DIR / "bitcoin_transactions.json",
        OUTPUT_DIR / "bitcoin_transactions.xml",
    )
    write_csv(records, paths[0])
    write_json(records, paths[1])
    write_xml(records, paths[2])
    validate_outputs(records, paths)
    write_readme(records, args.seed, OUTPUT_DIR / "README.md")

    wallets = {wallet for record in records for wallet in record["input_addresses"] + record["output_addresses"]}
    ips = {record["src_ip"] for record in records} | {record["dst_ip"] for record in records}
    asns = {record["asn"] for record in records}
    countries = {record["geo_country"] for record in records}
    print("Synthetic upload dataset generated successfully.")
    print(f"Records: {len(records)}")
    print(f"Wallets: {len(wallets)}")
    print(f"IPs: {len(ips)}")
    print(f"ASNs: {len(asns)}")
    print(f"Countries: {len(countries)}")
    print("\nFiles:")
    for path in paths:
        print(path)
    print("\nCSV validation: PASS")
    print("JSON validation: PASS")
    print("XML validation: PASS")
    print("Synthetic-only dataset: YES")


if __name__ == "__main__":
    main()
