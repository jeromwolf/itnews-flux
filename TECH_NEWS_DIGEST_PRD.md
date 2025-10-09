# Tech News Digest - PRD (Product Requirements Document)

**프로젝트명**: Tech News Digest (IT/Tech 뉴스 중심)
**타입**: IT/Tech 뉴스 영상 자동 생성 시스템
**작성일**: 2025-10-09
**작성자**: Kelly + Claude
**버전**: 1.1

---

## 📝 변경 이력

### **v1.1 (2025-10-09)** - IT/Tech 뉴스 중심으로 전략 변경
- ✅ **콘텐츠 포커스 명확화**: IT/Tech 60-80%, 경제 20-40%
- ✅ **타겟 시청자 재정의**: IT 종사자, 개발자, 스타트업 관심층
- ✅ **뉴스 소스 변경**: TechCrunch, The Verge, Ars Technica 등 IT 소스 추가
- ✅ **카테고리 가중치**: AI/ML 1.5x, Software/Cloud 1.3x 등
- ✅ **영상 구조 예시**: IT 뉴스 4개 + 경제 뉴스 1개

### **v1.0 (2025-10-09)** - 초기 PRD 작성
- 기본 시스템 아키텍처 설계
- 기능 요구사항 정의
- 프로젝트 분리 전략 수립

---

## 📋 프로젝트 개요

### **한 줄 요약**
> "매일 아침 7시, IT/Tech 뉴스로 영어와 기술 트렌드를 동시에 배우는 YouTube 채널"

### **배경**
- **기존 프로젝트**: [Daily English Mecca](../daily-english-mecca) - 9:16 Shorts, 30초, 영어 학습 문장
- **새 프로젝트**: Tech News Digest - 16:9 일반 영상, 5분, **IT/Tech 뉴스 중심** + 영어 학습
- **차별점**: IT 뉴스와 영어 학습을 통합한 **전문 앵커 스타일** 영상

### **콘텐츠 포커스**
- 🎯 **메인 (60-80%)**: IT/Technology 뉴스
  - AI, 소프트웨어, 스타트업, 클라우드, 사이버보안 등
- 💰 **서브 (20-40%)**: Business/Economics 뉴스
  - 테크 기업 실적, 투자, 경제 정책 등

### **타겟 시청자**
1. 💻 IT 종사자, 개발자
2. 🚀 스타트업 관심층
3. 📱 테크 트렌드 팔로워
4. 💼 비즈니스 영어 학습자 (중급~고급)
5. 🎓 해외 취업 준비생 (IT 분야)

---

## 🎯 목표 및 성공 지표

### **단기 목표 (3개월)**
- [ ] MVP 완성 (뉴스 크롤링 + 영상 생성)
- [ ] YouTube 채널 개설
- [ ] 구독자 1,000명 달성
- [ ] 매일 아침 7시 정시 업로드

### **중기 목표 (6개월)**
- [ ] 구독자 10,000명
- [ ] YouTube 수익화 달성 (월 $500+)
- [ ] 스폰서십 1건 이상

### **장기 목표 (12개월)**
- [ ] 구독자 100,000명
- [ ] 월 수익 $10,000+
- [ ] 다국어 확장 (일본어, 중국어)

### **핵심 성공 지표 (KPI)**
| 지표 | 목표 (3개월) | 측정 방법 |
|------|-------------|-----------|
| 구독자 수 | 1,000명 | YouTube Analytics |
| 평균 시청 시간 | 3분+ | YouTube Analytics |
| 좋아요 비율 | 5%+ | Likes / Views |
| 댓글 수 | 영상당 10개+ | YouTube Comments |
| 업로드 일관성 | 100% (매일) | 업로드 기록 |

---

## 🎬 제품 기능 요구사항

### **Core Features (MVP)**

