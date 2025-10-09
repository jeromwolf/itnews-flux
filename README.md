# Tech News Digest 🚀

> AI 기반 자동화로 매일 아침 7시, 최신 IT/Tech 뉴스를 전문 앵커 스타일 영상으로 전달하는 YouTube 채널

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green.svg)](https://platform.openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange.svg)]()

---

## 📋 목차

- [프로젝트 소개](#-프로젝트-소개)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [프로젝트 구조](#-프로젝트-구조)
- [시작하기](#-시작하기)
- [사용 방법](#-사용-방법)
- [개발 가이드](#-개발-가이드)
- [로드맵](#-로드맵)
- [기여하기](#-기여하기)
- [라이선스](#-라이선스)

---

## 🎯 프로젝트 소개

**Tech News Digest**는 AI를 활용하여 IT/Tech 뉴스를 자동으로 수집, 분석하고 전문 앵커 스타일의 뉴스 영상을 생성하는 완전 자동화 시스템입니다.

### 핵심 가치

- 🎯 **IT/Tech 중심**: TechCrunch, The Verge 등 전문 IT 뉴스 소스
- 🎬 **프로페셔널 품질**: 전문 뉴스 채널 스타일의 영상 제작
- 🤖 **완전 자동화**: 크롤링부터 영상 생성, 업로드까지 100% 자동
- ⏰ **정시 업로드**: 매일 아침 7시 YouTube 자동 업로드
- 💰 **비용 효율**: AI 활용으로 영상당 약 $0.03 (약 40원)

### 타겟 시청자

- 💻 IT 종사자, 개발자
- 🚀 스타트업 관심층
- 📱 테크 트렌드 팔로워
- 🌍 글로벌 IT 뉴스에 관심있는 누구나
- 🎥 자동화된 콘텐츠 제작에 관심있는 크리에이터

---

## ✨ 주요 기능

### 1. 뉴스 수집 및 선택 ✅ **완료**
- **멀티 소스 크롤링**:
  - 🇺🇸 영어: TechCrunch, The Verge
  - 🇰🇷 한국어: ETNews (전자신문), ZDNet Korea 🆕
- **스마트 선택**: 점수 기반 랭킹 + 다양성 필터
- **IT 중심**: IT/Tech 뉴스 75%, 경제 뉴스 25%
- **15개 카테고리**: AI/ML (1.5x), Software (1.3x), Startup (1.2x), Security (1.2x) 등
- **자동 점수 계산**: 중요도 × 카테고리 가중치 × 최신성 × 길이
- **AI 번역**: GPT-4o-mini 기반 영어↔한글 자동 번역 🆕

### 2. AI 콘텐츠 생성 ✅ **완료**
- **GPT-4o 스크립트**: 전문 앵커 스타일 뉴스 스크립트 자동 생성 (131단어, 60초)
- **DALL-E 3 이미지**: 뉴스 내용 기반 16:9 고품질 이미지 생성 (1792x1024)
- **OpenAI TTS**: 자연스러운 영어 음성 나레이션 생성 (Alloy 음성)

### 3. 영상 제작 ✅ **완료**
- **16:9 Full HD**: 전문 뉴스 채널 스타일 1920x1080 레이아웃
- **Lower Third**: 하단 자막 바 (영어 제목 + 한글 번역)
- **자동 합성**: MoviePy 2.x 기반 완전 자동 영상 합성
- **고품질 출력**: H264 코덱, 30fps, MP4 포맷

### 4. 자동화 ✅ **완료**
- **일일 스케줄러**: APScheduler 기반 매일 오전 7시 자동 실행
- **YouTube 업로드**: OAuth2 인증, 자동 메타데이터 생성 및 업로드
- **웹 대시보드**: FastAPI + Jinja2 기반 실시간 모니터링 UI 🆕
  - 뉴스 선택 UI (체크박스 방식, 최대 5개)
  - 선택한 뉴스로 영상 생성 버튼
  - 실시간 진행 상황 추적
- **알림 시스템**: Slack/Email 통합 지원

### 5. 배포 및 인프라 ✅ **완료**
- **Docker 컨테이너화**: 완전한 Docker/Docker Compose 지원
- **Redis 캐싱**: 뉴스 데이터 및 API 응답 캐싱
- **프로덕션 준비**: Health check, 로깅, 모니터링 완비

---

## 🛠️ 기술 스택

### Backend
- **Python 3.11+**: 핵심 언어
- **FastAPI**: 웹 프레임워크
- **Celery**: 비동기 작업 큐
- **PostgreSQL**: 데이터베이스
- **Redis**: 캐싱

### AI/ML
- **OpenAI GPT-4o**: 스크립트 생성
- **OpenAI GPT-4o-mini**: 번역 (영어 ↔ 한글) 🆕
- **OpenAI DALL-E 3**: 이미지 생성
- **OpenAI TTS-1**: 음성 생성

### Video
- **MoviePy 2.x**: 영상 합성
- **FFmpeg**: 비디오 인코딩
- **Pillow**: 이미지 처리

### Infrastructure
- **Docker**: 컨테이너화
- **AWS EC2**: 서버
- **AWS S3**: 스토리지
- **GitHub Actions**: CI/CD

---

## 📂 프로젝트 구조

```
tech-news-digest/
├── src/
│   ├── core/                    # 핵심 라이브러리 ✅
│   │   ├── logging/            # 로깅 시스템 ✅
│   │   │   ├── logger.py                # 로거 관리 ✅
│   │   │   ├── formatters.py            # JSON/Text 포맷터 ✅
│   │   │   └── filters.py               # 민감정보 필터 ✅
│   │   ├── config/             # 설정 관리 ✅
│   │   │   └── settings.py              # Pydantic Settings ✅
│   │   ├── ai_services/        # AI 서비스 (Phase 2)
│   │   └── utils/              # 유틸리티 (Phase 2)
│   │
│   ├── news/                    # 뉴스 처리 ✅
│   │   ├── models.py           # 데이터 모델 ✅
│   │   ├── crawler/            # 크롤러 ✅
│   │   │   ├── base_crawler.py         # 추상 클래스 ✅
│   │   │   └── sources/                # 뉴스 소스별 ✅
│   │   │       ├── techcrunch.py       # TechCrunch ✅
│   │   │       └── theverge.py         # The Verge ✅
│   │   ├── processor/          # 처리기 (Phase 2)
│   │   └── selector/           # 선택기 ✅
│   │       └── news_selector.py        # 뉴스 선택 알고리즘 ✅
│   │
│   ├── video/                   # 영상 제작
│   │   ├── layout/             # 레이아웃
│   │   └── composition/        # 합성
│   │
│   ├── scheduler/               # 자동화
│   │   ├── daily_scheduler.py
│   │   └── youtube_uploader.py
│   │
│   └── web/                     # 웹 인터페이스
│       ├── app.py
│       └── templates/
│
├── tests/                       # 테스트 (Phase 2+)
├── config/                      # 설정
├── resources/                   # 리소스
├── output/                      # 결과물
├── test_crawler.py              # 크롤러 테스트 스크립트 ✅
└── docs/                        # 문서
    ├── TECH_NEWS_DIGEST_PRD.md
    ├── TECH_NEWS_DIGEST_DESIGN.md
    ├── TASKS.md
    └── CLAUDE.md
```

---

## 🚀 시작하기

### 사전 요구사항

- Python 3.11 이상
- FFmpeg
- OpenAI API 키
- YouTube Data API 키

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/tech-news-digest.git
cd tech-news-digest

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 입력
```

### 환경 변수 설정 (.env)

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# YouTube
YOUTUBE_API_KEY=AIza...

# AWS (선택사항)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Database
DATABASE_URL=postgresql://user:pass@localhost/techNews

# Redis
REDIS_URL=redis://localhost:6379
```

---

## 📖 사용 방법

### 크롤러 테스트

```bash
# 영어 뉴스 크롤러 테스트 (TechCrunch + The Verge)
python test_crawler.py

# 한국 뉴스 크롤러 테스트 (ETNews + ZDNet Korea) 🆕
python test_korean_crawler.py

# 번역 서비스 테스트 🆕
python test_translator.py

# AI 서비스 통합 테스트
python test_ai_services.py
```

### 웹 서버 실행

```bash
# 개발 모드 (자동 리로드)
python run_web.py --reload

# 프로덕션 모드
python run_web.py --workers 4

# 브라우저에서 접속
# http://localhost:8000/dashboard
```

### Docker로 실행 (권장)

```bash
# 컨테이너 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f web

# 컨테이너 중지
docker-compose down
```

### 파이프라인 실행

```bash
# 즉시 실행 (테스트)
python run_scheduler.py --now

# 스케줄러 시작 (매일 7AM)
python run_scheduler.py

# YouTube 업로드 포함
python run_scheduler.py --youtube
```

### 수동 영상 생성

```python
from src.scheduler.daily_scheduler import DailyNewsScheduler

scheduler = DailyNewsScheduler()
video_path = scheduler.run_daily_pipeline()
print(f"영상 생성 완료: {video_path}")
```

---

## 👨‍💻 개발 가이드

### 개발 워크플로우

1. **TASKS.md 확인**: 현재 태스크 확인
2. **브랜치 생성**: `feature/기능명` 또는 `fix/버그명`
3. **코드 작성**: 가이드라인 준수 (CLAUDE.md 참고)
4. **테스트 작성**: 모든 코드에 테스트 작성
5. **문서 업데이트**: README, TASKS.md 업데이트
6. **PR 생성**: 리뷰 요청

### 테스트 실행

```bash
# 전체 테스트
pytest

# 특정 테스트
pytest tests/news/crawler/test_techcrunch.py

# 커버리지 확인
pytest --cov=src tests/
```

### 코드 품질

```bash
# Linting
ruff check src/

# Formatting
black src/

# Type checking
mypy src/
```

---

## 🗓️ 로드맵

### Phase 0: 프로젝트 기반 구축 ✅ **완료!**
- [x] PRD 작성
- [x] DESIGN 문서
- [x] TASKS.md
- [x] CLAUDE.md
- [x] README.md
- [x] 프로젝트 구조 생성
- [x] 로깅 시스템 (프로덕션급)
- [x] 설정 관리 (Pydantic Settings)

### Phase 1: 뉴스 크롤링 ✅ **완료!**
- [x] 뉴스 데이터 모델 (News, NewsCategory, NewsSource)
- [x] BaseCrawler 구현 (재사용 가능한 추상 클래스)
- [x] TechCrunch 크롤러 (AI, Startup, Funding)
- [x] The Verge 크롤러 (Mobile, Hardware, Reviews)
- [x] ETNews 크롤러 (한국 IT 뉴스) 🆕
- [x] ZDNet Korea 크롤러 (한국 IT 뉴스) 🆕
- [x] 뉴스 선택 알고리즘 (IT/Tech 75%, 다양성 보장)
- [x] 테스트 스크립트 (test_crawler.py, test_korean_crawler.py)

### Phase 2: AI 콘텐츠 생성 ✅ **완료!**
- [x] GPT-4o 스크립트 생성 (Professional/Casual/Educational 스타일)
- [x] DALL-E 3 이미지 생성 (16:9, 1792x1024)
- [x] OpenAI TTS 음성 생성 (6가지 음성 지원)
- [x] AI 번역 서비스 (GPT-4o-mini, 영어↔한글) 🆕
- [x] 캐싱 시스템 (MD5 해시 기반, 비용 절감)

### Phase 3: 영상 제작 ✅ **완료!**
- [x] 16:9 Full HD 레이아웃 시스템
- [x] Lower Third 컴포넌트 (dual language)
- [x] MoviePy 2.x 영상 합성 (fade effects)
- [x] 첫 테스트 영상 생성 성공 (36MB, 56초, $0.10)

### Phase 4: 자동화 ✅ **완료!**
- [x] APScheduler 일일 스케줄러 (cron-style)
- [x] YouTube OAuth2 자동 업로드
- [x] 전체 파이프라인 통합 (News → AI → Video → YouTube)
- [x] Slack/Email 알림 시스템

### Phase 5: 웹 인터페이스 ✅ **완료!**
- [x] FastAPI 백엔드 (16개 API 엔드포인트)
- [x] 대시보드 UI (Dashboard, News, Videos, Settings)
- [x] 뉴스 선택 UI (체크박스 방식, 최대 5개, 영상 생성 버튼) 🆕
- [x] 자동 번역 통합 (News API에 translate 파라미터) 🆕
- [x] 실시간 모니터링 (통계, 비용, 진행 상황)
- [x] 관리 기능 (뉴스 선택, 영상 생성, 스케줄 설정)

### Phase 6: 배포 ✅ **컨테이너화 완료!**
- [x] Docker 컨테이너화 (Python 3.11 + Redis)
- [x] docker-compose.yml (멀티 컨테이너 오케스트레이션)
- [x] 프로덕션 준비 (Health check, 로깅)
- [ ] AWS/GCP 클라우드 배포 (예정)
- [ ] CI/CD 파이프라인 (GitHub Actions, 예정)
- [ ] YouTube 채널 런칭 (예정)

---

## 🎯 성공 지표 (KPI)

### 시스템 성능
- ✅ 뉴스 크롤링: ~1초
- ✅ AI 콘텐츠 생성: ~30-60초
- ✅ 영상 제작: ~2-3분
- ✅ 전체 파이프라인: ~3-5분
- ✅ 영상당 비용: ~$0.023 (약 30원, 캐싱 활용 시)

### 비즈니스 목표 (예정)
- 업로드 일관성: 매일 오전 7시 자동 업로드
- 구독자 목표: 3개월 1,000명 → 12개월 100,000명
- YouTube 수익화 달성 (구독자 1,000명 + 시청시간 4,000시간)
- 장기 목표: 다국어 확장 (일본어, 중국어)

---

## 🤝 기여하기

기여를 환영합니다! 다음 절차를 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 기여 가이드라인
- 코드 스타일: Black + Ruff
- 테스트: 모든 코드에 테스트 필수
- 문서: 변경사항 문서화
- 커밋: Conventional Commits 사용

---

## 📝 문서

- [PRD](./TECH_NEWS_DIGEST_PRD.md) - 제품 요구사항 문서
- [DESIGN](./TECH_NEWS_DIGEST_DESIGN.md) - 기술 설계 문서
- [TASKS](./TASKS.md) - 태스크 관리 및 진행 상황
- [AUTOMATION](./AUTOMATION.md) - 자동화 시스템 사용 가이드
- [DOCKER](./DOCKER.md) - Docker 실행 가이드
- [CLAUDE](./CLAUDE.md) - 개발 가이드라인

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---

## 🙏 감사의 말

- [OpenAI](https://openai.com/) - AI 서비스 제공
- [MoviePy](https://zulko.github.io/moviepy/) - 영상 편집 라이브러리
- [FastAPI](https://fastapi.tiangolo.com/) - 웹 프레임워크

---

## 📞 연락처

- **프로젝트**: Tech News Digest
- **작성자**: Kelly
- **이메일**: [your-email@example.com]
- **YouTube**: [채널 링크 예정]

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/tech-news-digest&type=Date)](https://star-history.com/#yourusername/tech-news-digest&Date)

---

**Made with ❤️ by Kelly | Powered by Claude & OpenAI**

---

## 🔗 관련 프로젝트

- [Daily English Mecca](../daily-english-mecca) - 9:16 영어 학습 Shorts

---

<div align="center">

**Tech News Digest** 🚀

*AI 기반 자동화로 만드는 전문 IT 뉴스 채널*

[시작하기](#-시작하기) • [Docker 실행](./DOCKER.md) • [자동화 가이드](./AUTOMATION.md)

</div>
