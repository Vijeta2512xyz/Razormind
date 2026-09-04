from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def _normalise_document(text: str) -> str:
    return " ".join(text.split())


def ingest_directory(knowledge_base_dir: str | Path, output_path: str | Path) -> list[dict]:
    """Read Markdown/text runbooks and persist a small JSON document index."""
    source_dir = Path(knowledge_base_dir)
    output = Path(output_path)
    documents: list[dict] = []

    for path in sorted(source_dir.glob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = _normalise_document(path.read_text(encoding="utf-8"))
        if not text:
            continue
        documents.append(
            {
                "document_id": path.stem,
                "title": path.stem.replace("_", " ").title(),
                "source": path.name,
                "text": text,
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(documents, indent=2), encoding="utf-8")
    return documents
