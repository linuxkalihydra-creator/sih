#!/usr/bin/env python3
"""Run the complete synthetic analysis pipeline for the offline investigation prototype."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.pipeline.orchestrator import AnalysisOrchestrator

logging.basicConfig(level=logging.INFO, format="%(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the offline synthetic investigation pipeline.")
    parser.add_argument("--input", required=True, help="Path to a local synthetic dataset (.csv, .json, .xml).")
    parser.add_argument("--output-dir", default="data/processed", help="Directory for generated analysis artifacts.")
    parser.add_argument("--contamination", type=float, default=0.05, help="Isolation Forest contamination parameter.")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed used by ML routines.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    orchestrator = AnalysisOrchestrator(contamination=args.contamination, random_state=args.random_state)
    result = orchestrator.run(args.input, output_dir=args.output_dir, contamination=args.contamination, random_state=args.random_state)
    print(f"Analysis completed successfully. Transactions: {result.dataset_statistics['total_records']} | Wallets: {result.dataset_statistics['unique_wallets']} | IPs: {result.dataset_statistics['unique_ips']} | Anomalies: {int(result.anomaly_results['anomaly_label'].eq(-1).sum())} | Clusters: {int(result.cluster_results['cluster_id'].nunique())} | High-risk entities: {int((result.risk_scores['risk_score'] >= 60).sum())} | Processing time: {result.processing_duration:.2f}s")


if __name__ == "__main__":
    main()
