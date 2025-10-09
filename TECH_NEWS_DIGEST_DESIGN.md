# 영어 뉴스 다이제스트 (Tech News Digest)
## 프로덕션 레벨 설계 문서

**작성일**: 2025-10-09
**목표**: 전문 영어 뉴스 영상 자동 생성 시스템 구축
**포맷**: 16:9 가로 영상 (1920x1080), 3~5분

---

## 📌 프로젝트 비전

### **미션**
> "매일 아침 7시, AI가 만든 전문 영어 뉴스로 세상과 영어를 동시에 배운다"

### **핵심 가치**
1. **전문성**: BBC/CNN 수준의 뉴스 품질
2. **학습 효과**: 뉴스 + 영어 학습 통합
3. **자동화**: 100% AI 자동 생성
4. **일관성**: 매일 아침 정해진 시간 업로드

### **타겟 시청자**
- 📰 영어 뉴스에 관심 있는 학습자
- 💼 비즈니스 영어 학습자
- 🌍 글로벌 뉴스 트렌드 관심층
- 🎓 중급~고급 영어 학습자

---

## 🏗️ 시스템 아키텍처

### **전체 구조**

```
tech-news-digest/
├── src/
│   ├── core/                    # 🔧 공통 라이브러리 (패키지)
│   │   ├── ai_services/
│   │   │   ├── openai_client.py
│   │   │   ├── image_generator.py
│   │   │   └── tts_generator.py
│   │   └── utils/
│   │       ├── resource_manager.py
│   │       └── cache_manager.py
│   │
│   ├── news/                    # 📰 뉴스 처리
│   │   ├── crawler/
│   │   │   ├── base_crawler.py       # 추상 크롤러
│   │   │   ├── rss_crawler.py        # RSS 크롤러
│   │   │   ├── api_crawler.py        # API 크롤러
│   │   │   └── sources/
│   │   │       ├── bbc.py
│   │   │       ├── cnn.py
│   │   │       ├── nyt.py
│   │   │       ├── reuters.py
│   │   │       └── guardian.py
│   │   │
│   │   ├── processor/
│   │   │   ├── news_summarizer.py    # GPT 요약
│   │   │   ├── news_translator.py    # 번역 (영→한)
│   │   │   ├── script_generator.py   # 앵커 스크립트
│   │   │   └── topic_classifier.py   # 주제 분류
│   │   │
│   │   └── selector/
│   │       ├── news_ranker.py        # 뉴스 중요도 랭킹
│   │       └── diversity_filter.py   # 다양성 필터
│   │
│   ├── video/                   # 🎬 영상 제작
│   │   ├── layout/
│   │   │   ├── news_layout_manager.py   # 레이아웃 관리
│   │   │   ├── lower_third.py           # 하단 자막 바
│   │   │   ├── title_card.py            # 타이틀 카드
│   │   │   └── transition.py            # 전환 효과
│   │   │
│   │   ├── composition/
│   │   │   ├── video_composer.py        # 영상 합성
│   │   │   ├── subtitle_overlay.py      # 자막 오버레이
│   │   │   └── graphics_overlay.py      # 그래픽 오버레이
│   │   │
│   │   └── assets/
│   │       ├── templates/               # 템플릿
│   │       │   ├── intro_template.json
│   │       │   ├── news_template.json
│   │       │   └── outro_template.json
│   │       └── presets/                 # 프리셋
│   │           ├── morning_news.json
│   │           ├── tech_focus.json
│   │           └── business_daily.json
│   │
│   ├── scheduler/               # ⏰ 자동화
│   │   ├── daily_scheduler.py           # 일일 스케줄러
│   │   ├── youtube_uploader.py          # YouTube 자동 업로드
│   │   └── notification_sender.py       # 알림 발송
│   │
│   └── analytics/               # 📊 분석
│       ├── performance_tracker.py       # 성과 추적
│       ├── trend_analyzer.py            # 트렌드 분석
│       └── viewer_insights.py           # 시청자 분석
│
├── web/                         # 🌐 웹 인터페이스
│   ├── app.py                           # Flask 서버
│   ├── templates/
│   │   ├── news_dashboard.html          # 뉴스 대시보드
│   │   ├── video_preview.html           # 영상 미리보기
│   │   └── analytics_dashboard.html     # 분석 대시보드
│   └── static/
│       ├── css/
│       ├── js/
│       └── assets/
│
├── config/                      # ⚙️ 설정
│   ├── news_sources.yaml                # 뉴스 소스 설정
│   ├── video_presets.yaml               # 영상 프리셋
│   └── scheduler_config.yaml            # 스케줄러 설정
│
├── resources/                   # 📁 리소스
│   ├── fonts/                           # 폰트
│   ├── music/                           # 배경음악
│   ├── graphics/                        # 그래픽 에셋
│   └── stock_footage/                   # B-roll 영상
│
└── output/                      # 📤 결과물
    ├── videos/                          # 완성 영상
    ├── scripts/                         # 스크립트
    └── thumbnails/                      # 썸네일
```

