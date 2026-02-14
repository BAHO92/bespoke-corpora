"""Corpus service layer — unified CORPUS + DB browsing.

JSONL/JSON loading, memory caching, auto-discovery for both
CORPUS/ (keyword, threads) and DB/ (any JSON source collection).
"""

import json
import logging
import math
from pathlib import Path

import config

logger = logging.getLogger(__name__)

_cache = {}


def discover_corpora():
    """Auto-discover corpora in CORPUS/ directory."""
    corpus_dir = config.CORPUS_DIR
    if not corpus_dir.exists():
        return []

    results = []
    for meta_path in sorted(corpus_dir.glob('*/metadata.json')):
        dirname = meta_path.parent.name
        if dirname.startswith('.') or '.backup' in dirname:
            continue
        try:
            metadata = json.loads(meta_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning('Failed to read %s: %s', meta_path, e)
            continue

        corpus_type = _detect_type(meta_path.parent)
        record_count = _count_records(meta_path.parent, corpus_type, metadata)
        display_name = _get_display_name(metadata, dirname)

        results.append({
            'name': dirname,
            'type': corpus_type,
            'display_name': display_name,
            'record_count': record_count,
        })

    return results


def get_corpus_metadata(corpus_name):
    """Read metadata.json for a corpus."""
    meta_path = config.CORPUS_DIR / corpus_name / 'metadata.json'
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return None


def get_corpus_type(corpus_name):
    """Determine corpus type: 'keyword', 'threads', or 'unknown'."""
    corpus_path = config.CORPUS_DIR / corpus_name
    if not corpus_path.exists():
        return 'unknown'
    return _detect_type(corpus_path)


# ---------------------------------------------------------------------------
# Keyword corpus
# ---------------------------------------------------------------------------

def load_keyword_articles(corpus_name):
    """Load all keyword articles (sillok + sjw merged). Cached by file mtime."""
    corpus_path = config.CORPUS_DIR / corpus_name
    jsonl_files = _find_keyword_jsonl_files(corpus_path)
    if not jsonl_files:
        return []

    cache_key = f'keyword:{corpus_name}'
    return _get_cached_multi(cache_key, jsonl_files, _load_keyword_from_files)


def list_keyword_articles(corpus_name, page=1, per_page=50):
    """Paginated keyword article list (lightweight, no paragraphs)."""
    articles = load_keyword_articles(corpus_name)
    total = len(articles)
    pages = max(1, math.ceil(total / per_page))
    page = max(1, min(page, pages))
    start = (page - 1) * per_page
    end = start + per_page

    results = []
    for art in articles[start:end]:
        results.append({
            'id': art.get('id'),
            'source': art.get('source'),
            'metadata': art.get('metadata'),
            'has_translation': art.get('has_translation', False),
            '_sub_source': art.get('_sub_source'),
        })

    return {
        'results': results,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages,
    }


def get_keyword_article(corpus_name, article_id):
    """Single keyword article by id. Returns full dict or None."""
    articles = load_keyword_articles(corpus_name)
    for art in articles:
        if art.get('id') == article_id:
            return art
    return None


# ---------------------------------------------------------------------------
# Threads corpus
# ---------------------------------------------------------------------------

def load_thread_data(corpus_name):
    """Load annotations + canonical_segments. Cached."""
    corpus_path = config.CORPUS_DIR / corpus_name
    ann_path = corpus_path / 'annotations.jsonl'
    seg_path = corpus_path / 'canonical_segments.json'

    if not ann_path.exists() or not seg_path.exists():
        return {'annotations': [], 'segments': []}

    cache_key = f'threads:{corpus_name}'
    files = {str(ann_path): ann_path, str(seg_path): seg_path}

    def loader(file_map):
        annotations = _load_jsonl(ann_path)
        segments_data = json.loads(seg_path.read_text(encoding='utf-8'))
        segments = segments_data.get('segments', [])
        return {'annotations': annotations, 'segments': segments}

    return _get_cached_multi(cache_key, files, loader)


def get_thread_segments(corpus_name):
    """Return canonical segments with annotation counts."""
    data = load_thread_data(corpus_name)
    annotations = data.get('annotations', [])
    segments = data.get('segments', [])

    ann_by_id = {a['id']: a for a in annotations if 'id' in a}

    enriched = []
    for seg in segments:
        mapped = seg.get('mapped_records', [])
        jizhu_ann = ann_by_id.get(seg.get('jizhu_record', ''))
        ref_text_ko = jizhu_ann.get('ref_text_ko', '') if jizhu_ann else ''
        enriched.append({
            'id': seg.get('id'),
            'label': seg.get('label'),
            'jizhu_ref_text': seg.get('jizhu_ref_text'),
            'ref_text_ko': ref_text_ko,
            'annotation_count': len(mapped),
        })

    return {'segments': enriched}


def get_thread_segment_annotations(corpus_name, segment_id):
    """Return segment info + its mapped annotations."""
    data = load_thread_data(corpus_name)
    annotations = data.get('annotations', [])
    segments = data.get('segments', [])

    segment = None
    for seg in segments:
        if seg.get('id') == segment_id:
            segment = seg
            break

    if not segment:
        return None

    ann_by_id = {a['id']: a for a in annotations if 'id' in a}
    mapped_annotations = []
    for rec_id in segment.get('mapped_records', []):
        ann = ann_by_id.get(rec_id)
        if ann:
            mapped_annotations.append(ann)

    jizhu_ann = ann_by_id.get(segment.get('jizhu_record', ''))
    ref_text_ko = jizhu_ann.get('ref_text_ko', '') if jizhu_ann else ''

    return {
        'segment': {
            'id': segment.get('id'),
            'label': segment.get('label'),
            'jizhu_ref_text': segment.get('jizhu_ref_text'),
            'ref_text_ko': ref_text_ko,
        },
        'annotations': mapped_annotations,
    }


def get_thread_annotation(corpus_name, annotation_id):
    """Single annotation by id."""
    data = load_thread_data(corpus_name)
    for ann in data.get('annotations', []):
        if ann.get('id') == annotation_id:
            return ann
    return None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _detect_type(corpus_path):
    """Detect corpus type from directory contents."""
    if (corpus_path / 'annotations.jsonl').exists() and \
       (corpus_path / 'canonical_segments.json').exists():
        return 'threads'
    if list(corpus_path.glob('*/articles.jsonl')):
        return 'keyword'
    return 'unknown'


def _count_records(corpus_path, corpus_type, metadata):
    """Count records from metadata or by scanning files."""
    if corpus_type == 'keyword':
        return metadata.get('total_articles', 0)
    if corpus_type == 'threads':
        ann_path = corpus_path / 'annotations.jsonl'
        if ann_path.exists():
            try:
                return sum(1 for line in open(ann_path, encoding='utf-8') if line.strip())
            except OSError:
                return 0
    return 0


def _get_display_name(metadata, dirname):
    """Extract display name from metadata or use dirname."""
    if 'keyword' in metadata:
        kw = metadata['keyword']
        kr = metadata.get('keyword_kr', '')
        return f'{kw} ({kr})' if kr else kw
    if 'corpus' in metadata:
        chapter = metadata.get('chapter_title', '')
        if chapter:
            return f"{metadata['corpus']} — {chapter}"
        return metadata['corpus']
    return dirname


def _load_jsonl(filepath):
    """Parse JSONL, skip malformed lines."""
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
                    logger.warning('Malformed JSONL line %d in %s: %s', lineno, filepath.name, e)
    except OSError as e:
        logger.warning('Failed to read %s: %s', filepath, e)
    return results


def _find_keyword_jsonl_files(corpus_path):
    """Find all articles.jsonl files under corpus subdirs."""
    files = {}
    for jsonl_path in sorted(corpus_path.glob('*/articles.jsonl')):
        sub_source = jsonl_path.parent.name
        if sub_source.startswith('.') or '.backup' in sub_source:
            continue
        files[sub_source] = jsonl_path
    return files


def _load_keyword_from_files(file_map):
    """Load keyword articles from multiple sub-source JSONL files."""
    all_articles = []
    for sub_source, filepath in file_map.items():
        articles = _load_jsonl(filepath)
        for art in articles:
            art['_sub_source'] = sub_source
        all_articles.extend(articles)
    return all_articles


def _get_cached_multi(cache_key, files, loader):
    """Cache-or-load with multi-file mtime checking.

    files: dict {key: Path} for keyword, or similar mapping
    loader: callable(files) -> data
    """
    current_mtimes = {}
    for key, filepath in files.items():
        filepath = Path(filepath)
        try:
            current_mtimes[str(filepath)] = filepath.stat().st_mtime
        except OSError:
            current_mtimes[str(filepath)] = 0

    cached = _cache.get(cache_key)
    if cached and cached.get('mtimes') == current_mtimes:
        return cached['data']

    data = loader(files)
    _cache[cache_key] = {'mtimes': current_mtimes, 'data': data}
    return data


def _get_cached_single(cache_key, filepath):
    filepath = Path(filepath)
    try:
        mtime = filepath.stat().st_mtime
    except OSError:
        return None

    cached = _cache.get(cache_key)
    if cached and cached.get('mtime') == mtime:
        return cached['data']

    try:
        data = json.loads(filepath.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning('Failed to read %s: %s', filepath, e)
        return None

    _cache[cache_key] = {'mtime': mtime, 'data': data}
    return data


# ---------------------------------------------------------------------------
# DB source browsing
# ---------------------------------------------------------------------------

def get_db_source_info(source_key):
    db_root = config.DB_ROOT
    source_path = db_root / source_key
    if not source_path.is_dir():
        return None
    meta_path = source_path / 'metadata.json'
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            return {'name': meta.get('display_name', source_key)}
        except (json.JSONDecodeError, OSError):
            pass
    return {'name': source_key}


def discover_db_sources():
    db_root = config.DB_ROOT
    if not db_root.exists():
        return []

    results = []
    for source_path in sorted(db_root.iterdir()):
        if not source_path.is_dir() or source_path.name.startswith(('_', '.')):
            continue

        source_key = source_path.name
        source_info = get_db_source_info(source_key) or {'name': source_key}

        bundles = []
        for d in sorted(source_path.iterdir()):
            if not d.is_dir() or d.name.startswith('_') or d.name.startswith('.'):
                continue
            articles_path = d / 'articles.json'
            if not articles_path.exists():
                continue

            meta_path = d / 'metadata.json'
            article_count = 0
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding='utf-8'))
                    article_count = meta.get('total_articles', 0) or meta.get('article_count', 0) or 0
                except (json.JSONDecodeError, OSError):
                    pass
            if not article_count:
                cache_key = f'db:{source_key}:{d.name}'
                data = _get_cached_single(cache_key, articles_path)
                article_count = len(data) if data else 0

            bundles.append({
                'name': d.name,
                'article_count': article_count,
            })

        if bundles:
            results.append({
                'source': source_key,
                'display_name': source_info['name'],
                'bundles': bundles,
                'total_articles': sum(b['article_count'] for b in bundles),
            })

    return results


