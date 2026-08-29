"""Typed analysis result models for the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class AnalysisResult:
    """Structured data returned by the orchestration layer."""

    dataset_statistics: dict[str, Any]
    ingestion_statistics: dict[str, Any]
    validation_statistics: dict[str, Any]
    correlation_statistics: dict[str, Any]
    graph_statistics: dict[str, Any]
    wallet_features: pd.DataFrame
    anomaly_results: pd.DataFrame
    cluster_results: pd.DataFrame
    risk_scores: pd.DataFrame
    explanations: pd.DataFrame
    evidence: dict[str, Any]
    processing_duration: float
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    graph_available: bool = False
    evaluation: dict[str, Any] = field(default_factory=dict)
    output_dir: str = "data/processed"
    graph_records: list[dict[str, Any]] = field(default_factory=list)
    records: list[dict[str, Any]] = field(default_factory=list)
