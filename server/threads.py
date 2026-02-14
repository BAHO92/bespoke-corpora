import config
from server import cache, loader
from server.safety import is_safe_name


def load_data(collection_id):
    if not is_safe_name(collection_id):
        return {'annotations': [], 'segments': []}

    cpath = config.DATA_DIR / collection_id
    ann_path = cpath / 'annotations.jsonl'
    seg_path = cpath / 'segments.json'

    if not ann_path.exists() or not seg_path.exists():
        return {'annotations': [], 'segments': []}

    paths = {str(ann_path): ann_path, str(seg_path): seg_path}

    def _load(p):
        annotations = loader.load_jsonl(ann_path)
        seg_data = loader.load_json(seg_path)
        segments = seg_data.get('segments', []) if seg_data else []
        return {'annotations': annotations, 'segments': segments}

    return cache.get_or_load(f'threads:{collection_id}', paths, _load)


def list_segments(collection_id):
    data = load_data(collection_id)
    annotations = data.get('annotations', [])
    segments = data.get('segments', [])

    ann_by_id = {a['id']: a for a in annotations if 'id' in a}

    enriched = []
    for seg in segments:
        mapped = seg.get('mapped_records', [])
        ref_ann = ann_by_id.get(seg.get('ref_record', '') or seg.get('jizhu_record', ''))
        ref_text_ko = ref_ann.get('ref_text_ko', '') if ref_ann else ''
        enriched.append({
            'id': seg.get('id'),
            'label': seg.get('label'),
            'ref_text': seg.get('ref_text', '') or seg.get('jizhu_ref_text', ''),
            'ref_text_ko': ref_text_ko,
            'annotation_count': len(mapped),
        })

    return {'segments': enriched}


def get_segment(collection_id, segment_id):
    data = load_data(collection_id)
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
    mapped = []
    for rec_id in segment.get('mapped_records', []):
        ann = ann_by_id.get(rec_id)
        if ann:
            mapped.append(ann)

    ref_ann = ann_by_id.get(segment.get('ref_record', '') or segment.get('jizhu_record', ''))
    ref_text_ko = ref_ann.get('ref_text_ko', '') if ref_ann else ''

    return {
        'segment': {
            'id': segment.get('id'),
            'label': segment.get('label'),
            'ref_text': segment.get('ref_text', '') or segment.get('jizhu_ref_text', ''),
            'ref_text_ko': ref_text_ko,
        },
        'annotations': mapped,
    }


def get_annotation(collection_id, annotation_id):
    data = load_data(collection_id)
    for ann in data.get('annotations', []):
        if ann.get('id') == annotation_id:
            return ann
    return None
