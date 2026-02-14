# Bespoke Corpora

JSONL/JSON 사료 컬렉션을 브라우저에서 열람하는 경량 로컬 웹앱.

원문/번역 병렬 뷰, 주석 스레드 뷰, 페이지네이션, 메타데이터 표시를 지원한다. DB import 없이 JSON 파일을 직접 읽어서 동기화 걱정이 없다.

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/bespoke-corpora.git
cd bespoke-corpora
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
# → http://127.0.0.1:5222
```

`data/` 폴더에 샘플 데이터가 들어 있어서 바로 확인할 수 있다.

## 데이터 넣기

`data/` 아래 두 종류의 데이터를 넣을 수 있다:

### 1. Corpus (`data/corpus/`)

자체 구축한 코퍼스. 두 가지 타입이 있다:

#### Keyword 타입

키워드 검색 결과 등 기사 목록 형태.

```
data/corpus/my-corpus/
├── metadata.json
└── source-a/
    └── articles.jsonl      ← 한 줄에 기사 하나
```

**metadata.json:**
```json
{
    "keyword": "my-keyword",
    "keyword_kr": "내 키워드",
    "total_articles": 100
}
```

**articles.jsonl** (각 줄):
```json
{
    "id": "unique-id",
    "source": "source-name",
    "metadata": {
        "title": "기사 제목",
        "date": {"year": "1800", "month": "3", "day": "15"}
    },
    "original": {
        "paragraphs": ["원문 첫 단락", "원문 둘째 단락"]
    },
    "translation": {
        "paragraphs": ["번역 첫 단락", "번역 둘째 단락"]
    },
    "has_translation": true
}
```

#### Threads 타입

경전 주석처럼 원문 세그먼트에 여러 주석이 달리는 구조.

```
data/corpus/my-commentary/
├── metadata.json
├── canonical_segments.json
└── annotations.jsonl
```

**canonical_segments.json:**
```json
{
    "segments": [
        {
            "id": "seg-001",
            "label": "세그먼트 라벨",
            "jizhu_ref_text": "원문 텍스트",
            "jizhu_record": "ann-001",
            "mapped_records": ["ann-001", "ann-002"]
        }
    ]
}
```

**annotations.jsonl** (각 줄):
```json
{
    "id": "ann-001",
    "commentator": "著者名",
    "commentator_name": "저자명",
    "era": "時代",
    "life_years": "1130-1200",
    "commentary_type": "注",
    "source": "출전",
    "text": "주석 원문",
    "translation_ko": "주석 번역"
}
```

### 2. DB (`data/db/`)

크롤링한 원자료. 소스 > 번들 > articles.json 구조.

```
data/db/
├── MySource/
│   ├── metadata.json        ← optional: {"display_name": "표시 이름"}
│   └── bundle-name/
│       └── articles.json    ← JSON 배열
```

**articles.json:**
```json
[
    {
        "id": "article-001",
        "title": "기사 제목",
        "original": "원문 텍스트\n두 번째 단락",
        "translation": "번역 텍스트\n두 번째 단락",
        "date": {"year": "1800"},
        "source": {"collection": "컬렉션명"},
        "url": "https://원본-URL"
    }
]
```

## 설정

환경변수로 커스터마이징 가능:

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `BESPOKE_DATA_DIR` | `./data` | 데이터 루트 경로 |
| `BESPOKE_HOST` | `127.0.0.1` | 서버 호스트 |
| `BESPOKE_PORT` | `5222` | 서버 포트 |

예시: 다른 위치의 데이터를 쓰고 싶으면
```bash
BESPOKE_DATA_DIR=/path/to/my/data python app.py
```

## 기술 스택

- **Backend**: Flask, Python 3.10+
- **Frontend**: Vanilla JS, CSS
- **Data**: JSON/JSONL 직접 읽기 (DB 없음, mtime 캐시)

## License

MIT
