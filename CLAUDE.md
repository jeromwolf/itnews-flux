# Claude 작업 가이드라인

**프로젝트**: Tech News Digest
**목적**: Claude와 체계적이고 안전하게 협업하기 위한 가이드
**작성일**: 2025-10-09
**버전**: 2.2 (2025-10-20 macOS 호환성 수정)

---

## 🎯 프로젝트 비전

### 미션
> "매일 아침 7시, IT/Tech 뉴스로 영어와 기술 트렌드를 동시에 배우는 YouTube 채널"

### 핵심 가치
1. **전문성**: 고품질 IT 뉴스 콘텐츠
2. **학습 효과**: 뉴스 + 영어 학습 통합
3. **자동화**: AI 기반 완전 자동 생성
4. **일관성**: 매일 정시 업로드

### 성공 기준
- 3개월: 구독자 1,000명
- 6개월: YouTube 수익화
- 12개월: 구독자 100,000명

---

## 📚 프로젝트 컨텍스트

### 현재 상태
- **Phase**: Phase 7 완료 (Intro/Outro + 메타데이터 UI)
- **시작일**: 2025-10-09
- **현재일**: 2025-10-20
- **코드베이스**: 프로덕션 준비 완료
- **완료된 Phase**: Phase 0~7 (기반 구축 → Phase 7 완료)
- **다음 단계**: 실제 YouTube 채널 런칭 또는 추가 기능

### 핵심 문서
1. **TECH_NEWS_DIGEST_PRD.md** - 제품 요구사항 문서
2. **TECH_NEWS_DIGEST_DESIGN.md** - 기술 설계 문서
3. **TASKS.md** - 태스크 관리 문서
4. **CLAUDE.md** - 본 문서 (작업 가이드라인)
5. **AUTOMATION.md** - 자동화 시스템 가이드
6. **DOCKER.md** - Docker 실행 가이드
7. **README.md** - 프로젝트 소개 및 사용법

### 관련 프로젝트
- **Daily English Mecca**: 기존 프로젝트 (9:16 Shorts, 영어 학습)
  - 위치: `../daily-english-mecca`
  - 재사용 모듈: `image_generator.py`, `tts_generator.py`, `resource_manager.py`

---

## 🛡️ 작업 원칙

### 1. 안전성 (Safety First)
```
✅ DO:
- 모든 변경 전 백업
- 작은 단위로 커밋
- 충분한 테스트 후 배포
- 에러 핸들링 필수

❌ DON'T:
- 테스트 없이 프로덕션 변경
- 큰 규모 리팩토링 단번에 진행
- API 키 노출
- 사이드 이펙트 발생
```

### 2. 체계성 (Systematic Approach)
```
작업 순서:
1. TASKS.md에서 현재 태스크 확인
2. 태스크 시작 전 관련 문서 읽기
3. 코드 작성
4. 테스트 작성 및 실행
5. 문서 업데이트
6. TASKS.md 체크 업데이트
7. 다음 태스크로 이동
```

### 3. 문서화 (Documentation)
```
필수 문서화:
- 모든 함수에 docstring
- 복잡한 로직에 주석
- README 지속 업데이트
- TASKS.md 상태 업데이트
- 변경 이력 기록
```

### 4. 테스트 (Testing)
```
테스트 레벨:
- 단위 테스트: 각 함수/클래스
- 통합 테스트: 모듈 간 연동
- E2E 테스트: 전체 파이프라인
- 수동 테스트: 영상 품질 확인
```

### 5. 커뮤니케이션 (Communication)
```
사용자 확인 필요 시점:
- 중요 아키텍처 결정
- API 키/비용 관련 사항
- 디자인/UX 선택
- 배포 전 최종 확인
```

---

## 🔧 기술 스택 및 도구