---

## 📰 뉴스 크롤링 시스템 (멀티 소스)

### **지원 뉴스 소스**

| 소스 | 타입 | 특징 | 우선순위 |
|------|------|------|----------|
| **BBC News** | RSS | 글로벌 뉴스, 깔끔한 영어 | ⭐⭐⭐⭐⭐ |
| **CNN** | RSS | 미국 중심, 속보 빠름 | ⭐⭐⭐⭐ |
| **Reuters** | API | 경제/비즈니스 강세 | ⭐⭐⭐⭐ |
| **The Guardian** | RSS | 심층 분석 | ⭐⭐⭐ |
| **New York Times** | API | 고급 영어 표현 | ⭐⭐⭐ |

### **뉴스 선택 알고리즘**

```python
class NewsSelector:
    """뉴스 선택 및 랭킹"""

    def select_top_news(self, news_list: list, count: int = 5) -> list:
        """
        최상위 뉴스 선택

        선택 기준:
        1. 중요도 점수 (breaking > major > normal)
        2. 다양성 (주제별 1개씩)
        3. 학습 적합성 (문장 길이, 어휘 난이도)
        4. 시각화 가능성 (이미지 생성 용이성)
        5. 최신성 (24시간 이내)
        """

        scored_news = []
        for news in news_list:
            score = (
                self._importance_score(news) * 0.3 +
                self._diversity_score(news, scored_news) * 0.2 +
                self._learning_score(news) * 0.3 +
                self._visual_score(news) * 0.1 +
                self._recency_score(news) * 0.1
            )
            scored_news.append((news, score))

        # 점수 순 정렬 후 상위 N개
        scored_news.sort(key=lambda x: x[1], reverse=True)
        return [news for news, score in scored_news[:count]]
```

### **뉴스 카테고리**

```yaml
categories:
  - breaking:        # 속보 (최우선)
      priority: 10
      max_count: 1

  - technology:      # 기술
      priority: 8
      max_count: 2

  - business:        # 경제/비즈니스
      priority: 8
      max_count: 1

  - health:          # 건강
      priority: 7
      max_count: 1

  - world:           # 국제
      priority: 7
      max_count: 1

  - science:         # 과학
      priority: 6
      max_count: 1
```

---

## 🎬 전문 영상 제작 시스템

### **16:9 뉴스 레이아웃**

```
┌───────────────────────────────────────────────────┐
│  📰 ENGLISH NEWS DIGEST | Oct 9, 2025  7:00 AM   │ ← 상단 헤더 (고정)
├───────────────────────────────────────────────────┤
│                                                   │
│                                                   │
│          📸 메인 이미지/영상                       │
│          (1920x1080 - 16:9)                       │
│          - DALL-E 생성 이미지                      │
│          - 또는 Stock 영상                         │
│                                                   │
│                                                   │
├───────────────────────────────────────────────────┤
│ ■ BBC NEWS                                        │ ← Lower Third (하단 자막)
│   AI Breakthrough: New Model Understands Video    │ ← 영어 헤드라인
│   AI 돌파구: 새 모델이 비디오를 이해하다            │ ← 한글 번역
└───────────────────────────────────────────────────┘
```

### **영상 구조 (5분)**

```
[00:00] 인트로 (10초)
        - 오프닝 타이틀 "ENGLISH NEWS DIGEST"
        - 브랜딩 애니메이션
        - 날짜/시간 표시

[00:10] 오프닝 멘트 (10초)
        "Good morning. Here are today's top 5 stories in simple English."

[00:20] 뉴스 1 - Breaking News (60초)
        - 헤드라인 (5초)
        - 본문 (40초)
        - 어휘 설명 (10초)
        - 한글 번역 (5초)

[01:20] 전환 효과 (2초)
        - 와이프 전환 + "Next Story" 텍스트

[01:22] 뉴스 2 - Technology (60초)

[02:22] 전환 효과 (2초)

[02:24] 뉴스 3 - Business (60초)

[03:24] 전환 효과 (2초)

[03:26] 뉴스 4 - Health (60초)

[04:26] 전환 효과 (2초)

[04:28] 뉴스 5 - Science (60초)

[05:28] 아웃트로 (15초)
        - 요약 멘트 "That's all for today's news."
        - CTA "Subscribe for daily English news!"
        - 엔딩 크레딧
```

### **앵커 스크립트 생성 (GPT-4)**

