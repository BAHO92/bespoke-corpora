import json
import logging
from pathlib import Path

import config
from server.safety import is_safe_name

logger = logging.getLogger(__name__)


def discover():
    data_dir = config.DATA_DIR
    if not data_dir.exists():
        return []

    results = []
    for d in sorted(data_dir.iterdir()):
        if not d.is_dir() or d.name.startswith('.'):
            continue

        manifest = _read_manifest(d)
        if not manifest:
            continue

        ctype = manifest.get('type', 'articles')
        results.append({
            'id': d.name,
            'type': ctype,
            'title': manifest.get('title', d.name),
            'description': manifest.get('description', ''),
            'record_count': _count_records(d, ctype, manifest),
        })

    return results


def get_type(collection_id):
    if not is_safe_name(collection_id):
        return None
    cpath = config.DATA_DIR / collection_id
    if not cpath.is_dir():
        return None
    manifest = _read_manifest(cpath)
    if not manifest:
        return None
    return manifest.get('type', 'articles')


def get_manifest(collection_id):
    if not is_safe_name(collection_id):
        return None
    cpath = config.DATA_DIR / collection_id
    if not cpath.is_dir():
        return None
    return _read_manifest(cpath)


def _read_manifest(cpath):
    manifest_path = cpath / 'manifest.json'
    if not manifest_path.exists():
        return None
    try:
        return json.loads(manifest_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning('Bad manifest in %s: %s', cpath.name, e)
        return None


def _count_records(cpath, ctype, manifest):
    count = manifest.get('record_count', 0)
    if count:
        return count

    if ctype == 'articles':
        jsonl = cpath / 'articles.jsonl'
        if jsonl.exists():
            try:
                return sum(1 for line in open(jsonl, encoding='utf-8') if line.strip())
            except OSError:
                return 0
        json_file = cpath / 'articles.json'
        if json_file.exists():
            try:
                data = json.loads(json_file.read_text(encoding='utf-8'))
                return len(data) if isinstance(data, list) else 0
            except (json.JSONDecodeError, OSError):
                return 0

    if ctype == 'threads':
        ann = cpath / 'annotations.jsonl'
        if ann.exists():
            try:
                return sum(1 for line in open(ann, encoding='utf-8') if line.strip())
            except OSError:
                return 0

    return 0