### Core Technologies
```yaml
Language: Python 3.11+ (현재 3.13 사용)
Framework: FastAPI
Video: MoviePy 2.x
AI: OpenAI (GPT-4o, GPT-4o-mini, DALL-E 3, TTS-1)
Translation: GPT-4o-mini (영어↔한글)
Database: PostgreSQL (준비 완료, 사용 대기)
Cache: Redis (Docker 통합 완료)
Queue: Celery (준비 완료, 사용 대기)
Container: Docker + docker-compose
```

### Development Tools
```yaml
Version Control: Git
Package Manager: pip, poetry
Testing: pytest
Linting: ruff, black
Type Checking: mypy
```

### Infrastructure
```yaml
Container: Docker
Cloud: AWS (EC2, S3)
CI/CD: GitHub Actions
Monitoring: CloudWatch
```

---

## 📂 프로젝트 구조 (실제 구현 완료)

```
itnews-flux/
├── src/
│   ├── core/                      # 핵심 라이브러리 ✅
│   │   ├── logging/              # 로깅 시스템 ✅
│   │   ├── config/               # 설정 관리 ✅
│   │   ├── ai_services/          # AI 서비스 ✅
│   │   │   ├── script_generator.py    # GPT-4o 스크립트
│   │   │   ├── image_generator.py     # DALL-E 3 이미지
│   │   │   ├── tts_generator.py       # TTS 음성
│   │   │   └── translator.py          # 번역 서비스 🆕
│   │   └── utils/                # 유틸리티
│   │
│   ├── news/                      # 뉴스 처리 ✅
│   │   ├── crawler/              # 크롤러 ✅
│   │   │   └── sources/          # 뉴스 소스
│   │   │       ├── techcrunch.py      # TechCrunch ✅
│   │   │       └── theverge.py        # The Verge ✅
│   │   ├── models.py             # 데이터 모델 ✅
│   │   └── selector/             # 선택기 ✅
│   │
│   ├── video/                     # 영상 제작 ✅
│   ├── automation/                # 자동화 ✅
│   │   ├── pipeline.py           # 전체 파이프라인
│   │   ├── scheduler.py          # APScheduler
│   │   └── youtube.py            # YouTube 업로드
│   │
│   ├── api/                       # FastAPI 백엔드 ✅
│   │   ├── main.py               # 메인 앱
│   │   ├── routers/              # API 라우터
│   │   │   ├── news.py           # 뉴스 API 🆕
│   │   │   ├── videos.py         # 영상 API
│   │   │   ├── schedule.py       # 스케줄 API
│   │   │   └── analytics.py      # 분석 API
│   │   └── schemas/              # 데이터 스키마
│   │
│   └── web/                       # 웹 UI ✅
│       ├── templates/            # Jinja2 템플릿
│       │   ├── dashboard.html
│       │   ├── news.html         # 뉴스 선택 UI 🆕
│       │   ├── videos.html
│       │   └── settings.html
│       └── static/               # CSS/JS
│
├── tests/                         # 테스트 스크립트
├── output/                        # 생성된 영상
├── logs/                          # 로그 파일
├── resources/                     # 폰트, 에셋
│
├── docker-compose.yml             # Docker 오케스트레이션 ✅
├── Dockerfile                     # 컨테이너 이미지 ✅
├── requirements.txt               # Python 의존성
│
├── test_crawler.py                # 크롤러 테스트
├── test_translator.py             # 번역 테스트 (영어→한글) 🆕
├── test_ai_services.py            # AI 서비스 테스트
├── test_video_production.py       # 영상 제작 테스트
├── test_pipeline.py               # 파이프라인 테스트
├── run_web.py                     # 웹 서버 실행 ✅
└── run_scheduler.py               # 스케줄러 실행 ✅
```

---

## 🚀 개발 워크플로우 (진행 상황)

### Phase 0: 기반 구축 ✅ **완료!**
```bash
[✓] 문서 작성 (PRD, DESIGN, TASKS, CLAUDE, README)
[✓] 프로젝트 구조 생성
[✓] 로깅 시스템 (프로덕션급)
[✓] 설정 관리 (Pydantic Settings)
[✓] 에러 핸들링
```

