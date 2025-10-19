# Tech News Digest - 영상 제작 시스템 전체 개선 태스크

**프로젝트**: Tech News Digest
**참고 프로젝트**: Daily English Mecca
**작성일**: 2025-10-19
**목표**: 프로덕션급 영상 제작 시스템 구축

---

## 🎯 전체 목표

Daily English Mecca의 검증된 영상 제작 시스템을 Tech News Digest에 적용하여:
1. 한글 폰트 완벽 지원
2. 커스텀 인트로/아웃트로 이미지
3. 배경 음악 시스템
4. 리소스 공유 시스템
5. 타이핑 애니메이션 (선택)
6. 영상 편집 기능 (선택)

---

## 📋 메인 태스크 목록

### ✅ Task 1: 한글 폰트 시스템 (완료)
- **상태**: COMPLETED
- **완료일**: 2025-10-19
- **결과**: Lower Third, 인트로, 아웃트로 한글 지원

### 🔄 Task 2: 커스텀 인트로/아웃트로 시스템
- **상태**: IN_PROGRESS
- **우선순위**: HIGH
- **예상 시간**: 2-3시간

### 🔄 Task 3: 배경 음악 시스템
- **상태**: PENDING
- **우선순위**: HIGH
- **예상 시간**: 1-2시간

### 🔄 Task 4: 리소스 관리 시스템
- **상태**: PENDING
- **우선순위**: MEDIUM
- **예상 시간**: 2-3시간

### ⏳ Task 5: 한국어 TTS 지원 (Google Cloud)
- **상태**: PENDING
- **우선순위**: MEDIUM
- **예상 시간**: 2-3시간
- **비고**: Google Cloud 계정 필요

### ⏳ Task 6: 영상 편집 시스템 (선택)
- **상태**: PENDING
- **우선순위**: LOW
- **예상 시간**: 5-10시간

---

## 📝 Task 2: 커스텀 인트로/아웃트로 시스템

### 목표
Daily English Mecca처럼 커스텀 이미지를 인트로/아웃트로로 사용하고, 템플릿 캐싱 지원

### 참고 코드
`daily-english-mecca/src/video_creator.py:216-280`

### Sub-Tasks

#### ✅ 2.1 인트로 이미지 시스템 설계
- [ ] 커스텀 이미지 경로 속성 추가 (`intro_custom_image`)
- [ ] 템플릿 이미지 캐싱 시스템
- [ ] 우선순위: 커스텀 > 캐시 > AI 생성 > 기본 배경
- [ ] 16:9 비율 이미지 지원 (1920x1080)

**구현 파일**: `src/video/composition/video_composer.py`

**참고 로직**:
```python
# Daily English Mecca 방식
# 1. 커스텀 이미지 확인
if self.intro_custom_image and os.path.exists(self.intro_custom_image):
    intro_image_path = self.intro_custom_image

# 2. 캐시된 템플릿 확인
elif self.resource_manager.image_exists("intro_template"):
    intro_image_path = cached_intro

# 3. AI로 생성
else:
    intro_image_path = self.image_generator.generate_image(intro_prompt)

# 4. 기본 배경 (ColorClip)
```

#### ✅ 2.2 인트로 DALL-E 템플릿 생성
- [ ] Tech News Digest용 인트로 프롬프트 작성
- [ ] DALL-E로 인트로 이미지 생성 (1920x1080)
- [ ] 캐시에 저장 (`intro_template`)
- [ ] 재사용 가능하도록 설정

**프롬프트 예시**:
```
A modern tech news studio background with geometric patterns.
Professional blue gradient with circuit board motifs.
16:9 horizontal format (1920x1080).
Clean, minimalist, high-tech aesthetic.
Suitable for news channel intro.
```

**실행 방법**:
```python
from src.core.ai_services.image_generator import ImageGenerator

gen = ImageGenerator()
image = gen.generate(
    prompt="Tech news intro background...",
    size="1792x1024",  # 16:9
    quality="hd"
)
# 저장: output/cache/intro_template.png
```

#### ✅ 2.3 아웃트로 이미지 시스템
- [ ] 아웃트로 커스텀 이미지 지원 (`outro_custom_image`)
- [ ] 구독 유도 메시지 + 이미지 합성
- [ ] QR 코드 또는 채널 로고 추가 (선택)

