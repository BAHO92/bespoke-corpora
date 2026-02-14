import math

import config
from server import cache, loader
from server.safety import is_safe_name


def load_all(collection_id):
    if not is_safe_name(collection_id):
        return []

    cpath = config.DATA_DIR / collection_id
    jsonl_path = cpath / 'articles.jsonl'
    json_path = cpath / 'articles.json'

    if jsonl_path.exists():
        paths = {str(jsonl_path): jsonl_path}
        return cache.get_or_load(
            f'articles:{collection_id}',
            paths,
            lambda p: [loader.normalize_article(a) for a in loader.load_jsonl(jsonl_path)],
        )

    if json_path.exists():
        paths = {str(json_path): json_path}
        return cache.get_or_load(
            f'articles:{collection_id}',
            paths,
            lambda p: [loader.normalize_article(a) for a in (loader.load_json(json_path) or [])],
        )

    return []


def list_articles(collection_id, page=1, per_page=50):
    articles = load_all(collection_id)
    total = len(articles)
    pages = max(1, math.ceil(total / per_page))
    page = max(1, min(page, pages))
    start = (page - 1) * per_page

    results = []
    for art in articles[start:start + per_page]:
        results.append({
            'id': art.get('id'),
            'metadata': art.get('metadata'),
            'has_translation': art.get('has_translation', False),
        })

    return {
        'results': results,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages,
    }


def get_article(collection_id, article_id):
    for art in load_all(collection_id):
        if art.get('id') == article_id:
            return art
    return None
