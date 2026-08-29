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


def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200
    assert response.json()["total_transactions"] > 0


def test_alerts_endpoint():
    response = client.get("/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_alerts_for_wallet():
    response = client.get("/alerts/does-not-exist")
    assert response.status_code == 404 or response.status_code == 200


def test_entity_evidence_endpoint():
    response = client.get("/entities/unknown-wallet/evidence")
    assert response.status_code == 404 or response.status_code == 200
