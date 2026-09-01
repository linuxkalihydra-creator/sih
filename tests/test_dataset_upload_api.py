from fastapi.testclient import TestClient
import pytest

from backend.api.main import app
from backend.ingestion.dataset_store import DatasetStore


@pytest.mark.parametrize(("filename", "content", "content_type"), [
    ("transactions.csv", b"txid\ntransaction-1\n", "text/csv"),
    ("transactions.json", b"[{\"txid\": \"transaction-1\"}]", "application/json"),
    ("transactions.xml", b"<transactions><transaction /></transactions>", "application/xml"),
])
def test_multipart_upload_creates_a_discoverable_dataset(tmp_path, filename, content, content_type):
    app.state.dataset_store = DatasetStore(tmp_path / "uploads")
    client = TestClient(app)

    response = client.post("/datasets/upload", files={"file": (filename, content, content_type)})

    assert response.status_code == 201
    payload = response.json()
    assert payload["filename"] == filename
    assert payload["status"] == "uploaded"
    assert client.get("/datasets").json()[0]["dataset_id"] == payload["dataset_id"]