### Phase 1: 뉴스 크롤링 ✅ **완료!**
```bash
[✓] BaseCrawler (추상 클래스)
[✓] RSS Crawler
[✓] TechCrunch (영어 → 한글 번역)
[✓] The Verge (영어 → 한글 번역)
[✓] 뉴스 선택 알고리즘 (점수 기반)
```

### Phase 2: AI 콘텐츠 생성 ✅ **완료!**
```bash
[✓] GPT-4o 스크립트 생성
[✓] DALL-E 3 이미지 생성
[✓] TTS-1 음성 생성
[✓] 번역 서비스 (GPT-4o-mini) 🆕
[✓] 캐싱 시스템
```

### Phase 3: 영상 제작 ✅ **완료!**
```bash
[✓] MoviePy 2.x 통합
[✓] 16:9 Full HD 레이아웃
[✓] Lower Third 컴포넌트
[✓] 자동 영상 합성
```

### Phase 4: 자동화 ✅ **완료!**
```bash
[✓] APScheduler (매일 7AM)
[✓] YouTube OAuth2 업로드
[✓] 전체 파이프라인 통합
[✓] Slack/Email 알림
```

### Phase 5: 웹 인터페이스 ✅ **완료!**
```bash
[✓] FastAPI 백엔드 (16개 API)
[✓] 대시보드 UI
[✓] 뉴스 선택 UI 🆕
[✓] 영상 관리 UI
[✓] 실시간 모니터링
```

### Phase 6: 배포 🔄 **60% 완료**
```bash
[✓] Docker 컨테이너화
[✓] docker-compose 설정
[✓] Redis 통합
[ ] AWS/GCP 클라우드 배포 (대기)
[ ] CI/CD 파이프라인 (대기)
[ ] YouTube 채널 런칭 (대기)
```

### 각 Phase별 체크리스트
```
✅ 코드 작성
✅ 테스트 작성
✅ 테스트 실행
✅ 문서 업데이트
✅ TASKS.md 업데이트
✅ 사용자 확인
✅ 다음 Phase 이동
```

---

## 🧪 테스트 가이드라인

### 테스트 파일 구조
```python
# tests/news/crawler/test_techcrunch.py

import pytest
from src.news.crawler.sources.techcrunch import TechCrunchCrawler

class TestTechCrunchCrawler:
    """TechCrunch 크롤러 테스트"""

    @pytest.fixture
    def crawler(self):
        return TechCrunchCrawler()

    def test_fetch_news(self, crawler):
        """뉴스 가져오기 테스트"""
        news_list = crawler.fetch_news(limit=5)
        assert len(news_list) == 5
        assert all(news.title for news in news_list)

    def test_parse_article(self, crawler):
        """기사 파싱 테스트"""
        # 테스트 구현
        pass
```

### 테스트 실행
```bash
# 전체 테스트
pytest

# 특정 파일
pytest tests/news/crawler/test_techcrunch.py

# 커버리지
pytest --cov=src tests/
```

---

## 📝 로깅 가이드라인

### 로그 레벨
```python
# DEBUG: 개발 중 디버깅 정보
logger.debug("뉴스 크롤링 시작: source=TechCrunch")

# INFO: 일반 정보
logger.info("뉴스 25개 수집 완료")

# WARNING: 경고 (처리 가능한 문제)
logger.warning("API 요청 재시도 중 (3/5)")

# ERROR: 오류 (처리 불가)
logger.error("뉴스 크롤링 실패", exc_info=True)

# CRITICAL: 심각한 오류 (시스템 중단)
logger.critical("데이터베이스 연결 실패")
```