```python
class ScriptGenerator:
    """전문 앵커 스크립트 생성"""

    def generate_anchor_script(self, news_article: dict) -> dict:
        """
        뉴스 → 앵커 스크립트 변환

        출력 구조:
        {
            'headline': '헤드라인 (5~10단어)',
            'intro': '도입부 (15~20단어)',
            'body': '본문 (40~50단어, 3문장)',
            'vocabulary': [
                {'word': 'breakthrough', 'meaning': '돌파구', 'example': '...'}
            ],
            'translation': '한글 전체 번역',
            'key_point': '핵심 요약 (1문장)'
        }
        """

        prompt = f"""You are a professional news anchor for an English learning program.

Convert this news article into a clear, simple script suitable for Korean English learners.

News Article:
{news_article['title']}
{news_article['content']}

Requirements:
1. Headline: 5-10 words, attention-grabbing
2. Intro: 15-20 words, set the context
3. Body: 40-50 words, 3 sentences, explain the main points clearly
4. Use simple, clear vocabulary (B1-B2 level)
5. Include 3-5 key vocabulary words with Korean meanings
6. Natural, conversational tone (as if speaking to viewers)

Output format: JSON
"""

        response = openai.chat.completions.create(
            model="gpt-4o",  # GPT-4o for higher quality
            messages=[
                {"role": "system", "content": "You are a professional news anchor and English teacher."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
```

---

## 🎨 비주얼 디자인 시스템

### **색상 팔레트 (전문성)**

```css
/* 브랜드 컬러 */
--primary-blue: #1E3A8A;      /* 신뢰, 전문성 */
--accent-red: #DC2626;        /* Breaking News */
--neutral-dark: #1F2937;      /* 텍스트 */
--neutral-light: #F3F4F6;     /* 배경 */
--gold: #F59E0B;              /* 강조 */

/* 카테고리별 색상 */
--breaking: #DC2626;          /* 빨강 */
--tech: #3B82F6;              /* 파랑 */
--business: #10B981;          /* 초록 */
--health: #8B5CF6;            /* 보라 */
--science: #F59E0B;           /* 오렌지 */
```

### **타이포그래피**

```yaml
fonts:
  headline:
    family: "Roboto Condensed"
    weight: 700
    size: 72px

  body:
    family: "Open Sans"
    weight: 400
    size: 48px

  subtitle:
    family: "Noto Sans KR"
    weight: 500
    size: 36px

  lower_third:
    family: "Roboto"
    weight: 500
    size: 42px
```

### **그래픽 에셋**

1. **인트로 애니메이션**
   - 로고 등장 (2초)
   - 날짜 fade-in (1초)
   - 배경 모션 그래픽 (지구본 회전, 뉴스 아이콘)

2. **Lower Third Templates**
   ```
   ┌─────────────────────────────────┐
   │ ■ BBC NEWS                      │
   │   Headline goes here...         │
   │   한글 번역...                   │
   └─────────────────────────────────┘
   ```

3. **전환 효과**
   - 와이프 전환 (좌→우)
   - "NEXT STORY" 텍스트 애니메이션
   - 카테고리 아이콘 표시

---

## 🤖 자동화 파이프라인

### **일일 자동 생성 프로세스**

```python
# scheduler/daily_scheduler.py

class DailyNewsScheduler:
    """매일 아침 6시 자동 실행"""

    def run_daily_pipeline(self):
        """
        일일 뉴스 영상 자동 생성 파이프라인

        실행 시간: 매일 오전 6:00
        완료 시간: 오전 6:50 (50분 소요)
        업로드 시간: 오전 7:00
        """

        print("📰 뉴스 다이제스트 파이프라인 시작...")

        # 1. 뉴스 크롤링 (5분)
        news_list = self.crawl_all_sources()
        print(f"✓ 뉴스 {len(news_list)}개 수집")

        # 2. 뉴스 선택 (5분)
        top_news = self.select_top_news(news_list, count=5)
        print(f"✓ 최상위 뉴스 {len(top_news)}개 선택")

        # 3. 스크립트 생성 (10분)
        scripts = [self.generate_script(news) for news in top_news]
        print(f"✓ 스크립트 생성 완료")

        # 4. 이미지 생성 (10분)
        images = [self.generate_news_image(news) for news in top_news]
        print(f"✓ 이미지 생성 완료")

        # 5. 음성 생성 (5분)
        audio_clips = [self.generate_tts(script) for script in scripts]
        print(f"✓ TTS 생성 완료")

        # 6. 영상 합성 (10분)
        video_path = self.compose_news_video(
            scripts=scripts,
            images=images,
            audio=audio_clips
        )
        print(f"✓ 영상 합성 완료: {video_path}")

        # 7. 썸네일 생성 (2분)
        thumbnail_path = self.generate_thumbnail(top_news[0])
        print(f"✓ 썸네일 생성 완료")

        # 8. YouTube 업로드 (3분)
        video_id = self.upload_to_youtube(
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            title=self.generate_title(top_news),
            description=self.generate_description(top_news),
            scheduled_time="07:00"
        )
        print(f"✓ YouTube 업로드 완료: {video_id}")

        # 9. 알림 발송
        self.send_notification(f"영상 업로드 완료! video_id: {video_id}")

        print("✅ 파이프라인 완료!")
```

