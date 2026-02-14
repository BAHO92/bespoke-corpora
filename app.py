from flask import Flask, render_template, jsonify, request
import config
from server import corpus_service

app = Flask(__name__)


@app.context_processor
def inject_globals():
    import time
    return {'v': int(time.time())}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/corpus/')
def corpus_index():
    return render_template('corpus_index.html')


@app.route('/corpus/<corpus_name>/')
def corpus_view(corpus_name):
    corpus_type = corpus_service.get_corpus_type(corpus_name)
    if corpus_type == 'keyword':
        return render_template('corpus_keyword.html', corpus_name=corpus_name)
    elif corpus_type == 'threads':
        return render_template('corpus_threads.html', corpus_name=corpus_name)
    return jsonify({'error': 'unknown corpus type'}), 404


@app.route('/db/<source>/<bundle>/')
def db_bundle_view(source, bundle):
    source_info = corpus_service.get_db_source_info(source)
    if not source_info:
        return jsonify({'error': 'unknown source'}), 404
    return render_template('db_bundle.html', source=source, bundle=bundle,
                           source_name=source_info['name'])


@app.route('/api/collections')
def api_collections():
    return jsonify(corpus_service.discover_all())


@app.route('/api/corpus/corpora')
def api_corpus_corpora():
    return jsonify(corpus_service.discover_corpora())


@app.route('/api/corpus/<corpus_name>/metadata')
def api_corpus_metadata(corpus_name):
    meta = corpus_service.get_corpus_metadata(corpus_name)
    if not meta:
        return jsonify({'error': 'not found'}), 404
    return jsonify(meta)


@app.route('/api/corpus/<corpus_name>/articles')
def api_corpus_articles(corpus_name):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    return jsonify(corpus_service.list_keyword_articles(corpus_name, page, per_page))


@app.route('/api/corpus/<corpus_name>/articles/<article_id>')
def api_corpus_article(corpus_name, article_id):
    art = corpus_service.get_keyword_article(corpus_name, article_id)
    if not art:
        return jsonify({'error': 'not found'}), 404
    return jsonify(art)


@app.route('/api/corpus/<corpus_name>/segments')
def api_corpus_segments(corpus_name):
    return jsonify(corpus_service.get_thread_segments(corpus_name))


@app.route('/api/corpus/<corpus_name>/segments/<segment_id>')
def api_corpus_segment(corpus_name, segment_id):
    result = corpus_service.get_thread_segment_annotations(corpus_name, segment_id)
    if not result:
        return jsonify({'error': 'not found'}), 404
    return jsonify(result)


@app.route('/api/corpus/<corpus_name>/annotations/<annotation_id>')
def api_corpus_annotation(corpus_name, annotation_id):
    ann = corpus_service.get_thread_annotation(corpus_name, annotation_id)
    if not ann:
        return jsonify({'error': 'not found'}), 404
    return jsonify(ann)


@app.route('/api/db/sources')
def api_db_sources():
    return jsonify(corpus_service.discover_db_sources())


@app.route('/api/db/<source>/<bundle>/articles')
def api_db_articles(source, bundle):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    return jsonify(corpus_service.list_db_articles(source, bundle, page, per_page))


@app.route('/api/db/<source>/<bundle>/articles/<path:article_id>')
def api_db_article(source, bundle, article_id):
    art = corpus_service.get_db_article(source, bundle, article_id)
    if not art:
        return jsonify({'error': 'not found'}), 404
    return jsonify(art)


if __name__ == '__main__':
    app.run(host=config.HOST, port=config.VAULT_PORT, debug=True)
