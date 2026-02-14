# Bespoke Corpora

Local Flask app for browsing researcher-built corpora (JSON/JSONL) in the browser.
Two collection types: **articles** (original + translation) and **threads** (canonical text + commentator annotations).

## Setup & Run

```bash
bash run.sh
```

This creates `.venv/`, installs dependencies, and starts the server at `http://127.0.0.1:5222`.

Manual alternative:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## Data Format

Collections live in `data/`. Each collection is a directory with a `manifest.json`.

### manifest.json (required in every collection)

```json
{ "type": "articles", "title": "Collection Name", "description": "Optional" }
```

`type` is either `"articles"` or `"threads"`.

### Articles collection

Files: `manifest.json` + `articles.jsonl` (or `articles.json`)

```json
{
  "id": "unique-id",
  "metadata": { "title": "Title", "date": { "year": "1800" } },
  "original": { "paragraphs": ["First paragraph", "Second"] },
  "translation": { "paragraphs": ["번역 1", "번역 2"] },
  "has_translation": true
}
```

`original` and `translation` accept `{"paragraphs": [...]}` or a plain string.

### Threads collection

Files: `manifest.json` + `segments.json` + `annotations.jsonl`

**segments.json:**
```json
{
  "segments": [{
    "id": "seg-001",
    "label": "Sidebar label",
    "ref_text": "Canonical text",
    "ref_record": "ann-001",
    "mapped_records": ["ann-001", "ann-002"]
  }]
}
```

**annotations.jsonl** (one per line):
```json
{
  "id": "ann-001",
  "commentator": "Author (original script)",
  "commentator_name": "Author (display)",
  "era": "Dynasty/Period",
  "life_years": "1130-1200",
  "commentary_type": "注",
  "source": "Source title",
  "text": "Commentary text",
  "translation_ko": "Translation"
}
```

## Configuration

All optional — defaults work out of the box.

| Variable | Default | Purpose |
|----------|---------|---------|
| `BESPOKE_DATA_DIR` | `./data` | Data root |
| `BESPOKE_HOST` | `127.0.0.1` | Server host |
| `BESPOKE_PORT` | `5222` | Server port |

## Project Structure

```
app.py              ← Flask routes (entry point)
config.py           ← Env var configuration
server/
├── collections.py  ← Auto-discover collections via manifest.json
├── articles.py     ← Article list/detail + pagination
├── threads.py      ← Segments + annotations
├── loader.py       ← JSONL/JSON loading + normalization
├── cache.py        ← mtime-based in-memory cache
└── safety.py       ← Path traversal prevention
templates/          ← Jinja2 HTML (index, articles, threads)
static/             ← Vanilla CSS + JS (no build step)
data/               ← User collections go here
tests/              ← pytest (test_loader.py, test_safety.py)
```

## Testing

```bash
source .venv/bin/activate
pytest tests/ -v
```

## Constraints

- **Flask only** — don't add databases, ORMs, or heavy frameworks
- **No build step** — frontend is vanilla JS/CSS, keep it that way
- **`.venv/`** — use `.venv/` for virtual environment, not `venv/`
- **Sample data is sample** — `data/sample-articles/` and `data/sample-threads/` are examples; don't treat them as real data
- **Read-only viewer** — no editing, annotation, or write-back features
- **Local-only** — no auth, no deployment, no multi-user

## Common Tasks

**"실행해줘" (Run it)**:
→ `bash run.sh`

**"새 컬렉션 만들어줘" (Create new collection)**:
→ Create `data/{collection-id}/manifest.json` with type + title, then add data files.

**"데이터 넣어줘" (Add my data)**:
→ Put JSONL/JSON files in a new `data/` subdirectory with a `manifest.json`. App auto-discovers on next page load.

**"포트 바꿔줘" (Change port)**:
→ `BESPOKE_PORT=8080 python3 app.py` or edit `config.py`.
