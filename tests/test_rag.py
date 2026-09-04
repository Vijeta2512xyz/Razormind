from pathlib import Path

from app.rag.ingest import ingest_directory
from app.rag.retriever import RunbookRetriever, tokenize


KB = Path(__file__).parents[1] / "app" / "rag" / "knowledge_base"


def test_tokenizer_removes_common_stopwords():
    assert tokenize("The UPI gateway is failing") == ["upi", "gateway", "failing"]


def test_ingest_reads_runbooks(tmp_path):
    output = tmp_path / "index.json"
    docs = ingest_directory(KB, output)
    assert len(docs) == 6
    assert output.exists()
    assert {d["document_id"] for d in docs} == {
        "upi_degradation", "bank_failure", "latency_spike", "gateway_failure",
        "timeout_spike", "regional_degradation",
    }


def test_retriever_returns_relevant_bank_runbook(tmp_path):
    output = tmp_path / "index.json"
    ingest_directory(KB, output)
    retriever = RunbookRetriever.from_json(output)
    results = retriever.search("one bank failures compared with unaffected banks", top_k=3)
    assert results[0]["document_id"] == "bank_failure"
    assert results[0]["score"] > 0


def test_retriever_returns_relevant_upi_runbook(tmp_path):
    output = tmp_path / "index.json"
    ingest_directory(KB, output)
    retriever = RunbookRetriever.from_json(output)
    results = retriever.search("UPI success rate gateway upstream errors", top_k=2)
    assert results[0]["document_id"] == "upi_degradation"


def test_scores_are_sorted(tmp_path):
    output = tmp_path / "index.json"
    ingest_directory(KB, output)
    retriever = RunbookRetriever.from_json(output)
    results = retriever.search("HTTP 504 timeout retries", top_k=6)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_invalid_top_k_rejected(tmp_path):
    output = tmp_path / "index.json"
    ingest_directory(KB, output)
    retriever = RunbookRetriever.from_json(output)
    try:
        retriever.search("timeout", top_k=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