**아웃트로 프롬프트 예시**:
```
Minimalist thank you background for tech news channel.
Simple gradient with "Subscribe" call-to-action space.
16:9 horizontal format.
Professional and clean design.
```

#### ✅ 2.4 ImageClip 기반 인트로/아웃트로 구현
- [ ] `ColorClip` → `ImageClip` 변경
- [ ] 이미지 위에 텍스트 오버레이
- [ ] Fade In/Out 효과 유지
- [ ] 한글 폰트 적용 (이미 완료)

**구현 예시**:
```python
# 이미지 기반 인트로
intro_image = ImageClip(intro_image_path)
intro_image = intro_image.with_duration(3.0)
intro_image = intro_image.resized(width=1920, height=1080)

# 텍스트 오버레이
title_text = TextClip(
    text="Tech News Digest",
    font_size=80,
    color="white",
    font="AppleSDGothicNeo-Bold"
)
title_text = title_text.with_duration(3.0)
title_text = title_text.with_position("center")

# 합성
intro_clip = CompositeVideoClip([intro_image, title_text])
```

#### ✅ 2.5 설정 시스템 통합
- [ ] VideoProjectConfig에 커스텀 이미지 경로 추가
- [ ] 환경 변수로 기본 템플릿 경로 설정
- [ ] 웹 UI에서 이미지 업로드 기능 (선택)

**Config 추가**:
```python
class VideoProjectConfig(BaseModel):
    # 기존 필드...

    # 커스텀 이미지
    intro_custom_image: Optional[Path] = None
    outro_custom_image: Optional[Path] = None

    # 템플릿 사용 여부
    use_intro_template: bool = True
    use_outro_template: bool = True
```

---

## 📝 Task 3: 배경 음악 시스템

### 목표
인트로 구간(3초)에만 배경 음악을 낮은 볼륨(5%)으로 재생

### 참고 코드
`daily-english-mecca/src/video_creator.py:137-187`

### Sub-Tasks

#### ✅ 3.1 배경 음악 파일 준비
- [ ] 저작권 Free 배경 음악 다운로드 또는 생성
- [ ] MP3 포맷, 3초 이상 길이
- [ ] `resources/background_music.mp3` 저장
- [ ] 선택: 여러 장르 준비 (energetic, calm, upbeat)

**추천 소스**:
- YouTube Audio Library
- Pixabay Music
- Incompetech
- AI 음악 생성 (Suno, Udio)

#### ✅ 3.2 배경 음악 로딩 시스템
- [ ] ResourceManager에 배경 음악 경로 추가
- [ ] 파일 존재 여부 확인
- [ ] 여러 파일명 후보 시도 (`background_music_original.mp3`, `background_music.mp3`, `bgm.mp3`)

**구현 예시**:
```python
background_music_path = None
if self.resource_manager:
    bg_music_candidates = [
        "resources/background_music_original.mp3",
        "resources/background_music.mp3",
        "resources/bgm.mp3",
    ]
    for path in bg_music_candidates:
        if os.path.exists(path):
            background_music_path = path
            break
```

#### ✅ 3.3 볼륨 조절 및 자르기
- [ ] 볼륨 5%로 낮추기 (`bg_music * 0.05`)
- [ ] **중요**: 볼륨 조절 먼저, 자르기 나중 (순서 중요!)
- [ ] 인트로 3초만 사용 (`subclipped(0, 3.0)`)
- [ ] 시작 시간 0초로 설정 (`with_start(0)`)

**구현 예시**:
```python
# 1. 로드
bg_music = AudioFileClip(background_music_path)

# 2. 볼륨 먼저 (5%)
bg_music = bg_music * 0.05

# 3. 자르기 나중 (앞 3초만)
if bg_music.duration >= 3.0:
    bg_music = bg_music.subclipped(0, 3.0)

# 4. 시작 시간 설정
bg_music = bg_music.with_start(0)
```

#### ✅ 3.4 TTS와 배경 음악 합성
- [ ] `CompositeAudioClip`으로 TTS + 배경음악 합성
- [ ] 배경음악은 인트로 3초에만 재생
- [ ] TTS는 전체 구간 재생
- [ ] 최종 오디오 길이 검증

