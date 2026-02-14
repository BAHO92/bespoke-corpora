import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_jsonl(filepath):
    results = []
    filepath = Path(filepath)
    try:
        with open(filepath, encoding='utf-8') as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning('Bad JSONL line %d in %s: %s', lineno, filepath.name, e)
    except OSError as e:
        logger.warning('Cannot read %s: %s', filepath, e)
    return results


def load_json(filepath):
    filepath = Path(filepath)
    try:
        data = json.loads(filepath.read_text(encoding='utf-8'))
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.warning('Cannot read %s: %s', filepath, e)
        return None


def normalize_article(art):
    original = art.get('original', '')
    if isinstance(original, str):
        art['original'] = {
            'paragraphs': [p for p in original.split('\n') if p.strip()]
        } if original else {'paragraphs': []}

    translation = art.get('translation', '')
    if isinstance(translation, str):
        art['translation'] = {
            'paragraphs': [p for p in translation.split('\n') if p.strip()]
        } if translation else {'paragraphs': []}

    if 'has_translation' not in art:
        trans = art.get('translation', {})
        art['has_translation'] = bool(
            trans.get('paragraphs') if isinstance(trans, dict) else trans
        )

    if 'metadata' not in art:
        meta = {}
        for key in ('title', 'title_ko', 'date', 'author', 'source', 'category'):
            val = art.get(key)
            if val:
                meta[key] = val
        if not meta.get('title'):
            meta['title'] = art.get('id', '')
        art['metadata'] = meta

    return art
