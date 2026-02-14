from flask import Flask, render_template, jsonify, request
import config
from server import collections, articles, threads
from server.safety import is_safe_name

app = Flask(__name__)


@app.context_processor
def inject_globals():
    import time
    return {'v': int(time.time())}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/c/<collection_id>/')
def collection_view(collection_id):
    if not is_safe_name(collection_id):
        return jsonify({'error': 'invalid collection name'}), 400
    ctype = collections.get_type(collection_id)
    if ctype == 'articles':
        return render_template('articles.html', collection_id=collection_id)
    elif ctype == 'threads':
        return render_template('threads.html', collection_id=collection_id)
    return jsonify({'error': 'collection not found'}), 404


@app.route('/api/collections')
def api_collections():
    return jsonify(collections.discover())


@app.route('/api/c/<collection_id>/manifest')
def api_manifest(collection_id):
    manifest = collections.get_manifest(collection_id)
    if not manifest:
        return jsonify({'error': 'not found'}), 404
    return jsonify(manifest)


@app.route('/api/c/<collection_id>/articles')
def api_articles(collection_id):
    if not is_safe_name(collection_id):
        return jsonify({'error': 'invalid name'}), 400
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    return jsonify(articles.list_articles(collection_id, page, per_page))


@app.route('/api/c/<collection_id>/articles/<path:article_id>')
def api_article(collection_id, article_id):
    if not is_safe_name(collection_id):
        return jsonify({'error': 'invalid name'}), 400
    art = articles.get_article(collection_id, article_id)
    if not art:
        return jsonify({'error': 'not found'}), 404
    return jsonify(art)


@app.route('/api/c/<collection_id>/segments')
def api_segments(collection_id):
    if not is_safe_name(collection_id):
        return jsonify({'error': 'invalid name'}), 400
    return jsonify(threads.list_segments(collection_id))


@app.route('/api/c/<collection_id>/segments/<segment_id>')
def api_segment(collection_id, segment_id):
    if not is_safe_name(collection_id):
        return jsonify({'error': 'invalid name'}), 400
    result = threads.get_segment(collection_id, segment_id)
    if not result:
        return jsonify({'error': 'not found'}), 404
    return jsonify(result)


@app.route('/api/c/<collection_id>/annotations/<annotation_id>')
def api_annotation(collection_id, annotation_id):
    if not is_safe_name(collection_id):
        return jsonify({'error': 'invalid name'}), 400
    ann = threads.get_annotation(collection_id, annotation_id)
    if not ann:
        return jsonify({'error': 'not found'}), 404
    return jsonify(ann)


if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=True)