#### **1. 뉴스 크롤링 시스템**
- **요구사항**:
  - [ ] **IT/Tech 뉴스 소스 (메인)**:
    - TechCrunch (스타트업, 벤처)
    - The Verge (기술 리뷰, 트렌드)
    - Ars Technica (심층 기술 분석)
    - Wired (기술 + 문화)
    - MIT Technology Review (연구, 혁신)
  - [ ] **경제 뉴스 소스 (서브)**:
    - Reuters (글로벌 경제)
    - Bloomberg Technology (테크 경제)
  - [ ] RSS/API 크롤링 (feedparser, requests)
  - [ ] 실시간 뉴스 업데이트 (24시간 이내)
  - [ ] 카테고리별 분류 (AI, software, startup, cloud, security, business)

- **입력**: 뉴스 소스 URL
- **출력**: 뉴스 리스트 (제목, 내용, 카테고리, 발행 시간)

- **뉴스 구성 (5개 선택)**:
  - IT/Technology: 3~4개 (60-80%)
  - Business/Economics: 1~2개 (20-40%)

#### **2. 뉴스 선택 알고리즘**
- **요구사항**:
  - [ ] 중요도 점수 계산 (breaking > major > normal)
  - [ ] **IT 카테고리 우선 가중치**:
    - AI/ML: 1.5x
    - Software/Cloud: 1.3x
    - Startup/Funding: 1.2x
    - Security: 1.2x
    - Business/Economics: 1.0x
  - [ ] 다양성 필터 (IT 3~4개, 경제 1~2개)
  - [ ] 학습 적합성 평가 (문장 길이, 어휘 난이도)
  - [ ] 시각화 가능성 평가

- **입력**: 뉴스 리스트 (100개)
- **출력**: 선택된 뉴스 5개 (IT 3~4개, 경제 1~2개)

#### **3. 앵커 스크립트 생성 (GPT-4o)**
- **요구사항**:
  - [ ] 전문 앵커 스타일 스크립트
  - [ ] 헤드라인 + 도입부 + 본문 (3문장)
  - [ ] 핵심 어휘 3~5개 (영어 + 한글)
  - [ ] 전체 한글 번역

- **입력**: 뉴스 원문
- **출력**: 앵커 스크립트 (JSON)
  ```json
  {
    "headline": "AI Breakthrough: New Model Understands Video",
    "intro": "OpenAI has released a groundbreaking AI model today.",
    "body": "The new model can analyze and understand video content. It represents a major leap in artificial intelligence. Experts say this could revolutionize content creation.",
    "vocabulary": [
      {"word": "breakthrough", "meaning": "돌파구", "example": "..."},
      {"word": "groundbreaking", "meaning": "획기적인", "example": "..."}
    ],
    "translation": "AI 돌파구: 새 모델이 비디오를 이해하다..."
  }
  ```

#### **4. 이미지 생성 (DALL-E 3)**
- **요구사항**:
  - [ ] 16:9 가로 이미지 (1792x1024)
  - [ ] 뉴스 내용 기반 프롬프트
  - [ ] 뉴스 스타일 (전문적, 뉴트럴)

- **입력**: 뉴스 헤드라인 + 내용
- **출력**: 이미지 파일 경로

#### **5. TTS 음성 생성 (OpenAI TTS)**
- **요구사항**:
  - [ ] 전문 앵커 음성 (Alloy 또는 Echo)
  - [ ] 명확한 발음, 적절한 속도
  - [ ] 자연스러운 억양

- **입력**: 앵커 스크립트
- **출력**: MP3 음성 파일

#### **6. 16:9 영상 합성 (MoviePy)**
- **요구사항**:
  - [ ] 16:9 가로 포맷 (1920x1080)
  - [ ] 전문 뉴스 레이아웃
    - 상단 헤더 (로고, 날짜, 시간)
    - 메인 비주얼 (이미지/영상)
    - Lower Third (하단 자막 바)
  - [ ] 전환 효과 (와이프, fade)
  - [ ] 배경 음악 (뉴스 스타일, 낮은 볼륨)

