# codespace — Pipeline Scripts

Four scripts, one pipeline. Run them in order.

## Setup

```bash
# From the project root
pip install -r requirements.txt
pip install gradio>=6.9.0   # needed for app.py only
```

Copy `.env.example` to `.env` and add your Groq API key:
```
GROQ_API_KEY=your_key_here
```

## Run order

```bash
cd codespace

# 1. Ingest + chunk documents (sanity check)
python ingest.py

# 2. Embed chunks and store in ChromaDB  ← do this once
python embed.py

# 3. CLI — run the 5 evaluation questions
python query.py

# 4. Launch the Gradio UI
python app.py
```

## File map

| File | Stage | What it does |
|------|-------|--------------|
| `ingest.py` | 1 — Ingestion | Loads `.md`/`.txt` from `/documents`, cleans Markdown/HTML, chunks at ~450 chars with 60-char overlap |
| `embed.py`  | 2 — Embedding | Embeds chunks with `all-MiniLM-L6-v2`, persists to ChromaDB; exposes `retrieve(query, k)` |
| `query.py`  | 3 — Generation | Calls `retrieve()`, builds a grounded prompt, calls Groq `llama-3.3-70b-versatile`, returns `{answer, sources}` |
| `app.py`    | 4 — Interface | Gradio UI with question input, top-k slider, answer box, and sources box |

## Notes

- ChromaDB data is stored locally in `codespace/chroma_store/` (git-ignored).
- Re-run `python embed.py` only if you add or change documents.
- To force a full re-index: `build_index(force_rebuild=True)` in `embed.py`.
