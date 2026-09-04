# RazorMind — Milestone 8

Milestone 8 adds measurable evaluation for the incident-intelligence pipeline.

## Added
- Detection precision / recall / F1, confusion counts, incident hit rate, and detection delay.
- Diagnosis root-cause and component accuracy.
- RAG hit rate and mean reciprocal rank.
- LLM structured-output validity and basic grounding-rate checks.
- A single evaluation runner to combine results.

Run tests with:
```powershell
python -m pytest -q
```