**구현 예시**:
```python
# TTS 오디오 (전체 구간)
tts_audio = CompositeAudioClip(audio_clips)

# 배경 음악 추가 (인트로 3초만)
combined_audio = CompositeAudioClip([tts_audio, bg_music])

# 비디오에 적용
final_video = final_video.with_audio(combined_audio)
```

#### ✅ 3.5 에러 핸들링
- [ ] 배경 음악 파일 없어도 영상 생성 계속 진행
- [ ] try-except로 안전하게 처리
- [ ] 로그에 성공/실패 메시지 출력

**구현 예시**:
```python
try:
    # 배경 음악 추가 로직
    logger.info("배경 음악 추가 완료")
except Exception as e:
    logger.warning(f"배경 음악 추가 실패 (계속 진행): {e}")
    # 배경 음악 없이 진행
```

---

## 📝 Task 3.5: 이미지 재사용성 시스템

### 목표
DALL-E 이미지 생성 비용 절감을 위한 재사용 시스템 구축

### Sub-Tasks

#### ✅ 3.5.1 뉴스 이미지 캐싱 전략
- [ ] 동일한 프롬프트는 캐시에서 재사용 (현재 구현됨)
- [ ] 유사한 뉴스 카테고리는 같은 이미지 재사용 (신규)
- [ ] 이미지 풀 시스템 구축 (신규)

**현재 상태**:
```python
# src/core/ai_services/image_generator.py
# MD5 해시 기반 캐싱 (이미 구현됨)
cache_key = hashlib.md5(prompt.encode()).hexdigest()
cached_path = output/cache/{cache_key}.png
```

**개선 방안**:
```python
# 카테고리별 이미지 풀 사용
category_images = {
    "AI/ML": ["ai_image_1.png", "ai_image_2.png", "ai_image_3.png"],
    "Hardware": ["hw_image_1.png", "hw_image_2.png"],
    "Startup": ["startup_image_1.png", "startup_image_2.png"]
}

# 같은 카테고리는 풀에서 랜덤 선택 (DALL-E 비용 $0)
if news.category in category_images:
    image_path = random.choice(category_images[news.category])
else:
    # 새로 생성
    image_path = generate_dall_e_image(news)
```

#### ✅ 3.5.2 카테고리별 이미지 풀 구축
- [ ] 각 카테고리당 3-5개 템플릿 이미지 생성
- [ ] 일회성 비용: 15개 카테고리 × 3개 = 45개 × $0.08 = $3.6
- [ ] 이후 영상은 풀에서 재사용 → DALL-E 비용 $0

**이미지 풀 구조**:
```
~/ContentCreatorResources/library/news_images/
├── ai_ml/
│   ├── ai_neural_network.png
│   ├── ai_robot_tech.png
│   └── ai_data_science.png
├── hardware/
│   ├── hw_smartphone.png
│   ├── hw_computer.png
│   └── hw_gadget.png
├── software/
│   ├── sw_coding.png
│   ├── sw_app_dev.png
│   └── sw_cloud.png
└── ...
```

#### ✅ 3.5.3 이미지 풀 생성 스크립트
- [ ] `scripts/generate_image_pool.py` 생성
- [ ] 카테고리별 DALL-E 프롬프트 정의
- [ ] 일괄 생성 및 저장
- [ ] 캐시 및 라이브러리에 저장

**스크립트 예시**:
```python
#!/usr/bin/env python3
"""
카테고리별 이미지 풀 생성 스크립트
일회성 실행: 45개 이미지 생성 ($3.6)
"""

from src.core.ai_services.image_generator import ImageGenerator
from src.news.models import NewsCategory

CATEGORY_PROMPTS = {
    NewsCategory.AI_ML: [
        "Modern AI neural network visualization with blue circuits",
        "Humanoid robot with glowing blue eyes in tech lab",
        "Abstract data science visualization with graphs"
    ],
    NewsCategory.HARDWARE: [
        "Latest smartphone with sleek modern design",
        "High-performance computer setup with RGB lighting",
        "Modern tech gadgets on minimalist desk"
    ],
    # ... 다른 카테고리
}

def generate_image_pool():
    gen = ImageGenerator()

    for category, prompts in CATEGORY_PROMPTS.items():
        category_dir = f"~/ContentCreatorResources/library/news_images/{category.value}/"
        os.makedirs(category_dir, exist_ok=True)

        for i, prompt in enumerate(prompts, 1):
            image_path = gen.generate(
                prompt=f"{prompt}. Professional tech news style, 16:9 format.",
                size="1792x1024",
                quality="standard"  # $0.08/image
            )
            # 저장
            shutil.copy(image_path, f"{category_dir}/{category.value}_{i}.png")
            print(f"✓ {category.value} 이미지 {i}/3 생성")

    print(f"\n✅ 총 {total_count}개 이미지 생성 완료!")
    print(f"💰 총 비용: ${total_count * 0.08:.2f}")
```