### 로그 포맷
```python
# 파일: src/core/logging/logger.py
import logging

LOG_FORMAT = (
    "[%(asctime)s] %(levelname)s "
    "[%(name)s:%(funcName)s:%(lineno)d] "
    "%(message)s"
)

# 출력 예:
# [2025-10-09 10:30:15] INFO [crawler:fetch_news:42] 뉴스 25개 수집 완료
```

---

## 🔐 보안 가이드라인

### API 키 관리
```bash
# .env 파일 (절대 커밋하지 않음)
OPENAI_API_KEY=sk-...
YOUTUBE_API_KEY=AIza...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# .env.example (커밋 가능)
OPENAI_API_KEY=your_openai_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 민감 정보 처리
```python
# ❌ 잘못된 예
print(f"API Key: {api_key}")

# ✅ 올바른 예
logger.info(f"API Key: {api_key[:8]}...")
```

---

## 📊 성능 가이드라인

### 최적화 원칙
```python
# 1. 캐싱 활용
@lru_cache(maxsize=100)
def fetch_news(source: str):
    # 캐싱된 결과 재사용
    pass

# 2. 비동기 처리
async def fetch_multiple_sources():
    tasks = [fetch_news(source) for source in sources]
    return await asyncio.gather(*tasks)

# 3. 배치 처리
def process_news_batch(news_list: list, batch_size: int = 10):
    for batch in chunked(news_list, batch_size):
        process_batch(batch)
```

### 비용 최적화
```python
# API 호출 최소화
- 이미지: DALL-E 캐싱 (동일 뉴스는 재사용)
- TTS: 음성 캐싱 (동일 텍스트는 재사용)
- GPT: 배치 요청 활용
```

---

## 🐛 에러 핸들링

### 표준 에러 처리
```python
from src.core.exceptions import CrawlerError, APIError

def fetch_news(source: str):
    try:
        # 뉴스 가져오기
        news = crawler.fetch(source)
        return news

    except requests.RequestException as e:
        logger.error(f"네트워크 오류: {source}", exc_info=True)
        raise CrawlerError(f"Failed to fetch from {source}") from e

    except Exception as e:
        logger.critical(f"예상치 못한 오류: {source}", exc_info=True)
        # 알림 발송
        send_alert(f"Critical error in {source}")
        raise
