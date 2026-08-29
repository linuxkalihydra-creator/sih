"""FastAPI service for the offline synthetic investigation platform."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.graph.neo4j_client import Neo4jUnavailableError
from backend.ingestion.service import load_dataset
from backend.pipeline.orchestrator import AnalysisOrchestrator

app = FastAPI(title="Bitcoin Investigation Platform")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_DEFAULT_ANALYSIS_PATH = "data/synthetic/transactions.csv"


class AnalyzeRequest(BaseModel):
    path: str = _DEFAULT_ANALYSIS_PATH
    output_dir: str | None = None
    contamination: float = 0.05
    random_state: int = 42


class IngestRequest(BaseModel):
    path: str


def _analysis_cache() -> dict[str, Any]:
    cache = app.state.__dict__.get("analysis_cache")
    if cache is None:
        cache = {}
        app.state.analysis_cache = cache
    return cache


@app.get("/health")
def health() -> dict[str, Any]:
    """Return a health indicator for the offline platform."""
    return {
        "status": "ok",
        "mode": "offline_synthetic",
        "graph_available": False,
    }


@app.post("/ingest")
def ingest(request: IngestRequest) -> dict[str, Any]:
    """Ingest a dataset and return the canonical records count."""
    try:
        records = load_dataset(request.path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"records_loaded": len(records), "source": request.path}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    """Run the real end-to-end analysis pipeline for a local dataset."""
    try:
        orchestrator = AnalysisOrchestrator(contamination=request.contamination, random_state=request.random_state)
        result = orchestrator.run(request.path, output_dir=request.output_dir, contamination=request.contamination, random_state=request.random_state)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Neo4jUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - broad guard for runtime failures
        raise HTTPException(status_code=500, detail=f"Pipeline failure: {exc}") from exc

    cache = _analysis_cache()
    cache["latest"] = result

    return {
        "dataset_statistics": result.dataset_statistics,
        "ingestion_statistics": result.ingestion_statistics,
        "validation_statistics": result.validation_statistics,
        "correlation_statistics": result.correlation_statistics,
        "graph_statistics": result.graph_statistics,
        "graph_available": result.graph_available,
        "wallet_risk_scores": result.risk_scores[["wallet_id", "risk_score", "risk_level"]].to_dict(orient="records"),
        "wallet_features": result.wallet_features.to_dict(orient="records"),
        "cluster_results": result.cluster_results.to_dict(orient="records"),
        "anomaly_results": result.anomaly_results.to_dict(orient="records"),
        "explanations": result.explanations.to_dict(orient="records"),
        "evaluation": result.evaluation,
        "processing_duration": round(result.processing_duration, 6),
    }


@app.get("/stats")
def stats() -> dict[str, Any]:
    """Return the statistics for the default synthetic dataset."""
    records = load_dataset(_DEFAULT_ANALYSIS_PATH)
    return {
        "total_transactions": len(records),
        "unique_wallets": len({wallet for record in records for wallet in record["input_addresses"] + record["output_addresses"]}),
        "unique_ips": len({record["src_ip"] for record in records} | {record["dst_ip"] for record in records}),
        "behavior_types": sorted({record["behavior_type"] for record in records}),
    }


@app.get("/alerts")
def alerts() -> list[dict[str, Any]]:
    """Return the top wallet alerts from the latest pipeline run."""
    latest = _analysis_cache().get("latest")
    if latest is None:
        result = AnalysisOrchestrator().run(_DEFAULT_ANALYSIS_PATH)
        _analysis_cache()["latest"] = result
        latest = result

    alerts_list = []
    for _, row in latest.risk_scores.sort_values("risk_score", ascending=False).head(20).iterrows():
        alerts_list.append({
            "wallet_id": str(row["wallet_id"]),
            "risk_score": float(row["risk_score"]),
            "risk_level": str(row["risk_level"]),
            "cluster_id": int(latest.cluster_results.loc[latest.cluster_results["wallet_id"] == row["wallet_id"], "cluster_id"].iloc[0]) if not latest.cluster_results.empty else None,
            "confidence": round(float(max(0.5, min(0.99, row["risk_score"] / 100))), 3),
            "top_reasons": ["High anomaly score", "Elevated transaction footprint", "Unusual graph connectivity"],
        })
    return alerts_list


@app.get("/alerts/{wallet_id}")
def alert_for_wallet(wallet_id: str) -> dict[str, Any]:
    """Return a single alert for a wallet if it exists in the latest analysis snapshot."""
    latest = _analysis_cache().get("latest")
    if latest is None:
        latest = AnalysisOrchestrator().run(_DEFAULT_ANALYSIS_PATH)
        _analysis_cache()["latest"] = latest

    row = latest.risk_scores[latest.risk_scores["wallet_id"] == wallet_id]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Wallet not found in latest analysis: {wallet_id}")

    cluster_row = latest.cluster_results[latest.cluster_results["wallet_id"] == wallet_id]
    cluster_id = int(cluster_row["cluster_id"].iloc[0]) if not cluster_row.empty else None
    reasons = [
        "Elevated anomaly score",
        "Unusual transaction diversity",
        "High network connectivity"
    ]
    return {
        "wallet_id": wallet_id,
        "risk_score": float(row["risk_score"].iloc[0]),
        "risk_level": str(row["risk_level"].iloc[0]),
        "confidence": 0.9,
        "cluster_id": cluster_id,
        "top_reasons": reasons,
    }


@app.get("/entities/{wallet_id}")
def entity(wallet_id: str) -> dict[str, Any]:
    """Return a wallet summary dataset-health view for the given entity."""
    latest = _analysis_cache().get("latest")
    if latest is None:
        latest = AnalysisOrchestrator().run(_DEFAULT_ANALYSIS_PATH)
        _analysis_cache()["latest"] = latest

    wallet_features = latest.wallet_features[latest.wallet_features["wallet_id"] == wallet_id]
    if wallet_features.empty:
        raise HTTPException(status_code=404, detail=f"Wallet not found: {wallet_id}")

    row = wallet_features.iloc[0]
    risk_row = latest.risk_scores[latest.risk_scores["wallet_id"] == wallet_id]
    cluster_row = latest.cluster_results[latest.cluster_results["wallet_id"] == wallet_id]
    anomaly_row = latest.anomaly_results[latest.anomaly_results["wallet_id"] == wallet_id]

    related_ips = []
    for record in latest.records:
        wallets = set(str(item) for item in record.get("input_addresses", [])) | set(str(item) for item in record.get("output_addresses", []))
        if wallet_id in wallets:
            related_ips.extend([str(record.get("src_ip", "")), str(record.get("dst_ip", ""))])
    return {
        "wallet_id": wallet_id,
        "risk_score": float(risk_row["risk_score"].iloc[0]) if not risk_row.empty else 0.0,
        "risk_level": str(risk_row["risk_level"].iloc[0]) if not risk_row.empty else "LOW",
        "transaction_statistics": {
            "transaction_count": int(row["transaction_count"]),
            "incoming_transaction_count": int(row["incoming_transaction_count"]),
            "outgoing_transaction_count": int(row["outgoing_transaction_count"]),
        },
        "network_statistics": {
            "unique_ips": int(row["unique_ips"]),
            "unique_counterparties": int(row["unique_counterparties"]),
            "graph_degree": int(row["graph_degree"]),
        },
        "ml_information": {
            "anomaly_score": float(anomaly_row["anomaly_score"].iloc[0]) if not anomaly_row.empty else 0.0,
            "anomaly_label": int(anomaly_row["anomaly_label"].iloc[0]) if not anomaly_row.empty else 0,
        },
        "cluster_information": {"cluster_id": int(cluster_row["cluster_id"].iloc[0]) if not cluster_row.empty else None},
        "explanations": latest.explanations[latest.explanations["wallet_id"] == wallet_id].to_dict(orient="records"),
        "evidence": latest.evidence.get(wallet_id, {}),
        "related_entities": sorted(set(related_ips)),
    }


@app.get("/entities/{wallet_id}/evidence")
def entity_evidence(wallet_id: str) -> dict[str, Any]:
    """Return the evidence summary for a wallet."""
    latest = _analysis_cache().get("latest")
    if latest is None:
        latest = AnalysisOrchestrator().run(_DEFAULT_ANALYSIS_PATH)
        _analysis_cache()["latest"] = latest

    if wallet_id not in latest.evidence:
        raise HTTPException(status_code=404, detail=f"Evidence not found for wallet: {wallet_id}")
    return latest.evidence[wallet_id]


@app.get("/entities/{wallet_id}/graph")
def entity_graph(wallet_id: str) -> dict[str, Any]:
    """Return a graph payload for a wallet built from the synthetic transaction graph."""
    latest = _analysis_cache().get("latest")
    if latest is None:
        latest = AnalysisOrchestrator().run(_DEFAULT_ANALYSIS_PATH)
        _analysis_cache()["latest"] = latest

    if wallet_id not in {str(item["wallet_id"]) for item in latest.risk_scores[["wallet_id"]].to_dict(orient="records")}:
        raise HTTPException(status_code=404, detail=f"Wallet not found: {wallet_id}")

    nodes = []
    edges = []
    for item in latest.graph_records:
        if item.get("id") == wallet_id or item.get("type") == "Transaction":
            nodes.append({"id": str(item.get("id", "")), "type": str(item.get("type", "")), "relationship": str(item.get("relationship", ""))})
    return {"wallet_id": wallet_id, "nodes": nodes, "edges": edges}


@app.get("/entities/{wallet_id}/transactions")
def entity_transactions(wallet_id: str) -> list[dict[str, Any]]:
    """Return all synthetic records associated with a wallet."""
    latest = _analysis_cache().get("latest")
    if latest is None:
        latest = AnalysisOrchestrator().run(_DEFAULT_ANALYSIS_PATH)
        _analysis_cache()["latest"] = latest

    result = []
    for record in latest.records:
        wallet_set = {str(item) for item in record.get("input_addresses", [])} | {str(item) for item in record.get("output_addresses", [])}
        if wallet_id in wallet_set:
            result.append({
                "txid": record.get("txid"),
                "timestamp": record.get("timestamp"),
                "src_ip": record.get("src_ip"),
                "dst_ip": record.get("dst_ip"),
                "input_addresses": record.get("input_addresses", []),
                "output_addresses": record.get("output_addresses", []),
                "fee": record.get("fee"),
            })
    return result


@app.get("/clusters")
def clusters() -> list[dict[str, Any]]:
    """Return the latest cluster assignment summary."""
    latest = _analysis_cache().get("latest")
    if latest is None:
        latest = AnalysisOrchestrator().run(_DEFAULT_ANALYSIS_PATH)
        _analysis_cache()["latest"] = latest

    return latest.cluster_results.to_dict(orient="records")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