- **구조** (5분):
  ```
  [00:00] 인트로 (10초)
  [00:10] 오프닝 멘트 (10초)
          "Good morning. Here are today's top tech and business stories."

  [00:20] 뉴스 1 - AI/ML (60초)
          예: "OpenAI releases new multimodal AI model"

  [01:20] 전환 (2초)

  [01:22] 뉴스 2 - Software/Cloud (60초)
          예: "Google announces major cloud platform update"

  [02:22] 전환 (2초)

  [02:24] 뉴스 3 - Startup (60초)
          예: "Fintech startup raises $100M Series B funding"

  [03:24] 전환 (2초)

  [03:26] 뉴스 4 - IT/Tech (60초)
          예: "Apple unveils new AI-powered features"

  [04:26] 전환 (2초)

  [04:28] 뉴스 5 - Business/Economics (60초)
          예: "Tech stocks rise on strong earnings report"

  [05:28] 아웃트로 (15초)
          "That's all for today. Subscribe for daily tech news in English!"
  ```

#### **7. 자동화 스케줄러**
- **요구사항**:
  - [ ] 매일 오전 6시 자동 실행 (cron)
  - [ ] 파이프라인 자동 실행 (크롤링 → 영상 생성)
  - [ ] YouTube 자동 업로드 (오전 7시 예약)
  - [ ] 에러 알림 (Slack, Email)

- **실행 시간**: 50분 (6:00 ~ 6:50)

---

### **Nice-to-Have Features (Phase 2)**
- [ ] 실시간 자막 생성 (SRT 파일)
- [ ] 썸네일 자동 생성
- [ ] 다국어 지원 (일본어, 중국어)
- [ ] 개인화 추천 (시청 기록 기반)
- [ ] 커뮤니티 기능 (댓글, 퀴즈)

---

## 🏗️ 시스템 아키텍처

### **프로젝트 구조**
```
tech-news-digest/
├── src/
│   ├── news/                    # 뉴스 처리
│   │   ├── crawler/
│   │   │   ├── base_crawler.py
│   │   │   ├── bbc.py
│   │   │   ├── cnn.py
│   │   │   └── ...
│   │   ├── selector.py          # 뉴스 선택 알고리즘
│   │   ├── summarizer.py        # GPT 요약
│   │   └── script_generator.py  # 앵커 스크립트
│   │
│   ├── video/                   # 영상 제작
│   │   ├── layout_manager.py    # 레이아웃
│   │   ├── video_composer.py    # 영상 합성
│   │   └── subtitle_overlay.py  # 자막
│   │
│   ├── scheduler/               # 자동화
│   │   ├── daily_scheduler.py
│   │   └── youtube_uploader.py
│   │
│   └── core/                    # 공통 라이브러리
│       ├── image_generator.py   # DALL-E 3
│       ├── tts_generator.py     # TTS
│       └── resource_manager.py
│
├── web/                         # 웹 인터페이스
│   ├── app.py                   # Flask/FastAPI
│   └── templates/
│
├── config/
│   ├── news_sources.yaml        # 뉴스 소스 설정
│   └── video_presets.yaml       # 영상 프리셋
│
├── resources/
│   ├── fonts/
│   ├── music/
│   └── graphics/
│
└── output/
    ├── videos/
    ├── scripts/
    └── thumbnails/
```

### **기술 스택**

| 카테고리 | 기술 | 버전 |
|---------|------|------|
| **Backend** | Python | 3.11+ |
| **Web Framework** | FastAPI | 0.104+ |
| **Task Queue** | Celery + Redis | - |
| **Database** | PostgreSQL | 15+ |
| **AI/ML** | OpenAI GPT-4o, DALL-E 3, TTS-1 | latest |
| **Video** | MoviePy | 2.0+ |
| **Crawling** | feedparser, BeautifulSoup4 | latest |
| **Deployment** | Docker, AWS EC2, S3 | - |
| **CI/CD** | GitHub Actions | - |

---

## 📚 참고 프로젝트

### **Daily English Mecca** (기존 프로젝트)

**위치**: `/Users/blockmeta/Library/CloudStorage/GoogleDrive-jeromwolf@gmail.com/내 드라이브/KellyGoogleSpace/daily-english-mecca`

**참고할 모듈**:
1. **`src/image_generator.py`**
   - DALL-E 3 통합
   - 캐싱 로직
   - 이미지 회전/리사이즈
   - → **재사용 가능** (공통 패키지로)