```

### 재시도 로직
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def call_api(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

---

## 📋 작업 체크리스트

### 새 기능 개발 시
```
[ ] TASKS.md에서 태스크 확인
[ ] 관련 문서 읽기 (PRD, DESIGN)
[ ] 브랜치 생성 (feature/기능명)
[ ] 코드 작성
[ ] 테스트 작성
[ ] 테스트 실행 (pytest)
[ ] 문서 업데이트
[ ] TASKS.md 업데이트
[ ] 커밋 (의미있는 메시지)
[ ] 사용자 확인
[ ] 메인 브랜치 병합
```

### 버그 수정 시
```
[ ] 이슈 확인 및 재현
[ ] 원인 분석
[ ] 수정 코드 작성
[ ] 테스트 추가 (재발 방지)
[ ] 테스트 실행
[ ] TASKS.md 이슈 업데이트
[ ] 커밋 및 배포
```

### 배포 전
```
[ ] 모든 테스트 통과
[ ] 문서 최신화
[ ] .env 설정 확인
[ ] API 키 유효성 확인
[ ] 배포 스크립트 테스트
[ ] 백업 생성
[ ] 사용자 최종 확인
[ ] 배포 실행
[ ] 모니터링 확인
```

---

## 💬 커뮤니케이션 프로토콜

### 사용자 확인이 필요한 경우
1. **아키텍처 결정**
   - "데이터베이스는 PostgreSQL을 사용하려고 합니다. 괜찮을까요?"

2. **비용 관련**
   - "DALL-E 3 사용 시 일일 $5 정도 예상됩니다. 진행할까요?"

3. **디자인 선택**
   - "로고 색상을 파란색(#1E3A8A)으로 하려고 하는데 어떠신가요?"

4. **배포 전**
   - "모든 테스트가 통과했습니다. 배포해도 될까요?"

### 진행 상황 보고
```
✅ 완료: TechCrunch 크롤러 구현
🔄 진행 중: The Verge 크롤러 구현 (50%)
⏳ 대기: Ars Technica 크롤러
❌ 블록: API 키 대기 중
```

---

## 🎯 다음 작업 (Quick Reference)

### ✅ 최근 완료 (2025-10-20)
1. [✓] Intro/Outro 텍스트 렌더링 (PIL 방식)
   - MoviePy TextClip 문제 해결 → PIL로 직접 렌더링
   - 배경음악 추가 (30% 볼륨)
   - 완벽한 텍스트 표시 (클리핑 없음)
2. [✓] YouTube 메타데이터 UI 추가
   - 웹 대시보드에서 메타데이터 확인 가능
   - 제목, 설명, 태그 표시
   - 클립보드 복사 기능

### 🔥 현재 가능한 작업
1. [ ] 실제 뉴스 영상 제작 테스트 (전체 파이프라인)
2. [ ] YouTube 채널 개설 및 OAuth 설정
3. [ ] 첫 영상 수동 업로드
4. [ ] AWS/GCP 클라우드 배포

### 🚀 새로운 기능 추가 (선택)
1. [ ] 영어 뉴스 소스 확장 (Ars Technica, Wired, MIT Tech Review)
2. [ ] 실시간 자막 (SRT) 생성
3. [ ] 다국어 지원 (일본어, 중국어)
4. [✓] ~~배경음악 추가~~ (완료)
5. [ ] 썸네일 자동 생성

### 📊 개선 작업 (선택)
1. [ ] Unit 테스트 추가 (pytest)
2. [ ] CI/CD 파이프라인 (GitHub Actions)
3. [ ] 성능 최적화 (렌더링 속도)
4. [ ] 비용 추적 대시보드
5. [ ] A/B 테스트 시스템

---

## 📞 긴급 연락

### 문제 발생 시
1. 즉시 작업 중단
2. TASKS.md에 이슈 기록
3. 사용자에게 상황 보고
4. 해결 방안 논의
5. 승인 후 진행

### 의사결정 필요 시
1. 현재 상황 설명
2. 옵션 제시 (2-3개)
3. 각 옵션의 장단점
4. 추천 사항
5. 사용자 선택 대기

---

## 🔄 문서 업데이트

### 이 문서 업데이트 시기
- Phase 변경 시
- 중요 결정 후
- 새로운 패턴 발견 시
- 문제 해결 후

### 업데이트 방법
```bash
# 1. CLAUDE.md 수정
# 2. 버전 증가 (상단)
# 3. 변경 이력 기록
# 4. TASKS.md에 반영
```

---

## 📚 참고 자료

### 내부 문서
- [TECH_NEWS_DIGEST_PRD.md](./TECH_NEWS_DIGEST_PRD.md) - 제품 요구사항
- [TECH_NEWS_DIGEST_DESIGN.md](./TECH_NEWS_DIGEST_DESIGN.md) - 기술 설계
- [TASKS.md](./TASKS.md) - 태스크 관리

### 외부 문서
- [OpenAI API Docs](https://platform.openai.com/docs)
- [MoviePy Docs](https://zulko.github.io/moviepy/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [YouTube API Docs](https://developers.google.com/youtube/v3)

---

## ✨ 성공의 열쇠

1. **체계성**: 모든 작업을 문서화하고 추적
2. **안전성**: 테스트와 검증을 철저히
3. **소통**: 중요한 결정은 반드시 확인
4. **품질**: 타협하지 않는 코드 품질
5. **지속성**: 꾸준한 개선과 학습

---

## 📊 현재 시스템 상태 (2025-10-20)

### 구현된 기능
- ✅ 뉴스 크롤링 (영어 2개 + 한국어 2개 소스)
- ✅ AI 번역 (영어 → 한글, GPT-4o-mini)
- ✅ AI 콘텐츠 생성 (스크립트, 이미지, 음성)
- ✅ 영상 자동 제작 (16:9 Full HD)
- ✅ Intro/Outro (PIL 텍스트 렌더링 + 배경음악)
- ✅ YouTube 메타데이터 (제목, 설명, 태그 자동 생성 + UI)
- ✅ YouTube 자동 업로드 (준비 완료)
- ✅ 웹 대시보드 (뉴스 선택 → 영상 생성 → 메타데이터 확인)
- ✅ Docker 컨테이너화
- ✅ 전체 파이프라인 자동화

### 시스템 성능
- 뉴스 크롤링: ~1초
- AI 콘텐츠 생성: ~30-60초
- 영상 제작: ~2-3분
- 전체 파이프라인: ~3-5분
- 영상당 비용: ~$0.023 (약 30원)

### 즉시 실행 가능
```bash
# 웹 서버 실행
python run_web.py --reload

