import json
import tempfile
from pathlib import Path

from server.loader import load_jsonl, load_json, normalize_article


def test_load_jsonl_valid():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write('{"id": "a"}\n')
        f.write('{"id": "b"}\n')
        f.flush()
        result = load_jsonl(f.name)
    assert len(result) == 2
    assert result[0]['id'] == 'a'


def test_load_jsonl_skips_bad_lines():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write('{"id": "good"}\n')
        f.write('not json\n')
        f.write('{"id": "also-good"}\n')
        f.flush()
        result = load_jsonl(f.name)
    assert len(result) == 2


def test_load_jsonl_skips_blank_lines():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write('{"id": "a"}\n\n\n{"id": "b"}\n')
        f.flush()
        result = load_jsonl(f.name)
    assert len(result) == 2


def test_load_json_array():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([{"id": "x"}, {"id": "y"}], f)
        f.flush()
        result = load_json(f.name)
    assert isinstance(result, list)
    assert len(result) == 2


def test_load_json_missing_file():
    result = load_json('/nonexistent/path.json')
    assert result is None


def test_normalize_string_original():
    art = {'id': 'test', 'original': 'line1\nline2\n\nline3'}
    normalized = normalize_article(art)
    assert normalized['original'] == {'paragraphs': ['line1', 'line2', 'line3']}


def test_normalize_keeps_dict_original():
    art = {'id': 'test', 'original': {'paragraphs': ['already', 'structured']}}
    normalized = normalize_article(art)
    assert normalized['original'] == {'paragraphs': ['already', 'structured']}


def test_normalize_derives_has_translation():
    art = {'id': 'test', 'original': 'text', 'translation': 'trans'}
    normalized = normalize_article(art)
    assert normalized['has_translation'] is True


def test_normalize_no_translation():
    art = {'id': 'test', 'original': 'text'}
    normalized = normalize_article(art)
    assert normalized['has_translation'] is False


def test_normalize_builds_metadata():
    art = {'id': 'test', 'title': 'My Title', 'date': {'year': '1800'}, 'original': ''}
    normalized = normalize_article(art)
    assert normalized['metadata']['title'] == 'My Title'
    assert normalized['metadata']['date'] == {'year': '1800'}


def test_normalize_preserves_existing_metadata():
    art = {'id': 'test', 'metadata': {'title': 'Explicit'}, 'original': ''}
    normalized = normalize_article(art)
    assert normalized['metadata']['title'] == 'Explicit'
