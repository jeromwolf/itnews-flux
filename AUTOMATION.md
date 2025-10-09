# Tech News Digest - Automation Guide

완전 자동화된 뉴스 영상 제작 시스템 사용 가이드입니다.

## 📋 목차

1. [빠른 시작](#빠른-시작)
2. [파이프라인 실행](#파이프라인-실행)
3. [스케줄러 설정](#스케줄러-설정)
4. [YouTube 업로드](#youtube-업로드)
5. [알림 설정](#알림-설정)

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 1. 가상환경 활성화
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일에서 OpenAI API 키 설정
```

### 2. 즉시 실행 (테스트)

```bash
# 파이프라인 즉시 실행 (YouTube 업로드 없음)
python run_scheduler.py --now

# YouTube 업로드 포함 (OAuth 인증 필요)
python run_scheduler.py --now --youtube
```

### 3. 스케줄러 실행

```bash
# 매일 오전 7시에 자동 실행
python run_scheduler.py

# 커스텀 시간 설정 (오전 9시 30분)
python run_scheduler.py --hour 9 --minute 30

# YouTube 업로드 + 이메일 알림 포함
python run_scheduler.py --youtube --email your@email.com
```

---

## 🔄 파이프라인 실행

### 기본 파이프라인

```python
from src.automation import create_pipeline, PipelineConfig

# 설정
config = PipelineConfig(
    news_limit=3,              # 뉴스 3개
    max_age_hours=24,          # 최근 24시간 뉴스
    sources=["techcrunch", "theverge"],
    segment_duration=60,       # 60초/세그먼트
    image_quality="standard",  # 이미지 품질
    tts_voice="alloy",        # TTS 음성
    enable_youtube_upload=False,  # YouTube 업로드 비활성화
)

# 실행
pipeline = create_pipeline(config)
result = pipeline.run()

# 결과 확인
if result.success:
    print(f"✅ Video: {result.video_path}")
    print(f"💰 Cost: ${result.total_cost:.4f}")
    print(f"⏱️  Time: {result.execution_time:.1f}s")
else:
    print(f"❌ Errors: {result.errors}")
```

### 파이프라인 단계별 실행

```python
from src.automation import create_pipeline

pipeline = create_pipeline()

# Step 1: 뉴스 크롤링
news_list = pipeline.fetch_news()
print(f"Fetched {len(news_list)} articles")

# Step 2: AI 콘텐츠 생성
segments = pipeline.generate_content(news_list)
print(f"Generated {len(segments)} segments")

# Step 3: 영상 제작
video_path = pipeline.create_video(segments)
print(f"Video created: {video_path}")
```

---

## ⏰ 스케줄러 설정

### 기본 스케줄러

```python
from src.automation import create_scheduler, SchedulerConfig, PipelineConfig

# 파이프라인 설정
pipeline_config = PipelineConfig(
    news_limit=3,
    enable_youtube_upload=True,
)

# 스케줄러 설정
scheduler_config = SchedulerConfig(
    hour=7,                    # 오전 7시
    minute=0,                  # 0분
    timezone="Asia/Seoul",     # 한국 시간
    pipeline_config=pipeline_config,
)

# 스케줄러 생성 및 실행
scheduler = create_scheduler(scheduler_config)
scheduler.start()  # Blocking - Ctrl+C로 종료
```

### CLI로 스케줄러 실행

```bash
# 기본 (오전 7시)
python run_scheduler.py

# 커스텀 시간
python run_scheduler.py --hour 9 --minute 30

# 타임존 변경
python run_scheduler.py --timezone America/New_York

# 즉시 실행 (테스트)
python run_scheduler.py --now

# YouTube 업로드 활성화
python run_scheduler.py --youtube

# 뉴스 개수 설정
python run_scheduler.py --news-limit 5 --max-age 48
```

---

## 📺 YouTube 업로드

### 1. YouTube API 설정

1. **Google Cloud Console 설정**
   ```
   1. https://console.cloud.google.com/ 접속
   2. 새 프로젝트 생성: "Tech News Digest"
   3. YouTube Data API v3 활성화
   4. OAuth 2.0 Client ID 생성 (Desktop app)
   5. JSON 다운로드
   ```

2. **인증 파일 저장**
   ```bash
   mkdir -p config
   # 다운로드한 JSON을 config/client_secrets.json으로 저장
   mv ~/Downloads/client_secret_*.json config/client_secrets.json
   ```

3. **첫 인증 실행**
   ```bash
   # 첫 실행 시 브라우저가 열리고 인증 진행
   python run_scheduler.py --now --youtube
   ```

### 2. YouTube 업로드 설정

```python
from src.automation import create_youtube_uploader, YouTubeConfig

# 설정
config = YouTubeConfig(
    title_template="Tech News Digest - {date}",
    category_id="28",  # Science & Technology
    tags=["tech news", "english learning", "IT"],
    privacy_status="public",  # public/private/unlisted
    playlist_id="PLxxxxxxx",  # 플레이리스트 ID (선택)
)

# 업로더 생성
uploader = create_youtube_uploader(config)
uploader.authenticate()

# 영상 업로드
result = uploader.upload_video(
    video_path=Path("output/videos/tech_news.mp4"),
    topics=["OpenAI GPT-5", "Tesla AI"],
)

print(f"✅ Uploaded: {result['video_url']}")
```

### 3. 파이프라인에서 YouTube 업로드

```python
from src.automation import create_pipeline, PipelineConfig

# YouTube 업로드 활성화
config = PipelineConfig(
    enable_youtube_upload=True,  # ← 이것만 True로 설정
)

pipeline = create_pipeline(config)
result = pipeline.run()

if result.youtube_url:
    print(f"📺 YouTube: {result.youtube_url}")
```

---

## 🔔 알림 설정

### 1. 이메일 알림 (예정)

```bash
# 이메일 알림 활성화
python run_scheduler.py --email your@email.com
```

### 2. Slack 알림

1. **Slack Webhook 생성**
   ```
   1. https://api.slack.com/apps 접속
   2. "Create New App" → "From scratch"
   3. "Incoming Webhooks" 활성화
   4. "Add New Webhook to Workspace"
   5. Webhook URL 복사
   ```

2. **Slack 알림 사용**
   ```bash
   python run_scheduler.py \
       --slack-webhook https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

3. **코드에서 설정**
   ```python
   from src.automation import create_scheduler, SchedulerConfig

   config = SchedulerConfig(
       enable_notifications=True,
       slack_webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
   )

   scheduler = create_scheduler(config)
   scheduler.start()
   ```

---

## 📊 비용 및 성능

### 예상 비용 (뉴스 3개 기준)

| 항목 | 단가 | 비용 |
|------|------|------|
| GPT-4o Script | $0.005/article | $0.015 |
| DALL-E 3 Image | $0.08/image | $0.24 |
| TTS Audio | $0.007/article | $0.021 |
| **총 비용** | - | **$0.276** (~370원) |

*캐싱 활용 시 이미지 비용 절감 가능*

### 실행 시간

- 뉴스 크롤링: ~1초
- AI 콘텐츠 생성: ~30-60초
- 영상 제작: ~2-3분
- YouTube 업로드: ~30-60초
- **총 시간: ~3-5분**

---

## 🛠️ 고급 설정

### 1. 커스텀 파이프라인

```python
from src.automation import ContentPipeline, PipelineConfig

class CustomPipeline(ContentPipeline):
    def fetch_news(self):
        # 커스텀 뉴스 소스 추가
        news = super().fetch_news()
        # ... 추가 로직
        return news

    def generate_content(self, news_list):
        # 커스텀 콘텐츠 생성
        segments = super().generate_content(news_list)
        # ... 추가 로직
        return segments
```

### 2. 로깅 설정

```python
from src.core.logging import get_logger

# 커스텀 로거 사용
logger = get_logger("my_automation")
logger.info("Custom log message")
```

### 3. 에러 처리

```python
from src.automation import create_pipeline

pipeline = create_pipeline()

try:
    result = pipeline.run()
    if not result.success:
        for error in result.errors:
            print(f"Error: {error}")
except Exception as e:
    print(f"Pipeline failed: {e}")
```

---

## 🔍 트러블슈팅

### YouTube 인증 실패

```bash
# 1. 인증 토큰 삭제
rm config/youtube_token.pickle

# 2. 재인증
python run_scheduler.py --now --youtube
```

### API 할당량 초과

```python
# YouTube API 할당량 확인
from src.automation import create_youtube_uploader

uploader = create_youtube_uploader()
quota = uploader.get_upload_quota()
print(quota)
```

### 스케줄러가 실행되지 않음

```bash
# 다음 실행 시간 확인
python -c "
from src.automation import create_scheduler
scheduler = create_scheduler()
scheduler.list_jobs()
"
```

---

## 📝 예제 사용 사례

### 1. 매일 아침 7시 자동 실행 + YouTube 업로드

```bash
# systemd service로 등록 (Linux)
sudo nano /etc/systemd/system/tech-news-digest.service

# 서비스 파일 내용:
[Unit]
Description=Tech News Digest Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/itnews-flux
ExecStart=/path/to/venv/bin/python run_scheduler.py --youtube
Restart=always

[Install]
WantedBy=multi-user.target

# 서비스 시작
sudo systemctl enable tech-news-digest
sudo systemctl start tech-news-digest
```

### 2. 주말에만 실행

```python
from datetime import datetime
from src.automation import create_scheduler

scheduler = create_scheduler()

# 토요일, 일요일에만 실행 (커스텀 로직 필요)
def weekend_only():
    if datetime.now().weekday() >= 5:  # 5=토, 6=일
        scheduler.run_pipeline()

# Cron job으로 등록
# 0 7 * * 6,0 python run_weekend.py
```

### 3. 영상 후처리 추가

```python
from src.automation import create_pipeline

pipeline = create_pipeline()
result = pipeline.run()

if result.success and result.video_path:
    # 썸네일 생성
    thumbnail = create_thumbnail(result.video_path)

    # YouTube 업로드 + 썸네일 설정
    if result.youtube_url:
        uploader.set_thumbnail(
            video_id=result.youtube_url.split('=')[1],
            thumbnail_path=thumbnail
        )
```

---

## 📞 지원

문제가 발생하면:
1. 로그 확인: `logs/` 디렉토리
2. GitHub Issues: https://github.com/yourusername/itnews-flux/issues
3. 문서: [README.md](README.md), [DESIGN.md](DESIGN.md)

---

**마지막 업데이트**: 2025-10-09