#### ✅ 3.5.4 이미지 선택 로직 구현
- [ ] `ImageSelector` 클래스 생성
- [ ] 카테고리별 이미지 풀 로드
- [ ] 랜덤 선택 또는 순환 선택
- [ ] 풀에 없으면 DALL-E 생성

**구현 예시**:
```python
class ImageSelector:
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.image_pools = self._load_image_pools()

    def get_image_for_news(self, news: News, use_pool: bool = True):
        """
        뉴스에 맞는 이미지 선택

        Args:
            news: 뉴스 객체
            use_pool: 이미지 풀 사용 여부

        Returns:
            이미지 경로 (풀에서 선택 또는 DALL-E 생성)
        """
        if use_pool and news.category in self.image_pools:
            # 풀에서 랜덤 선택 (비용 $0)
            return random.choice(self.image_pools[news.category])
        else:
            # DALL-E로 생성 (비용 $0.08)
            return self.dalle_generator.generate(news)
```

#### ✅ 3.5.5 비용 절감 효과 측정
- [ ] 이미지 풀 사용률 추적
- [ ] DALL-E 생성 vs 재사용 비율 로그
- [ ] 월간 비용 절감액 계산

**비용 비교**:
```
Before (이미지 풀 없음):
- 매일 5개 뉴스 × $0.08 = $0.40/일
- 월간: $0.40 × 30 = $12/월

After (이미지 풀 사용):
- 초기 비용: $3.6 (일회성)
- 이후: $0/월 (풀에서 재사용)
- 절감액: $12/월 → ROI: 3.6일

연간 절감: $144 - $3.6 = $140.4
```

---

## 📝 Task 4: 리소스 관리 시스템

### 목표
프로젝트 간 리소스 공유 및 캐싱 시스템 구축 (daily-english-mecca와 공유)

### 참고 문서
- `daily-english-mecca/PROJECT_SEPARATION_STRATEGY.md`
- `itnews-flux/RESOURCE_SHARING.md`

### Sub-Tasks

#### ✅ 4.1 ResourceManager 확인 및 개선
- [ ] 현재 `src/core/resource_manager.py` 확인
- [ ] daily-english-mecca의 ResourceManager와 호환성 확인
- [ ] 공유 리소스 풀 경로 설정 (`~/ContentCreatorResources/`)

**확인 사항**:
```python
# .resource_config.json
{
    "version": "2.0",
    "shared_resource_path": "~/ContentCreatorResources",
    "project_output_path": "./output",
    "cache_enabled": true
}
```

#### ✅ 4.2 폰트 리소스 공유
- [ ] 한글 폰트를 공유 리소스로 이동
- [ ] `~/ContentCreatorResources/fonts/` 디렉토리
- [ ] AppleSDGothicNeo, NanumGothic 등
- [ ] 두 프로젝트에서 동일 폰트 사용

#### ✅ 4.3 배경 음악 리소스 공유
- [ ] `~/ContentCreatorResources/library/music/` 사용
- [ ] 장르별 폴더 (energetic, calm, upbeat)
- [ ] 두 프로젝트에서 재사용

#### ✅ 4.4 인트로/아웃트로 템플릿 공유
- [ ] `~/ContentCreatorResources/cache/` 사용
- [ ] `intro_template_tech_news.png`
- [ ] `outro_template_tech_news.png`
- [ ] 한 번 생성하면 재사용 (API 비용 절감)

---

