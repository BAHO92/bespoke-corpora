# Bespoke Corpora

**English** | [한국어](README_ko.md)

A local-first Flask web app for researchers to browse their own corpora (JSON/JSONL) in the browser.

Read original text and translations side-by-side, scan metadata, and explore **threads** — where multiple commentators annotate the same canonical text. Intentionally simple and hackable: meant to be forked and reshaped per project.

## What This Does

- Browse article collections with original/translation parallel view
- Explore commentary threads (canonical text + multiple annotator cards)
- Auto-discover collections from a flat `data/` directory
- Paginate large collections, display metadata
- Cache in memory by file mtime — no database, no sync

## What This Does NOT Do

- Crawl or scrape sources (bring your own data)
- Full-text search or indexing
- Multi-user authentication or hosting
- Annotation or editing workflows
- Version control for your data

## Quick Start

Open Terminal and paste all three lines at once:

```bash
git clone https://github.com/BAHO92/bespoke-corpora.git
cd bespoke-corpora
bash run.sh
```

`run.sh` sets up everything automatically (Python virtual environment, dependencies) and starts the server. When you see `http://127.0.0.1:5222` in the terminal, open that URL in your browser.

Sample data is included — you'll see it immediately.

> **Using Claude Code?** Run `claude` inside the `bespoke-corpora` folder and say "실행해줘". Claude reads `CLAUDE.md` and handles the rest.

<details>
<summary>Manual setup (if you prefer step-by-step)</summary>

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

</details>

## Data Format

All collections live in `data/`. Each collection is a directory with a `manifest.json`.

### Articles Collection

A flat list of articles with original text and optional translation.

```
data/my-collection/
├── manifest.json
└── articles.jsonl
```

**manifest.json:**
```json
{
    "type": "articles",
    "title": "My Collection"
}
```

**articles.jsonl** — one article per line:
```json
{
    "id": "unique-id",
    "metadata": { "title": "Article Title", "date": {"year": "1800"} },
    "original": { "paragraphs": ["First paragraph", "Second paragraph"] },
    "translation": { "paragraphs": ["번역 첫 단락", "번역 둘째 단락"] },
    "has_translation": true
}
```

**Flexible input:** `original` and `translation` accept either `{"paragraphs": [...]}` or a plain string (auto-split by `\n`).

You can also use `articles.json` (JSON array) instead of JSONL.

### Threads Collection

Canonical text segments with multiple commentator annotations — for modeling commentary traditions.

```
data/my-commentary/
├── manifest.json
├── segments.json
└── annotations.jsonl
```

**manifest.json:**
```json
{
    "type": "threads",
    "title": "My Commentary Corpus"
}
```

**segments.json:**
```json
{
    "segments": [
        {
            "id": "seg-001",
            "label": "Short label for sidebar",
            "ref_text": "Canonical text being commented on",
            "ref_record": "ann-001",
            "mapped_records": ["ann-001", "ann-002"]
        }
    ]
}
```

**annotations.jsonl** — one annotation per line:
```json
{
    "id": "ann-001",
    "commentator": "Author Name (original script)",
    "commentator_name": "Author Name (display)",
    "era": "Dynasty/Period",
    "life_years": "1130-1200",
    "commentary_type": "注",
    "source": "Source text title",
    "text": "Commentary text",
    "translation_ko": "Translation of commentary"
}
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BESPOKE_DATA_DIR` | `./data` | Data root path |
| `BESPOKE_HOST` | `127.0.0.1` | Server host |
| `BESPOKE_PORT` | `5222` | Server port |

```bash
BESPOKE_DATA_DIR=/path/to/my/data python3 app.py
```

## Project Structure

```
app.py              ← Flask routes
config.py           ← Configuration (env vars)
server/
├── collections.py  ← Auto-discover collections from manifest.json
├── articles.py     ← Article list/detail with pagination
├── threads.py      ← Segments + annotations
├── loader.py       ← JSONL/JSON loading + article normalization
├── cache.py        ← mtime-based in-memory cache
└── safety.py       ← Path traversal prevention
templates/          ← Jinja2 HTML templates
static/             ← CSS + JS (vanilla, no build step)
data/               ← Your collections go here
tests/              ← pytest tests
```

## Tech Stack

- **Backend**: Flask 3.x, Python 3.10+
- **Frontend**: Vanilla JS, CSS (no build step, no framework)
- **Data**: JSON/JSONL direct file reads, mtime cache
- **Dependencies**: `flask`

## License

MIT
