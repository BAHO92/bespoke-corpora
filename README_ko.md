# Bespoke Corpora

[English](README.md) | **한국어**

연구자가 직접 구축한 코퍼스(JSON/JSONL)를 브라우저에서 열람하는 로컬 웹앱.

원문과 번역을 나란히 읽고, 메타데이터를 훑고, **threads** — 하나의 원전 텍스트에 여러 주석가의 해설이 달리는 구조 — 를 탐색할 수 있습니다. 의도적으로 단순하게 만들었고, 포크해서 자기 프로젝트에 맞게 고쳐 쓰는 것을 전제합니다.

## 이 앱이 하는 일

- 원문/번역 병렬 뷰로 기사(article) 컬렉션 열람
- 주석 스레드 탐색 (원전 텍스트 + 주석가별 카드)
- `data/` 디렉토리에서 컬렉션 자동 탐지
- 대규모 컬렉션 페이지네이션, 메타데이터 표시
- 파일 수정시각(mtime) 기반 인메모리 캐시 — DB 없음, 동기화 없음

## 이 앱이 하지 않는 일

- 데이터 크롤링·스크래핑 (데이터는 직접 준비)
- 전문검색(full-text search)·인덱싱
- 다중 사용자 인증·호스팅
- 주석 작성·편집 워크플로
- 데이터 버전 관리

## 빠른 시작

### Claude Code로 설치 + 실행 (가장 쉬움)

1. 터미널을 열고 `claude`를 실행하세요.
2. Claude에게 이렇게 요청하세요:

```
https://github.com/BAHO92/bespoke-corpora.git 클론하고, 폴더로 들어가서 bash run.sh로 실행해줘
```

`run.sh`가 Python 환경 설치, 의존성 설치, 서버 실행, 브라우저 열기를 자동으로 처리합니다. 샘플 데이터가 포함되어 있어 바로 화면을 확인할 수 있습니다.

종료하려면 터미널에서 `Ctrl+C`를 누르세요.

<details>
<summary>Claude 없이 직접 실행</summary>

터미널에 아래 세 줄을 한꺼번에 붙여넣으세요:

```bash
git clone https://github.com/BAHO92/bespoke-corpora.git
cd bespoke-corpora
bash run.sh
```

</details>

### 다음부터 실행할 때

`bespoke-corpora` 폴더에서:

```bash
bash run.sh
```

<details>
<summary>(선택) 어디서든 bespoke 한 마디로 실행하기</summary>

`~/.zshrc` (또는 `~/.bashrc`)에 추가:

```bash
alias bespoke='bash ~/bespoke-corpora/run.sh'
```

터미널을 재시작한 뒤 `bespoke`만 입력하면 실행됩니다.

</details>

## 데이터 포맷

모든 컬렉션은 `data/` 안에 둡니다. 각 컬렉션은 `manifest.json`이 있는 디렉토리입니다.

### Articles 컬렉션

원문과 선택적 번역이 포함된 기사 목록.

```
data/my-collection/
├── manifest.json
└── articles.jsonl
```

**manifest.json:**
```json
{
    "type": "articles",
    "title": "내 컬렉션"
}
```

**articles.jsonl** — 한 줄에 기사 하나:
```json
{
    "id": "고유-id",
    "metadata": { "title": "기사 제목", "date": {"year": "1800"} },
    "original": { "paragraphs": ["첫째 단락", "둘째 단락"] },
    "translation": { "paragraphs": ["First paragraph", "Second paragraph"] },
    "has_translation": true
}
```

**유연한 입력:** `original`과 `translation`은 `{"paragraphs": [...]}` 형태뿐 아니라 일반 문자열도 받습니다 (줄바꿈 `\n` 기준 자동 분리).

JSONL 대신 `articles.json` (JSON 배열)도 사용 가능합니다.

### Threads 컬렉션

원전 텍스트 세그먼트에 여러 주석가의 해설이 매핑되는 구조 — 주석사(commentary tradition) 모델링용.

```
data/my-commentary/
├── manifest.json
├── segments.json
└── annotations.jsonl
```

**manifest.json:**
```json
{
    "type": "threads",
    "title": "내 주석 코퍼스"
}
```

**segments.json:**
```json
{
    "segments": [
        {
            "id": "seg-001",
            "label": "사이드바용 짧은 라벨",
            "ref_text": "주석 대상 원전 텍스트",
            "ref_record": "ann-001",
            "mapped_records": ["ann-001", "ann-002"]
        }
    ]
}
```

**annotations.jsonl** — 한 줄에 주석 하나:
```json
{
    "id": "ann-001",
    "commentator": "저자명 (원어)",
    "commentator_name": "저자명 (표시용)",
    "era": "시대/왕조",
    "life_years": "1130-1200",
    "commentary_type": "注",
    "source": "출전",
    "text": "주석 본문",
    "translation_ko": "주석 번역"
}
```

## 설정

| 환경변수 | 기본값 | 설명 |
|----------|--------|------|
| `BESPOKE_DATA_DIR` | `./data` | 데이터 루트 경로 |
| `BESPOKE_HOST` | `127.0.0.1` | 서버 호스트 |
| `BESPOKE_PORT` | `5222` | 서버 포트 |

```bash
BESPOKE_DATA_DIR=/path/to/my/data python3 app.py
```

## 프로젝트 구조

```
app.py              ← Flask 라우트
config.py           ← 설정 (환경변수)
server/
├── collections.py  ← manifest.json 기반 컬렉션 자동 탐지
├── articles.py     ← 기사 목록/상세 + 페이지네이션
├── threads.py      ← 세그먼트 + 주석
├── loader.py       ← JSONL/JSON 로딩 + 기사 정규화
├── cache.py        ← mtime 기반 인메모리 캐시
└── safety.py       ← 경로 탐색(path traversal) 방지
templates/          ← Jinja2 HTML 템플릿
static/             ← CSS + JS (빌드 없음, 프레임워크 없음)
data/               ← 컬렉션을 여기에 넣으세요
tests/              ← pytest 테스트
```

## 기술 스택

- **백엔드**: Flask 3.x, Python 3.10+
- **프론트엔드**: Vanilla JS, CSS (빌드 스텝 없음, 프레임워크 없음)
- **데이터**: JSON/JSONL 직접 파일 읽기, mtime 캐시
- **의존성**: `flask`

## 라이선스

MIT
