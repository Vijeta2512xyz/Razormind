from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9_]+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "is", "it", "of", "on", "or", "the", "to", "with", "this",
    "that", "during", "when", "into", "after", "before", "all", "use",
}


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


class RunbookRetriever:
    """Lightweight TF-IDF + cosine retriever with transparent scores."""

    def __init__(self, documents: list[dict]):
        if not documents:
            raise ValueError("At least one document is required")
        self.documents = documents
        self.doc_tokens = [tokenize(d["text"]) for d in documents]
        self.doc_term_counts = [Counter(tokens) for tokens in self.doc_tokens]
        self.document_frequency = Counter()
        for counts in self.doc_term_counts:
            self.document_frequency.update(counts.keys())
        self.n_docs = len(documents)
        self.norms = [self._vector_norm(counts) for counts in self.doc_term_counts]

    @classmethod
    def from_json(cls, path: str | Path) -> "RunbookRetriever":
        docs = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(docs)

    def _idf(self, term: str) -> float:
        df = self.document_frequency.get(term, 0)
        return math.log((1 + self.n_docs) / (1 + df)) + 1.0

    def _weight(self, term: str, count: int) -> float:
        return (1.0 + math.log(count)) * self._idf(term)

    def _vector_norm(self, counts: Counter) -> float:
        return math.sqrt(sum(self._weight(t, c) ** 2 for t, c in counts.items()))

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        query_counts = Counter(tokenize(query))
        query_norm = self._vector_norm(query_counts)
        results = []

        for doc, counts, norm in zip(self.documents, self.doc_term_counts, self.norms):
            dot = sum(
                self._weight(term, q_count) * self._weight(term, counts[term])
                for term, q_count in query_counts.items()
                if term in counts
            )
            score = dot / (query_norm * norm) if query_norm and norm else 0.0
            results.append({
                "document_id": doc["document_id"],
                "title": doc["title"],
                "source": doc["source"],
                "text": doc["text"],
                "score": float(score),
            })

        results.sort(key=lambda item: (-item["score"], item["document_id"]))
        return results[:top_k]