## 📝 Task 5: 한국어 TTS 지원 (Google Cloud)

### 목표
Google Cloud TTS를 추가하여 한국어 뉴스는 한국어 음성으로 생성

### Sub-Tasks

#### ✅ 5.1 Google Cloud 설정
- [ ] Google Cloud 계정 생성
- [ ] Cloud TTS API 활성화
- [ ] 서비스 계정 키 발급 (JSON)
- [ ] `.env`에 경로 추가 (`GOOGLE_APPLICATION_CREDENTIALS`)

**가격**:
- 무료: 월 100만 자 (Standard)
- 유료: $4 / 100만 자
- 예상 비용: $0 (무료 할당량 내)

#### ✅ 5.2 Google TTS 클라이언트 구현
- [ ] `src/core/ai_services/google_tts_generator.py` 생성
- [ ] `google-cloud-texttospeech` 라이브러리 설치
- [ ] BaseTTSService 인터페이스 구현
- [ ] 한국어 음성 모델 설정 (`ko-KR-Wavenet-A`)

**구현 예시**:
```python
from google.cloud import texttospeech

class GoogleTTSGenerator(BaseAIService):
    def generate(self, text: str, language: str = "ko-KR"):
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            name="ko-KR-Wavenet-A"  # 여성 음성
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # MP3 파일 저장
        with open(output_path, "wb") as f:
            f.write(response.audio_content)
```

#### ✅ 5.3 언어 자동 감지 및 TTS 선택
- [ ] 뉴스 언어 자동 감지 (한글/영어)
- [ ] 한글 → Google TTS
- [ ] 영어 → OpenAI TTS
- [ ] Pipeline에서 자동 선택

**구현 예시**:
```python
def generate_audio(self, script: str, news_language: str):
    if news_language == "ko":
        # Google TTS (한국어)
        return self.google_tts.generate(script, language="ko-KR")
    else:
        # OpenAI TTS (영어)
        return self.openai_tts.generate(script, voice="alloy")
```

#### ✅ 5.4 비용 추적 통합
- [ ] Google TTS 비용 계산
- [ ] OpenAI TTS와 동일한 인터페이스
- [ ] 총 비용 집계에 포함

---

## 📝 Task 6: 영상 편집 시스템 (선택)

### 목표
Daily English Mecca처럼 웹 UI에서 영상 편집 기능 제공

### 참고 파일
- `daily-english-mecca/src/editor/video_editor.py`
- `daily-english-mecca/src/editor/config_manager.py`
- `daily-english-mecca/EDITOR_DESIGN.md`

### Sub-Tasks

#### ✅ 6.1 편집 Config 시스템
- [ ] VideoEditConfig 모델 설계
- [ ] JSON 기반 편집 설정 저장
- [ ] 버전 관리 (config version)

**Config 구조**:
```json
{
  "video_id": "video-20251019-abc123",
  "version": "1.0",
  "edited_at": "2025-10-19T12:00:00",
  "global_settings": {
    "background_music": {"enabled": true, "volume": 0.15},
    "intro": {"enabled": true, "duration": 3, "custom_image": "path/to/intro.png"},
    "outro": {"enabled": true, "duration": 2, "custom_image": "path/to/outro.png"}
  },
  "clips": [
    {
      "clip_id": 1,
      "sentence": "Breaking news...",
      "translation": "속보...",
      "image_path": "path/to/image1.png",
      "audio_path": "path/to/audio1.mp3",
      "duration": 10.5
    }
  ]
}
```

#### ✅ 6.2 웹 UI 편집 인터페이스
- [ ] 영상 편집 페이지 추가 (`/videos/{video_id}/edit`)
- [ ] 세그먼트별 미리보기
- [ ] 순서 변경 (Drag & Drop)
- [ ] 세그먼트 삭제/추가
- [ ] 실시간 미리보기 (선택)

#### ✅ 6.3 영상 재생성 API
- [ ] `POST /api/videos/{video_id}/regenerate` 엔드포인트
- [ ] 편집된 설정으로 영상 재생성
- [ ] 백그라운드 작업으로 실행
- [ ] 진행 상황 추적

