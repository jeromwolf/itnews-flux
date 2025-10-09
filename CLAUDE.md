# Claude 작업 가이드라인

**프로젝트**: Tech News Digest
**목적**: Claude와 체계적이고 안전하게 협업하기 위한 가이드
**작성일**: 2025-10-09
**버전**: 1.0

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
- **Phase**: Phase 0 - 프로젝트 기반 구축
- **시작일**: 2025-10-09
- **코드베이스**: 초기 상태 (문서만 존재)

### 핵심 문서
1. **TECH_NEWS_DIGEST_PRD.md** - 제품 요구사항 문서
2. **TECH_NEWS_DIGEST_DESIGN.md** - 기술 설계 문서
3. **TASKS.md** - 태스크 관리 문서
4. **CLAUDE.md** - 본 문서 (작업 가이드라인)

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
Language: Python 3.11+
Framework: FastAPI
Video: MoviePy 2.x
AI: OpenAI (GPT-4o, DALL-E 3, TTS-1)
Database: PostgreSQL
Cache: Redis
Queue: Celery
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

## 📂 프로젝트 구조

```
tech-news-digest/
├── src/
│   ├── core/               # 핵심 라이브러리
│   │   ├── logging/       # 로깅 시스템
│   │   ├── config/        # 설정 관리
│   │   ├── ai_services/   # AI 서비스 (OpenAI)
│   │   └── utils/         # 유틸리티
│   │
│   ├── news/              # 뉴스 처리
│   │   ├── crawler/       # 크롤러
│   │   ├── processor/     # 처리기
│   │   └── selector/      # 선택기
│   │
│   ├── video/             # 영상 제작
│   │   ├── layout/        # 레이아웃
│   │   └── composition/   # 합성
│   │
│   ├── scheduler/         # 자동화
│   └── web/               # 웹 인터페이스
│
├── tests/                 # 테스트
├── config/                # 설정 파일
├── resources/             # 리소스
├── output/                # 결과물
└── docs/                  # 문서
```

---

## 🚀 개발 워크플로우

### Phase 0: 기반 구축 (현재)
```bash
# 1. 문서 작성
[✓] TASKS.md
[>] CLAUDE.md
[ ] .gitignore
[ ] README.md

# 2. 프로젝트 구조
[ ] 디렉토리 생성
[ ] 설정 파일 작성

# 3. 코어 시스템
[ ] 로깅 시스템
[ ] 설정 관리
[ ] 에러 핸들링
```

### Phase 1: 뉴스 크롤링
```bash
# 1. 기반 구조
[ ] BaseCrawler
[ ] RSS Crawler
[ ] API Crawler

# 2. IT 뉴스 소스 (우선순위)
[ ] TechCrunch      # 최우선
[ ] The Verge
[ ] Ars Technica
[ ] MIT Tech Review
[ ] Wired

# 3. 경제 뉴스 소스
[ ] Reuters
[ ] Bloomberg Tech
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

### 지금 당장 (Phase 0)
1. [>] CLAUDE.md 작성 (현재)
2. [ ] .gitignore 작성
3. [ ] 프로젝트 구조 생성
4. [ ] 로깅 시스템 구현

### 이번 주 (Phase 0-1)
1. [ ] 설정 관리 시스템
2. [ ] TechCrunch 크롤러
3. [ ] 첫 테스트 실행

### 다음 주 (Phase 1-2)
1. [ ] 나머지 크롤러 구현
2. [ ] GPT 스크립트 생성
3. [ ] 이미지/음성 생성

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

**이 가이드라인을 따라 Tech News Digest를 성공적으로 만들어갑시다!** 🚀

**마지막 업데이트**: 2025-10-09
**다음 리뷰**: Phase 1 시작 시
