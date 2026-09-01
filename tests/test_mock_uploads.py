import json

from backend.ingestion.service import load_dataset
from scripts.generate_mock_uploads import generate_records, validate_outputs, write_csv, write_json, write_xml


def test_mock_generation_is_deterministic_and_valid():
    records_a = generate_records(40, seed=42)
    records_b = generate_records(40, seed=42)

    assert records_a == records_b
    assert len(records_a) == 40
    assert len({record["txid"] for record in records_a}) == 40
    for record in records_a:
        assert record["txid"].startswith("synthetic_tx_")
        assert sum(record["input_amounts"]) >= sum(record["output_amounts"]) + record["fee"]
        assert record["fee"] >= 0
        assert all(amount > 0 for amount in record["input_amounts"] + record["output_amounts"])


def test_mock_formats_are_equivalent_and_ingestion_compatible(tmp_path):
    records = generate_records(25, seed=7)
    paths = (
        tmp_path / "bitcoin_transactions.csv",
        tmp_path / "bitcoin_transactions.json",
        tmp_path / "bitcoin_transactions.xml",
    )
    write_csv(records, paths[0])
    write_json(records, paths[1])
    write_xml(records, paths[2])

    validate_outputs(records, paths)
    expected_ids = [record["txid"] for record in records]
    assert [record["txid"] for record in load_dataset(paths[0])] == expected_ids
    assert [record["txid"] for record in load_dataset(paths[1])] == expected_ids
    assert [record["txid"] for record in load_dataset(paths[2])] == expected_ids
    assert json.loads(paths[1].read_text(encoding="utf-8"))[0]["txid"] == expected_ids[0]