### **크론 설정**

```bash
# crontab -e

# 매일 오전 6시 실행 (한국 시간 기준)
0 6 * * * cd /path/to/tech-news-digest && python -m scheduler.daily_scheduler
```

---

## 💰 수익화 전략

### **1단계: YouTube 수익화 (1~3개월)**

**요구사항:**
- 구독자 1,000명 ✓
- 시청 시간 4,000시간 ✓

**수익 예상:**
- CPM: $3~$8 (영어 학습 콘텐츠)
- 월 조회수 100만 → 월 $300~$800

### **2단계: 스폰서십 (3~6개월)**

**타겟 스폰서:**
- 영어 학습 앱 (Duolingo, Cake)
- 온라인 서점 (Yes24, 알라딘)
- 뉴스 앱 (Naver 뉴스, Google News)

**수익 예상:**
- 영상당 스폰서십: $500~$2,000
- 월 30개 영상 → 월 $15,000~$60,000

### **3단계: 프리미엄 멤버십 (6~12개월)**

**프리미엄 특전:**
- 📄 PDF 스크립트 다운로드
- 🎧 MP3 오디오 다운로드
- 📝 어휘 플래시카드
- 🎯 개인화 학습 추천

**수익 예상:**
- 멤버십 가격: $9.99/월
- 전환율 5% (구독자 10만 기준) → 5,000명
- 월 수익: $49,950

---

## 📊 성장 로드맵

### **Phase 1: MVP (1개월)**
- [x] 기본 뉴스 크롤링 (BBC, CNN)
- [x] 16:9 영상 생성
- [x] 수동 업로드

### **Phase 2: 자동화 (2개월)**
- [ ] 멀티 소스 크롤링 (5개 소스)
- [ ] 뉴스 선택 알고리즘
- [ ] 자동 스케줄링
- [ ] YouTube 자동 업로드

### **Phase 3: 고도화 (3개월)**
- [ ] AI 앵커 음성 (ElevenLabs)
- [ ] 실시간 자막 생성
- [ ] 다국어 지원 (일본어, 중국어)
- [ ] 개인화 추천

### **Phase 4: 확장 (6개월)**
- [ ] 모바일 앱 출시
- [ ] 라이브 뉴스 방송
- [ ] 커뮤니티 기능
- [ ] B2B 서비스 (기업 영어 교육)

---

## 🛠️ 기술 스택

### **Backend**
- Python 3.11+
- FastAPI (Flask보다 빠름)
- Celery (비동기 작업)
- Redis (캐싱)
- PostgreSQL (뉴스 데이터)

### **AI/ML**
- OpenAI GPT-4o (스크립트 생성)
- OpenAI DALL-E 3 (이미지 생성)
- OpenAI TTS-1 (음성 생성)
- ElevenLabs (프리미엄 음성) - 선택사항

### **Video**
- MoviePy 2.x (영상 합성)
- FFmpeg (인코딩)
- Pillow (이미지 처리)

### **Infrastructure**
- Docker (컨테이너화)
- AWS EC2 (서버)
- AWS S3 (영상 저장)
- GitHub Actions (CI/CD)

---

## 📝 다음 단계

### **즉시 실행 (이번 주)**
1. ✅ 설계 문서 완성 ← 현재
2. [ ] 프로젝트 생성 (`tech-news-digest`)
3. [ ] 공통 모듈 패키지화 (`english-content-toolkit`)
4. [ ] BBC 뉴스 크롤러 구현

### **단기 목표 (1개월)**
1. [ ] 5개 뉴스 소스 통합
2. [ ] 16:9 영상 생성 시스템 완성
3. [ ] 첫 번째 뉴스 영상 수동 생성

### **중기 목표 (3개월)**
1. [ ] 자동화 파이프라인 완성
2. [ ] YouTube 채널 개설
3. [ ] 구독자 1,000명 달성

---

## 💡 핵심 성공 요인

### **1. 품질**
- BBC/CNN 수준의 전문성
- 깔끔한 영상 편집
- 정확한 번역/해설

### **2. 일관성**
- 매일 아침 7시 업로드 (시간 엄수)
- 5분 고정 길이
- 통일된 포맷

### **3. 차별화**
- 뉴스 + 영어 학습 통합
- AI 100% 자동 생성
- 개인화 추천 (향후)

### **4. 커뮤니티**
- 댓글 적극 응답
- 시청자 피드백 반영
- 학습 커뮤니티 형성

---

**이 설계로 프로덕션 레벨 뉴스 시스템을 구축하시겠습니까?** 🚀

바로 구현 시작할까요?
