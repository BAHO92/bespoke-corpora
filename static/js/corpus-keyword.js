(function () {
    let currentPage = 1;
    const PER_PAGE = 50;

    function route() {
        const hash = location.hash.slice(1);
        if (hash.startsWith('article/')) {
            showArticleDetail(hash.slice('article/'.length));
        } else {
            showArticleList();
        }
    }
    window.addEventListener('hashchange', route);

    async function showArticleList(page) {
        page = page || currentPage;
        const data = await API.get(
            `${API_BASE}/articles?page=${page}&per_page=${PER_PAGE}`
        );
        currentPage = data.page;

        const main = document.getElementById('bespoke-main');
        main.innerHTML = '';

        const info = document.createElement('div');
        info.className = 'bespoke-info';
        info.textContent = `총 ${data.total.toLocaleString()}건 — ${data.page}/${data.pages} 페이지`;
        main.appendChild(info);

        const table = document.createElement('table');
        table.className = 'bespoke-table';
        table.innerHTML =
            '<thead><tr><th>소스</th><th>제목</th><th>날짜</th></tr></thead><tbody></tbody>';
        const tbody = table.querySelector('tbody');

        for (const art of data.results) {
            const tr = document.createElement('tr');
            tr.onclick = function () { location.hash = 'article/' + art.id; };

            const source = art._sub_source || art.source || '';
            const title = (art.metadata && art.metadata.title) || art.id;
            const date = formatDate(art.metadata && art.metadata.date);

            tr.innerHTML =
                '<td><span class="source-badge ' + source + '">' + source + '</span></td>' +
                '<td>' + escHtml(title) + '</td>' +
                '<td>' + escHtml(date) + '</td>';
            tbody.appendChild(tr);
        }
        main.appendChild(table);
        renderPagination(main, data);
    }

    function formatDate(d) {
        if (!d) return '';
        var parts = [];
        if (d.reign) parts.push(d.reign);
        if (d.year) parts.push(d.year + '년');
        if (d.month) parts.push(d.month + '월');
        if (d.day) parts.push(d.day + '일');
        return parts.join(' ');
    }

    function renderPagination(container, data) {
        var div = document.createElement('div');
        div.className = 'bespoke-pagination';

        var prev = document.createElement('button');
        prev.textContent = '← 이전';
        prev.disabled = data.page <= 1;
        prev.onclick = function () { showArticleList(data.page - 1); };

        var info = document.createElement('span');
        info.textContent = data.page + ' / ' + data.pages;

        var next = document.createElement('button');
        next.textContent = '다음 →';
        next.disabled = data.page >= data.pages;
        next.onclick = function () { showArticleList(data.page + 1); };

        div.append(prev, info, next);
        container.appendChild(div);
    }

    async function showArticleDetail(articleId) {
        var art = await API.get(
            `${API_BASE}/articles/${encodeURIComponent(articleId)}`
        );
        var main = document.getElementById('bespoke-main');
        if (art.error) {
            main.innerHTML = '<p class="bespoke-error">기사를 찾을 수 없습니다.</p>';
            return;
        }

        main.innerHTML = '';

        var back = document.createElement('a');
        back.href = '#list';
        back.className = 'bespoke-back';
        back.textContent = '← 목록으로';
        main.appendChild(back);

        main.appendChild(renderMetadataCard(art.metadata));

        var origParas = (art.original && art.original.paragraphs) || [];
        var transParas = (art.translation && art.translation.paragraphs) || [];

        if (art.has_translation && transParas.length) {
            main.appendChild(renderParallelView(origParas, transParas));
        } else {
            main.appendChild(renderFullWidth(origParas));
        }
    }

    function renderMetadataCard(metadata) {
        var details = document.createElement('details');
        details.className = 'bespoke-metadata-card';
        details.open = true;

        var summary = document.createElement('summary');
        summary.className = 'metadata-toggle';
        summary.textContent = 'Metadata';
        details.appendChild(summary);

        var table = document.createElement('table');
        table.className = 'metadata-table';

        flattenMeta(metadata, '').forEach(function (pair) {
            if (pair[1] === null || pair[1] === undefined || pair[1] === '') return;
            var tr = document.createElement('tr');
            tr.innerHTML = '<th>' + escHtml(pair[0]) + '</th><td>' + escHtml(String(pair[1])) + '</td>';
            table.appendChild(tr);
        });

        details.appendChild(table);
        return details;
    }

    function flattenMeta(obj, prefix) {
        var pairs = [];
        if (!obj) return pairs;
        Object.keys(obj).forEach(function (k) {
            var key = prefix ? prefix + '.' + k : k;
            var v = obj[k];
            if (v && typeof v === 'object' && !Array.isArray(v)) {
                pairs = pairs.concat(flattenMeta(v, key));
            } else if (Array.isArray(v)) {
                pairs.push([key, v.join(', ')]);
            } else {
                pairs.push([key, v]);
            }
        });
        return pairs;
    }

    function renderParallelView(origParas, transParas) {
        var container = document.createElement('div');
        container.className = 'bespoke-parallel';

        container.appendChild(buildPanel('원문', 'original-panel', origParas, 'original-paragraph'));
        container.appendChild(buildPanel('번역', 'translation-panel', transParas, 'translation-paragraph'));
        return container;
    }

    function buildPanel(title, panelClass, paragraphs, paraClass) {
        var panel = document.createElement('div');
        panel.className = 'parallel-panel ' + panelClass;
        panel.innerHTML = '<h3>' + title + '</h3>';

        var scroll = document.createElement('div');
        scroll.className = 'parallel-scroll';
        paragraphs.forEach(function (p) {
            if (!p || !p.trim()) return;
            var div = document.createElement('div');
            div.className = 'paragraph ' + paraClass;
            div.textContent = p;
            scroll.appendChild(div);
        });

        panel.appendChild(scroll);
        return panel;
    }

    function renderFullWidth(paragraphs) {
        var container = document.createElement('div');
        container.className = 'bespoke-fullwidth';
        container.innerHTML = '<h3>원문</h3>';
        paragraphs.forEach(function (p) {
            if (!p || !p.trim()) return;
            var div = document.createElement('div');
            div.className = 'paragraph original-paragraph';
            div.textContent = p;
            container.appendChild(div);
        });
        return container;
    }

    function escHtml(s) {
        if (!s) return '';
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    route();
})();
