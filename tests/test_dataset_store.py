from pathlib import Path

from backend.ingestion.dataset_store import DatasetStore


def test_dataset_metadata_survives_a_new_store_instance(tmp_path: Path):
    source = tmp_path / "transactions.csv"
    source.write_text("txid\ntransaction-1\n", encoding="utf-8")
    store = DatasetStore(tmp_path / "uploads")
    dataset = store.register_file(source)
    store.update(dataset["dataset_id"], status="ready", analysis_status="completed", record_count=1)

    restarted_store = DatasetStore(tmp_path / "uploads")
    restored = restarted_store.get(dataset["dataset_id"])
    assert restored is not None
    assert restored["filename"] == "transactions.csv"
    assert restored["analysis_status"] == "completed"
    assert restarted_store.list()[0]["dataset_id"] == dataset["dataset_id"]


def test_uploaded_bytes_are_persisted_with_safe_metadata(tmp_path: Path):
    store = DatasetStore(tmp_path / "uploads")
    dataset = store.register_upload("../transactions.csv", b"txid\ntransaction-1\n")

    assert dataset["filename"] == "transactions.csv"
    assert (tmp_path / "uploads" / dataset["dataset_id"] / "source.csv").is_file()
    assert store.get(dataset["dataset_id"])["status"] == "uploaded"