# Docker 실행
docker-compose up -d

# 뉴스 크롤링 + 영상 생성
python run_scheduler.py --now
```

---

**이 가이드라인을 따라 Tech News Digest를 성공적으로 만들어갑시다!** 🚀

**마지막 업데이트**: 2025-10-20 (macOS 호환성 수정 완료)
**다음 리뷰**: YouTube 채널 런칭 시 또는 새로운 기능 추가 시
**현재 상태**: Phase 7 완료 + macOS 호환성 수정 - 프로덕션 사용 가능

---

## 📝 Phase 7 완료 내역 (2025-10-20)

### 주요 성과
1. **Intro/Outro 완성** ✅
   - 문제: MoviePy TextClip의 크기 계산 오류 및 텍스트 클리핑
   - 해결: PIL(Pillow)로 직접 텍스트 렌더링 후 ImageClip 변환
   - 결과: 완벽한 텍스트 표시, 배경음악 추가 (30% 볼륨)
   - 파일: `src/video/composition/video_composer.py:286-481`

2. **YouTube 메타데이터 UI** ✅
   - 기능: 웹 대시보드에서 메타데이터 확인 및 복사
   - 내용: 제목, 설명, 태그, 카테고리, 공개 상태
   - 파일: `src/web/templates/videos.html:123-218`
   - API: `src/api/routers/videos.py:121, 153` (youtube_metadata)

### 기술적 개선
- PIL을 사용한 정확한 텍스트 렌더링 (textbbox로 크기 계산)
- 수학적 중앙 정렬 (center position)
- Stroke 효과 구현 (검은 테두리)
- 메타데이터 클립보드 복사 기능

### 다음 단계
- [ ] 실제 뉴스로 전체 파이프라인 테스트
- [ ] YouTube 채널 개설 및 첫 영상 업로드
- [ ] 사용자 피드백 수집 및 개선

---

## 🔧 macOS 호환성 수정 (2025-10-20 오후)

### 문제 발견 및 해결

#### 1. **인트로/아웃트로 폰트 크기 문제** ❌→✅
- **문제**: Phase 7에서 Linux 폰트 경로 사용 → macOS에 없어서 tiny default font로 대체
- **원인**: `/usr/share/fonts/truetype/dejavu/` 경로가 macOS에 존재하지 않음
- **해결**:
  - macOS Arial 폰트 우선 시도 (`/System/Library/Fonts/Supplemental/Arial Bold.ttf`)
  - Linux DejaVu 폰트로 fallback
  - 최후 수단으로 default font
- **커밋**: `5a43ec4` - fix: Use macOS compatible fonts for intro/outro text
- **파일**: `src/video/composition/video_composer.py`

#### 2. **썸네일 생성 실패 - 파이프라인** ❌→✅
- **문제**: `'GeneratedImage' object has no attribute 'image_path'`
- **원인**: `GeneratedImage` 모델은 `local_path`를 사용, `image_path` 속성 없음
- **해결**: `first_segment.image.image_path` → `first_segment.image.local_path`
- **커밋**: `f90199d` - fix: Thumbnail generation - use local_path instead of image_path
- **파일**: `src/api/routers/videos.py:703`

#### 3. **썸네일 생성 실패 - API 스키마** ❌→✅
- **문제**: `VideoSegmentInfo`에 `image_path` 필드 없어서 API 엔드포인트에서 썸네일 생성 불가
- **원인**: 스키마에 이미지 경로 정보가 저장되지 않음
- **해결**:
  - `VideoSegmentInfo`에 `image_path` 필드 추가
  - segments 저장 시 `image.local_path` 포함
- **커밋**: `a3fc67f` - fix: Add image_path to VideoSegmentInfo for thumbnail generation
- **파일**: `src/api/schemas/video.py`, `src/api/routers/videos.py:768`

#### 4. **썸네일 한글 깨짐** ❌→✅
- **문제**: 썸네일 제목에서 한글이 깨져서 표시됨
- **원인**: Arial 폰트는 한글 지원 안 함, 잘못된 폰트 경로 사용
- **해결**:
  - macOS 한글 폰트 사용 (`AppleSDGothicNeo.ttc`)
  - Arial fallback 추가
  - 제목, 부제목, 브랜딩 모두 한글 지원
- **커밋**: `f453a80` - fix: Thumbnail Korean font support and date format
- **파일**: `src/video/thumbnail_generator.py`

#### 5. **썸네일 날짜 형식** ❌→✅
- **문제**: 날짜가 영어 형식 (`October 20, 2025`)
- **해결**: 한국 형식으로 변경 (`2025년 10월 20일`)
- **커밋**: `f453a80` (동일)
- **파일**: `src/api/routers/videos.py:711`

#### 6. **썸네일 텍스트 가독성** ❌→✅
- **문제**: 텍스트 박스가 너무 투명해서 배경 이미지 때문에 글씨가 잘 안 보임
- **해결**: `text_box_opacity` 0.85 → 0.95로 증가 (95% 불투명)
- **커밋**: `68d22d1` - fix: Increase thumbnail text box opacity for better readability
- **파일**: `src/video/thumbnail_generator.py:42`

### 커밋 히스토리
```
68d22d1 fix: Increase thumbnail text box opacity for better readability
f453a80 fix: Thumbnail Korean font support and date format
a3fc67f fix: Add image_path to VideoSegmentInfo for thumbnail generation
f90199d fix: Thumbnail generation - use local_path instead of image_path
5a43ec4 fix: Use macOS compatible fonts for intro/outro text
c3c7b20 fix: Handle VideoSegmentInfo object in thumbnail generation
08a29a5 fix: Correct TranslationService API usage
f2b1af6 fix: Use correct translate method name (generate)
```

### 수정 완료 상태

| 기능 | 상태 | 비고 |
|------|------|------|
| 인트로/아웃트로 폰트 | ✅ | macOS Arial 140pt/120pt |
| 썸네일 생성 (파이프라인) | ✅ | local_path 사용 |
| 썸네일 생성 (API) | ✅ | image_path 스키마 추가 |
| 썸네일 한글 표시 | ✅ | AppleSDGothicNeo 폰트 |
| 썸네일 날짜 형식 | ✅ | 2025년 10월 20일 |
| 썸네일 가독성 | ✅ | 95% 불투명도 |
| 번역 기능 | ✅ | 코드 정상 (API quota 필요) |

### 학습 및 개선
- **교훈**: macOS와 Linux 환경 차이를 항상 고려해야 함
- **개선**: 폰트 경로를 환경별로 fallback 구조로 설계
- **원칙**: 한 번에 테스트하지 말고, 코드 검증 후 최종 테스트만 수행 (비용 절감)
