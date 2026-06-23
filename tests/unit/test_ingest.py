"""Unit tests for ingest.py — no network, no Neo4j, no Azure."""
import pytest
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from ingest import _parse_json, _extract_text, extract_entities, ingest_document


# ---------- _parse_json ----------

def test_parse_json_valid():
    raw = '{"entities": [{"name": "Pump-01", "type": "Equipment", "metadata": {}}], "relationships": []}'
    result = _parse_json(raw)
    assert result["entities"][0]["name"] == "Pump-01"


def test_parse_json_strips_markdown_fences():
    raw = "```json\n{\"entities\": [], \"relationships\": []}\n```"
    result = _parse_json(raw)
    assert result["entities"] == []


def test_parse_json_strips_plain_fences():
    raw = "```\n{\"entities\": [], \"relationships\": []}\n```"
    result = _parse_json(raw)
    assert result == {"entities": [], "relationships": []}


def test_parse_json_malformed_returns_empty():
    result = _parse_json("not json at all")
    assert result == {"entities": [], "relationships": []}


def test_parse_json_empty_string_returns_empty():
    result = _parse_json("")
    assert result == {"entities": [], "relationships": []}


def test_parse_json_defaults_missing_keys():
    result = _parse_json('{"entities": [{"name": "X", "type": "Equipment", "metadata": {}}]}')
    assert "relationships" in result
    assert result["relationships"] == []


# ---------- _extract_text ----------

def test_extract_text_txt():
    raw = b"Pump-01 bearing failure report"
    assert "Pump-01" in _extract_text("report.txt", raw)


def test_extract_text_csv():
    raw = "Valve-02,open,2025-01-01".encode("utf-8")
    assert "Valve-02" in _extract_text("data.csv", raw)


def test_extract_text_md():
    raw = b"# Maintenance Log\nPump-01"
    assert "Pump-01" in _extract_text("log.md", raw)


def test_extract_text_non_utf8_bytes_dont_crash():
    raw = bytes(range(256))
    result = _extract_text("file.txt", raw)
    assert isinstance(result, str)


def test_extract_text_empty_file():
    result = _extract_text("empty.txt", b"")
    assert result == ""


# ---------- extract_entities ----------

FIXTURE_RESPONSE = (
    '{"entities": [{"name": "Pump-01", "type": "Equipment", "metadata": {}}], '
    '"relationships": []}'
)


@patch("ingest.get_chat_response")
def test_extract_entities_parses_llm_response(mock_llm):
    mock_llm.return_value = FIXTURE_RESPONSE
    result = extract_entities("Pump-01 was inspected on 2025-01-15")
    assert len(result["entities"]) == 1
    assert result["entities"][0]["name"] == "Pump-01"
    assert result["entities"][0]["type"] == "Equipment"


@patch("ingest.get_chat_response")
def test_extract_entities_handles_llm_exception(mock_llm):
    mock_llm.side_effect = Exception("Azure timeout")
    result = extract_entities("any text")
    assert result == {"entities": [], "relationships": []}


@patch("ingest.get_chat_response")
def test_extract_entities_truncates_long_text(mock_llm):
    mock_llm.return_value = FIXTURE_RESPONSE
    long_text = "x" * 10_000
    extract_entities(long_text)
    call_args = mock_llm.call_args[0][1]  # second positional arg (user prompt)
    assert len(call_args) < 5_000  # 4000 char limit + prompt overhead


@patch("ingest.get_chat_response")
def test_extract_entities_uses_json_mode(mock_llm):
    mock_llm.return_value = FIXTURE_RESPONSE
    extract_entities("some text")
    _, kwargs = mock_llm.call_args
    assert kwargs.get("json_mode") is True


# ---------- ingest_document ----------

@patch("ingest.graph")
@patch("ingest.get_chat_response")
def test_ingest_document_returns_correct_shape(mock_llm, mock_graph):
    mock_llm.return_value = FIXTURE_RESPONSE
    mock_graph.write_entities = MagicMock()
    result = ingest_document("test.txt", b"Pump-01 bearing failure")
    assert result["status"] == "ingested"
    assert result["entity_count"] == 1
    assert "doc_id" in result


@patch("ingest.graph")
@patch("ingest.get_chat_response")
def test_ingest_document_calls_write_entities(mock_llm, mock_graph):
    mock_llm.return_value = FIXTURE_RESPONSE
    mock_graph.write_entities = MagicMock()
    ingest_document("test.txt", b"Pump-01 bearing failure")
    mock_graph.write_entities.assert_called_once()