def discover_all():
    return {
        'corpora': discover_corpora(),
        'db_sources': discover_db_sources(),
    }


def _load_db_articles(source, bundle):
    articles_path = config.DB_ROOT / source / bundle / 'articles.json'
    cache_key = f'db:{source}:{bundle}'
    return _get_cached_single(cache_key, articles_path) or []


def list_db_articles(source, bundle, page=1, per_page=50):
    articles = _load_db_articles(source, bundle)
    total = len(articles)
    pages = max(1, math.ceil(total / per_page))
    page = max(1, min(page, pages))
    start = (page - 1) * per_page
    end = start + per_page

    results = []
    for art in articles[start:end]:
        results.append(_normalize_db_article_for_list(art, source))

    return {
        'results': results,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages,
    }


def get_db_article(source, bundle, article_id):
    articles = _load_db_articles(source, bundle)
    for art in articles:
        if art.get('id') == article_id:
            return _normalize_db_article_for_detail(art, source)
    return None


def _normalize_db_article_for_list(art, source_type):
    metadata = _build_db_metadata(art, source_type)
    return {
        'id': art.get('id', ''),
        'source': source_type,
        'metadata': metadata,
        'has_translation': bool(art.get('translation', '') or art.get('has_translation', False)),
    }


def _normalize_db_article_for_detail(art, source_type):
    result = _normalize_db_article_for_list(art, source_type)

    orig_text = art.get('original', '')
    trans_text = art.get('translation', '')

    result['original'] = {
        'paragraphs': [p for p in orig_text.split('\n') if p.strip()] if orig_text else []
    }
    result['translation'] = {
        'paragraphs': [p for p in trans_text.split('\n') if p.strip()] if trans_text else []
    }
    result['url'] = art.get('url', '')

    footnotes = art.get('footnotes')
    if footnotes:
        result['footnotes'] = footnotes

    return result


def _build_db_metadata(art, source_type):
    metadata = {}
    metadata['title'] = art.get('title_ko') or art.get('title', art.get('id', ''))

    if art.get('title') and art.get('title') != metadata['title']:
        metadata['title_original'] = art['title']
    if art.get('date'):
        metadata['date'] = art['date']

    author = art.get('author')
    if isinstance(author, dict):
        metadata['author'] = author.get('name', '')
    elif isinstance(author, str) and author:
        metadata['author'] = author

    source = art.get('source')
    if isinstance(source, dict):
        for k, v in source.items():
            if v:
                metadata[k] = v

    if art.get('category'):
        metadata['category'] = art['category']

    return metadata