2. **`src/tts_generator.py`**
   - OpenAI TTS-1 통합
   - 멀티 음성 생성
   - MP3 저장
   - → **재사용 가능** (공통 패키지로)

3. **`src/content_analyzer.py`**
   - GPT-4o-mini 분석
   - 이미지 프롬프트 생성
   - → **참고** (뉴스 스크립트 생성에 활용)

4. **`src/video_creator.py`**
   - MoviePy 영상 합성
   - 9:16 Shorts 로직
   - → **참고** (16:9로 변경 필요)

5. **`src/resource_manager.py`**
   - 리소스 캐싱
   - 폴더 관리
   - → **재사용 가능** (공통 패키지로)

6. **`web/app.py`**
   - Flask 웹 서버
   - 영상 생성 API
   - → **참고** (FastAPI로 변경)

**재사용 전략**:
```bash
# 1. 공통 모듈을 패키지로 추출
english-content-toolkit/
├── image_generator.py  (from daily-english-mecca)
├── tts_generator.py    (from daily-english-mecca)
└── resource_manager.py (from daily-english-mecca)

# 2. 두 프로젝트에서 공통 패키지 사용
daily-english-mecca/
└── import from english-content-toolkit

tech-news-digest/
└── import from english-content-toolkit
```

---

## 🚀 실행 계획

### **Phase 1: 기반 구축 (Week 1)**
- [ ] 프로젝트 생성 (`tech-news-digest`)
- [ ] 공통 패키지 추출 (`english-content-toolkit`)
- [ ] BBC 뉴스 크롤러 구현
- [ ] 뉴스 선택 알고리즘 구현

### **Phase 2: 영상 생성 (Week 2)**
- [ ] 앵커 스크립트 생성 (GPT-4o)
- [ ] 16:9 레이아웃 시스템 구현
- [ ] 영상 합성 로직 구현
- [ ] 첫 번째 뉴스 영상 수동 생성

### **Phase 3: 자동화 (Week 3)**
- [ ] 멀티 소스 크롤링 (5개)
- [ ] 자동 스케줄러 구현 (cron)
- [ ] YouTube API 통합
- [ ] 자동 업로드 테스트

### **Phase 4: 런칭 (Week 4)**
- [ ] YouTube 채널 개설
- [ ] 첫 영상 업로드
- [ ] 마케팅 시작
- [ ] 피드백 수집

---

## ✅ 체크리스트 (다른 세션에서 시작할 때)

### **환경 설정**
- [ ] Python 3.11+ 설치
- [ ] OpenAI API 키 발급 (.env 파일)
- [ ] YouTube Data API 키 발급
- [ ] FFmpeg 설치 (영상 인코딩)

### **의존성 설치**
```bash
pip install openai>=1.12.0
pip install moviepy>=2.0.0
pip install fastapi>=0.104.0
pip install feedparser>=6.0.0
pip install beautifulsoup4>=4.12.0
pip install celery[redis]>=5.3.0
pip install psycopg2-binary>=2.9.0
```

### **프로젝트 생성**
```bash
# 1. 프로젝트 폴더 생성
mkdir tech-news-digest
cd tech-news-digest

# 2. 구조 생성
mkdir -p src/{news/{crawler,processor},video,scheduler,core}
mkdir -p web/{templates,static}
mkdir -p config resources output

# 3. pyproject.toml 작성
cat > pyproject.toml << 'EOF'
[project]
name = "tech-news-digest"
version = "1.0.0"
dependencies = [
    "openai>=1.12.0",
    "moviepy>=2.0.0",
    "fastapi>=0.104.0",
    "feedparser>=6.0.0",
]
EOF

# 4. Git 초기화
git init
git add .
git commit -m "Initial commit: Tech News Digest"
```

### **참고 문서**
- [ ] `TECH_NEWS_DIGEST_DESIGN.md` - 전체 설계 문서
- [ ] `PROJECT_SEPARATION_STRATEGY.md` - 프로젝트 분리 전략
- [ ] Daily English Mecca 코드 - 재사용 가능 모듈

---

## 📊 예상 타임라인

