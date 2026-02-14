(function () {
    var segmentsData = null;
    var activeSegmentId = null;

    async function init() {
        var data = await API.get(API_BASE + '/segments');
        segmentsData = data.segments;
        renderSegmentIndex(segmentsData);

        if (segmentsData.length > 0) {
            loadSegment(segmentsData[0].id);
        }
    }

    function renderSegmentIndex(segments) {
        var sidebar = document.getElementById('segment-index');
        sidebar.innerHTML = '<h2>세그먼트</h2>';

        var list = document.createElement('ul');
        list.className = 'segment-list';

        segments.forEach(function (seg) {
            var li = document.createElement('li');
            li.className = 'segment-item';
            li.dataset.segId = seg.id;
            li.onclick = function () { loadSegment(seg.id); };

            var label = document.createElement('span');
            label.className = 'segment-label';
            var labelText = seg.label || seg.id;
            label.textContent = labelText.length > 30 ? labelText.slice(0, 30) + '…' : labelText;
            label.title = labelText;

            var count = document.createElement('span');
            count.className = 'segment-count';
            count.textContent = seg.annotation_count;

            li.append(label, count);
            list.appendChild(li);
        });

        sidebar.appendChild(list);
    }

    async function loadSegment(segmentId) {
        activeSegmentId = segmentId;

        document.querySelectorAll('.segment-item').forEach(function (li) {
            li.classList.toggle('active', li.dataset.segId === segmentId);
        });

        var data = await API.get(
            API_BASE + '/segments/' + encodeURIComponent(segmentId)
        );
        if (data.error) {
            document.getElementById('threads-main').innerHTML =
                '<p class="bespoke-error">세그먼트를 찾을 수 없습니다.</p>';
            return;
        }

        renderSegmentDetail(data);
    }

    function renderSegmentDetail(data) {
        var main = document.getElementById('threads-main');
        main.innerHTML = '';

        var segment = data.segment;
        var annotations = data.annotations;

        var header = document.createElement('div');
        header.className = 'segment-header';

        var badge = document.createElement('span');
        badge.className = 'segment-id-badge';
        badge.textContent = segment.id;

        var refText = document.createElement('div');
        refText.className = 'segment-ref-text';
        refText.textContent = segment.ref_text || segment.label || '';

        header.append(badge, refText);

        if (segment.ref_text_ko) {
            var refKo = document.createElement('div');
            refKo.className = 'segment-ref-ko';
            refKo.textContent = segment.ref_text_ko;
            header.appendChild(refKo);
        }
        main.appendChild(header);

        if (!annotations.length) {
            var empty = document.createElement('p');
            empty.className = 'bespoke-error';
            empty.textContent = '이 세그먼트에 주석이 없습니다.';
            main.appendChild(empty);
            return;
        }

        var container = document.createElement('div');
        container.className = 'annotations-container';

        annotations.forEach(function (ann) {
            container.appendChild(renderAnnotationCard(ann));
        });

        main.appendChild(container);
    }

    function renderAnnotationCard(ann) {
        var card = document.createElement('div');
        card.className = 'annotation-card';

        var cardHeader = document.createElement('div');
        cardHeader.className = 'annotation-header';

        var tag = document.createElement('span');
        tag.className = 'commentator-tag';
        var nameHtml = '<strong>' + esc(ann.commentator_name || ann.commentator) + '</strong>';
        if (ann.era) nameHtml += ' <span class="era-tag">' + esc(ann.era) + '</span>';
        if (ann.life_years) nameHtml += ' <span class="life-years">' + esc(ann.life_years) + '</span>';
        tag.innerHTML = nameHtml;

        var typeBadge = document.createElement('span');
        typeBadge.className = 'commentary-type-badge type-' + getTypeClass(ann.commentary_type);
        typeBadge.textContent = ann.commentary_type || '';

        cardHeader.append(tag, typeBadge);
        card.appendChild(cardHeader);

        if (ann.source) {
            var src = document.createElement('div');
            src.className = 'annotation-source';
            src.textContent = ann.source;
            card.appendChild(src);
        }

        var text = document.createElement('div');
        text.className = 'annotation-text';
        text.textContent = ann.text || '';
        card.appendChild(text);

        if (ann.translation_ko) {
            var trans = document.createElement('div');
            trans.className = 'annotation-translation';
            trans.textContent = ann.translation_ko;
            card.appendChild(trans);
        }

        return card;
    }

    function getTypeClass(type) {
        var map = { '注': 'zhu', '疏': 'shu', '集注': 'jizhu', '大全': 'daquan' };
        return map[type] || 'other';
    }

    function esc(s) {
        if (!s) return '';
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    init();
})();