#### ✅ 6.4 VideoEditor 클래스 구현
- [ ] `src/video/editor/video_editor.py` 생성
- [ ] ConfigManager 통합
- [ ] 편집 설정 적용 로직
- [ ] 원본 리소스 재사용 (audio, image)

---

## 🎯 작업 우선순위

### Phase 1 (즉시 시작, 1-2일)
1. ✅ Task 1: 한글 폰트 (완료)
2. 🔄 Task 2: 커스텀 인트로/아웃트로 (진행 중)
3. 🔄 Task 3: 배경 음악
4. 🔥 Task 3.5: 이미지 재사용성 시스템 (비용 절감)

### Phase 2 (1주일 내)
5. ⏳ Task 4: 리소스 관리 시스템
6. ⏳ Task 5: 한국어 TTS (Google Cloud)

### Phase 3 (선택, 2주 내)
7. ⏳ Task 6: 영상 편집 시스템

---

## 📊 예상 일정

| Task | 우선순위 | 예상 시간 | 예상 비용 절감 | 상태 |
|------|---------|----------|--------------|------|
| Task 1: 한글 폰트 | HIGH | 30분 | - | ✅ DONE |
| Task 2: 인트로/아웃트로 | HIGH | 2-3시간 | $0.16/영상 | 🔄 IN_PROGRESS |
| Task 3: 배경 음악 | HIGH | 1-2시간 | - | ⏳ PENDING |
| **Task 3.5: 이미지 재사용** | **🔥 CRITICAL** | **2-3시간** | **$12/월** | ⏳ PENDING |
| Task 4: 리소스 관리 | MEDIUM | 2-3시간 | - | ⏳ PENDING |
| Task 5: 한국어 TTS | MEDIUM | 2-3시간 | - | ⏳ PENDING |
| Task 6: 영상 편집 | LOW | 5-10시간 | - | ⏳ PENDING |

**총 예상 시간**: 15-25시간 (Task 6 제외 시: 10-15시간)
**예상 비용 절감**: 월 $12 (연간 $140+)

---

## ✅ 완료 기준

### Task 2 완료 조건
- [ ] 커스텀 이미지로 인트로/아웃트로 생성 가능
- [ ] DALL-E 템플릿 이미지 1회 생성 후 재사용
- [ ] 한글 텍스트 정상 표시
- [ ] Fade 효과 작동
- [ ] 테스트 영상 생성 성공

### Task 3 완료 조건
- [ ] 배경 음악 파일 준비 완료
- [ ] 인트로 3초 구간만 재생
- [ ] 볼륨 5% 적용
- [ ] TTS와 정상 합성
- [ ] 배경 음악 없어도 영상 생성 가능

### Task 4 완료 조건
- [ ] 공유 리소스 디렉토리 설정
- [ ] daily-english-mecca와 리소스 공유 확인
- [ ] 폰트, 음악, 템플릿 공유 작동
- [ ] API 비용 절감 확인 (캐시 히트율 측정)

### Task 5 완료 조건
- [ ] Google Cloud TTS 계정 설정
- [ ] 한국어 음성 정상 생성
- [ ] 언어 자동 감지 작동
- [ ] 영어/한국어 뉴스 각각 적절한 TTS 사용
- [ ] 비용 추적 정상 작동

### Task 6 완료 조건
- [ ] 웹 UI에서 영상 편집 가능
- [ ] 편집 설정 저장/로드 가능
- [ ] 영상 재생성 API 작동
- [ ] 편집된 영상 정상 생성

---

## 🚀 다음 액션

켈리님, 어떤 Task부터 시작할까요?

### 옵션 A: Task 2 바로 시작 (추천)
```
✅ 인트로/아웃트로 이미지 시스템
⏱️  2-3시간 소요
🎬 즉시 효과 확인 가능
```

### 옵션 B: Task 2 + Task 3 함께
```
✅ 인트로/아웃트로 + 배경 음악
⏱️  3-5시간 소요
🎬 완성도 높은 영상
```

### 옵션 C: 전체 순서대로 (Task 2 → 3 → 4 → 5)
```
✅ 모든 기능 완성
⏱️  1-2주 소요
🎬 프로덕션 완성도
```

---

**문서 작성 완료**: 2025-10-19
**다음 업데이트**: 각 Task 시작 시
**참고 프로젝트**: Daily English Mecca