| 주차 | 작업 | 목표 |
|------|------|------|
| Week 1 | 기반 구축 | 뉴스 크롤링 + 선택 |
| Week 2 | 영상 생성 | 16:9 영상 시스템 |
| Week 3 | 자동화 | 자동 스케줄러 |
| Week 4 | 런칭 | YouTube 채널 개설 |
| Month 2 | 성장 | 구독자 1,000명 |
| Month 3 | 수익화 | YouTube 파트너 |
| Month 6 | 확장 | 다국어 지원 |

---

## 💰 예상 비용

### **초기 비용 (월)**
- OpenAI API (GPT-4o + DALL-E 3 + TTS): $100~$300
- AWS EC2 (t3.medium): $30
- AWS S3 (영상 저장): $10
- **총**: $140~$340/월

### **수익 예상 (6개월 후)**
- YouTube 광고 수익: $500/월
- 스폰서십: $1,000/월
- **총**: $1,500/월 (ROI 300%+)

---

## 💡 IT 뉴스 중심 전략의 장점

### **왜 IT/Tech 뉴스인가?**
1. **명확한 타겟팅**
   - IT 종사자, 개발자라는 명확한 타겟
   - 영어 학습 + 기술 트렌드라는 이중 가치

2. **높은 CPM**
   - IT 관련 콘텐츠는 광고 CPM이 높음 ($5~$15)
   - 일반 뉴스 대비 3~5배 수익성

3. **스폰서십 기회**
   - IT 교육 플랫폼 (Udemy, Coursera)
   - 개발자 도구 (GitHub, JetBrains)
   - 클라우드 서비스 (AWS, Azure)

4. **글로벌 관심사**
   - AI, 스타트업은 전 세계 공통 관심사
   - 번역/다국어 확장 시 유리

5. **전문성 구축**
   - "IT 뉴스 영어 학습" 니치 시장 선점
   - 경쟁자 적음, 차별화 명확

### **경제 뉴스를 서브로 하는 이유**
- IT 뉴스만으로는 다양성 부족
- 테크 기업 실적, 투자 뉴스는 IT와 연관
- 비즈니스 영어 학습자도 타겟 가능

---

## 📝 다음 단계

### **즉시 실행 (다른 세션에서)**
1. 이 PRD 읽기
2. 환경 설정 (Python, API 키)
3. 프로젝트 생성
4. **TechCrunch 크롤러부터 시작** (IT 뉴스 메인 소스)

### **1주일 내**
- [ ] 뉴스 크롤링 시스템 완성
- [ ] 첫 번째 뉴스 영상 수동 생성

### **1개월 내**
- [ ] 자동화 완성
- [ ] YouTube 채널 개설
- [ ] 매일 아침 7시 업로드

---

## 🔗 유용한 링크

### **프로젝트 문서**
- **Daily English Mecca**: `../daily-english-mecca`
- **설계 문서**: `TECH_NEWS_DIGEST_DESIGN.md`
- **분리 전략**: `PROJECT_SEPARATION_STRATEGY.md`

### **기술 문서**
- **OpenAI Docs**: https://platform.openai.com/docs
- **MoviePy Docs**: https://zulko.github.io/moviepy/
- **YouTube API**: https://developers.google.com/youtube/v3
- **Feedparser Docs**: https://feedparser.readthedocs.io/

### **IT/Tech 뉴스 소스 (RSS)**
- **TechCrunch**: https://techcrunch.com/feed/
- **The Verge**: https://www.theverge.com/rss/index.xml
- **Ars Technica**: https://feeds.arstechnica.com/arstechnica/index
- **Wired**: https://www.wired.com/feed/rss
- **MIT Technology Review**: https://www.technologyreview.com/feed/

### **경제 뉴스 소스**
- **Reuters Technology**: https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best
- **Bloomberg Technology**: (API 필요)

---

**이 PRD를 기반으로 다른 세션에서 바로 시작하세요!** 🚀

**질문이 있으면**:
1. 설계 문서 참고 (`TECH_NEWS_DIGEST_DESIGN.md`)
2. Daily English Mecca 코드 참고
3. 이 PRD의 체크리스트 따라 진행

**Good luck!** 💪
