from fastapi.testclient import TestClient

from backend.api.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ingest_endpoint_with_synthetic_csv():
    response = client.post("/ingest", json={"path": "data/synthetic/transactions.csv"})
    assert response.status_code == 200
    assert response.json()["records_loaded"] > 0


def test_analyze_endpoint():
    response = client.post("/analyze", json={"path": "data/synthetic/transactions.csv"})
    assert response.status_code == 200
    assert response.json()["dataset_statistics"]["total_records"] > 0
    assert "wallet_risk_scores" in response.json()


def test_stats_requires_an_uploaded_dataset():
    response = client.get("/stats")
    assert response.status_code == 422


def test_alerts_requires_an_uploaded_dataset():
    response = client.get("/alerts")
    assert response.status_code == 422


def test_alerts_for_wallet_requires_an_uploaded_dataset():
    response = client.get("/alerts/does-not-exist")
    assert response.status_code == 422


def test_entity_evidence_requires_an_uploaded_dataset():
    response = client.get("/entities/unknown-wallet/evidence")
    assert response.status_code == 422
