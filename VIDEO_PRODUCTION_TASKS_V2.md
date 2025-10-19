# Tech News Digest - 영상 제작 시스템 전체 개선 태스크 (v2)

**프로젝트**: Tech News Digest
**참고 프로젝트**: Daily English Mecca
**작성일**: 2025-10-19
**버전**: 2.0 (체계적 단계별 진행)
**목표**: 프로덕션급 영상 제작 시스템 구축

---

## 🎯 전체 목표

현재 문제점:
1. ❌ 한글 Lower Third 깨짐 (□□□ 표시)
2. ❌ 동영상 한국어 TTS 안 나옴 (OpenAI TTS는 영어만 지원)
3. ❌ 인트로/아웃트로가 단순 컬러 배경

개선 목표:
1. ✅ 한글 완벽 지원 (폰트, TTS)
2. ✅ 커스텀 인트로/아웃트로 이미지
3. ✅ 배경 음악 시스템
4. ✅ 이미지 재사용 시스템 (비용 절감)
5. ✅ 리소스 공유 시스템

---

## 📋 메인 태스크 목록 및 우선순위

### Phase 1: 핵심 기능 수정 (필수)

#### ✅ Task 1: 한글 폰트 시스템
- **상태**: ✅ COMPLETED
- **완료일**: 2025-10-19
- **결과**: 코드 수정 완료, 실제 테스트 필요

#### 🔲 Task 2: 실제 영상 생성 테스트 및 검증
- **상태**: ⏳ PENDING
- **우선순위**: 🔥 CRITICAL
- **예상 시간**: 30분
- **목적**: Task 1의 한글 폰트 수정이 실제로 작동하는지 확인

#### 🔲 Task 3: 커스텀 인트로/아웃트로 시스템
- **상태**: ⏳ PENDING
- **우선순위**: 🔥 HIGH
- **예상 시간**: 2-3시간

#### 🔲 Task 4: 배경 음악 시스템
- **상태**: ⏳ PENDING
- **우선순위**: 🔥 HIGH
- **예상 시간**: 1-2시간

### Phase 2: 비용 최적화 (중요)

#### ✅ Task 5: 이미지 재사용 시스템
- **상태**: ✅ COMPLETED
- **완료일**: 2025-10-19
- **결과**: 코드 완료, 풀 생성은 켈리님 결정 필요

### Phase 3: 고급 기능 (선택)

#### 🔲 Task 6: 한국어 TTS 지원 (Google Cloud)
- **상태**: ⏳ PENDING
- **우선순위**: ⭐ MEDIUM
- **예상 시간**: 2-3시간
- **비고**: Google Cloud 계정 필요

#### 🔲 Task 7: 리소스 관리 시스템
- **상태**: ⏳ PENDING
- **우선순위**: ⭐ MEDIUM
- **예상 시간**: 2-3시간

#### 🔲 Task 8: 영상 편집 시스템 (선택)
- **상태**: ⏳ PENDING
- **우선순위**: 🟢 LOW
- **예상 시간**: 5-10시간

---

## 📝 Task 2: 실제 영상 생성 테스트 및 검증

### 목표
Task 1에서 수정한 한글 폰트 시스템이 실제로 작동하는지 테스트

### 현재 상황
- ✅ 코드는 수정 완료 (Lower Third, 인트로, 아웃트로)
- ❓ 실제 영상 생성 시 한글이 제대로 표시되는지 미확인
- ❓ Docker 재시작 필요 여부 확인

### Sub-Tasks

#### 🔲 2.1 Docker 컨테이너 재시작
- [ ] Docker Compose 중지
- [ ] 코드 변경사항 반영
- [ ] Docker Compose 재시작
- [ ] 로그 확인

**실행 명령**:
```bash
cd ~/Library/CloudStorage/GoogleDrive-jeromwolf@gmail.com/내\ 드라이브/KellyGoogleSpace/itnews-flux
docker-compose down
docker-compose up -d
docker-compose logs -f web
```

**체크포인트**:
- [ ] 컨테이너 정상 시작
- [ ] 웹 서버 http://localhost:8000 접속 가능
- [ ] 에러 로그 없음

#### 🔲 2.2 테스트 영상 생성 (웹 UI)
- [ ] 웹 브라우저에서 http://localhost:8000 접속
- [ ] News 페이지에서 뉴스 1개 선택
- [ ] "Create Video" 클릭
- [ ] Videos 페이지에서 생성 진행 확인
- [ ] 생성 완료 대기 (~3-5분)

**체크포인트**:
- [ ] 뉴스 크롤링 성공
- [ ] AI 콘텐츠 생성 성공 (스크립트, 이미지, 오디오)
- [ ] 영상 합성 성공
- [ ] COMPLETED 상태 확인

#### 🔲 2.3 영상 다운로드 및 확인
- [ ] "Download" 버튼으로 영상 다운로드
- [ ] 영상 재생
- [ ] Lower Third 한글 확인
- [ ] 인트로 한글 확인 ("Tech News Digest")
- [ ] 아웃트로 한글 확인 ("시청해 주셔서 감사합니다")

**확인 사항**:
- [ ] Lower Third에 한글이 □□□ 없이 제대로 표시됨
- [ ] 인트로 타이틀이 제대로 표시됨
- [ ] 아웃트로 메시지가 제대로 표시됨
- [ ] 전반적인 영상 품질 확인

#### 🔲 2.4 문제 발생 시 디버깅
**만약 한글이 여전히 깨진다면**:

1. 로그 확인
   ```bash
   docker-compose logs web | grep -i "font"
   ```

2. 폰트 파일 확인
   ```bash
   docker-compose exec web ls -la /System/Library/Fonts/Apple* 2>/dev/null || echo "macOS 폰트 없음"
   ```

3. 컨테이너 내부 확인
   ```bash
   docker-compose exec web python -c "from PIL import ImageFont; print('PIL 정상')"
   ```

**해결 방법**:
- [ ] 폰트 파일을 프로젝트에 직접 포함
- [ ] Dockerfile에 폰트 설치 추가
- [ ] 다른 폰트로 대체

#### 🔲 2.5 켈리님 컨펌
- [ ] 영상 확인 완료
- [ ] 한글 표시 정상
- [ ] 다음 Task로 진행 승인

**컨펌 후 액션**:
- ✅ 성공 → Task 3으로 진행
- ❌ 실패 → Task 2.4 디버깅 계속

---

## 📝 Task 3: 커스텀 인트로/아웃트로 시스템

### 목표
ColorClip 대신 DALL-E로 생성한 커스텀 이미지 사용

### Sub-Tasks

#### 🔲 3.1 VideoProjectConfig에 커스텀 이미지 필드 추가
**파일**: `src/video/models.py`

**추가할 필드**:
```python
class VideoProjectConfig(BaseModel):
    # 기존 필드...

    # 커스텀 이미지
    intro_image_path: Optional[Path] = None
    outro_image_path: Optional[Path] = None

    # 이미지 우선순위 사용 여부
    use_custom_intro: bool = True
    use_custom_outro: bool = True
```

**테스트**:
```python
config = VideoProjectConfig(intro_image_path=Path("intro.png"))
assert config.intro_image_path is not None
```

**체크포인트**:
- [ ] 코드 수정 완료
- [ ] 테스트 통과
- [ ] 켈리님 컨펌

#### 🔲 3.2 인트로 이미지 생성 (DALL-E)
**목표**: Tech News Digest용 전문 인트로 이미지 생성

**스크립트**: `scripts/generate_intro_outro.py` (새로 생성)

```python
from src.core.ai_services.image_generator import ImageGenerator

gen = ImageGenerator()

# 인트로 프롬프트
intro_prompt = """
Modern tech news studio background for 'Tech News Digest' channel.
Professional blue gradient with subtle circuit board patterns and geometric shapes.
Clean, minimalist, high-tech aesthetic suitable for news channel intro.
16:9 horizontal format (1792x1024).
Dark blue to light blue gradient.
No text, leave space for title overlay.
Photorealistic, professional lighting.
"""

intro_image = gen.generate(
    prompt=intro_prompt,
    size="1792x1024",
    quality="hd",
)

print(f"Intro image: {intro_image.local_path}")
print(f"Cost: ${intro_image.total_cost:.2f}")
```

**실행**:
```bash
python scripts/generate_intro_outro.py --type intro
```

**체크포인트**:
- [ ] 스크립트 작성 완료
- [ ] 인트로 이미지 생성 ($0.12)
- [ ] 이미지 확인 및 승인
- [ ] `resources/intro_background.png`로 저장

#### 🔲 3.3 아웃트로 이미지 생성 (DALL-E)
**프롬프트**:
```
Minimalist thank you background for tech news channel.
Simple blue gradient with space for 'Subscribe' call-to-action.
Professional and clean design suitable for video outro.
16:9 horizontal format (1792x1024).
Light and friendly aesthetic.
No text, leave space for message overlay.
```

**실행**:
```bash
python scripts/generate_intro_outro.py --type outro
```

**체크포인트**:
- [ ] 아웃트로 이미지 생성 ($0.12)
- [ ] 이미지 확인 및 승인
- [ ] `resources/outro_background.png`로 저장

#### 🔲 3.4 VideoComposer에 이미지 기반 인트로 구현
**파일**: `src/video/composition/video_composer.py`

**수정 위치**: `_create_intro_clip()` 메서드

**구현 로직**:
```python
def _create_intro_clip(self, config: VideoProjectConfig) -> VideoClip:
    # 1. 커스텀 이미지 또는 기본 이미지 사용
    if config.intro_image_path and config.intro_image_path.exists():
        intro_bg = ImageClip(str(config.intro_image_path))
    else:
        # 기본 이미지 (resources/intro_background.png)
        default_intro = Path("resources/intro_background.png")
        if default_intro.exists():
            intro_bg = ImageClip(str(default_intro))
        else:
            # 폴백: ColorClip
            intro_bg = ColorClip(
                size=(config.width, config.height),
                color=self._hex_to_rgb(config.primary_color),
                duration=config.intro_duration,
            )

    # 2. 이미지 설정
    intro_bg = intro_bg.with_duration(config.intro_duration)
    intro_bg = intro_bg.resized(width=config.width, height=config.height)

    # 3. 텍스트 오버레이 (기존 코드 유지)
    # ... (한글 폰트 적용된 텍스트)

    # 4. 합성
    return CompositeVideoClip([intro_bg, title_clip])
```

**테스트**:
- [ ] 커스텀 이미지 있을 때
- [ ] 기본 이미지 사용
- [ ] 폴백 ColorClip

**체크포인트**:
- [ ] 코드 수정 완료
- [ ] 테스트 영상 생성
- [ ] 인트로 이미지 정상 표시
- [ ] 켈리님 컨펌

#### 🔲 3.5 VideoComposer에 이미지 기반 아웃트로 구현
**파일**: `src/video/composition/video_composer.py`

**수정 위치**: `_create_outro_clip()` 메서드

**구현**: 3.4와 동일한 로직

**체크포인트**:
- [ ] 코드 수정 완료
- [ ] 테스트 영상 생성
- [ ] 아웃트로 이미지 정상 표시
- [ ] 켈리님 컨펌

#### 🔲 3.6 전체 통합 테스트
- [ ] 웹 UI에서 새 영상 생성
- [ ] 인트로 커스텀 이미지 확인
- [ ] 아웃트로 커스텀 이미지 확인
- [ ] 전체 영상 품질 확인
- [ ] 켈리님 최종 승인

---

## 📝 Task 4: 배경 음악 시스템

### 목표
인트로 3초 구간에만 배경 음악 5% 볼륨으로 재생

### Sub-Tasks

#### 🔲 4.1 배경 음악 파일 준비
**옵션 A**: 무료 음원 다운로드
- YouTube Audio Library
- Pixabay Music
- Incompetech

**옵션 B**: AI 생성 (Suno AI, 선택)

**요구사항**:
- MP3 포맷
- 3초 이상 길이
- Energetic, upbeat 분위기
- 저작권 Free

**저장 위치**: `resources/background_music.mp3`

**체크포인트**:
- [ ] 배경 음악 파일 준비
- [ ] 저작권 확인
- [ ] 파일 저장 완료
- [ ] 켈리님 음악 승인

#### 🔲 4.2 VideoProjectConfig에 배경 음악 설정 추가
**파일**: `src/video/models.py`

```python
class VideoProjectConfig(BaseModel):
    # 기존 필드...

    # 배경 음악
    background_music_path: Optional[Path] = Field(
        default=Path("resources/background_music.mp3"),
        description="배경 음악 파일 경로"
    )
    background_music_volume: float = Field(
        default=0.05,  # 5%
        ge=0.0,
        le=1.0,
        description="배경 음악 볼륨 (0.0-1.0)"
    )
    use_background_music: bool = Field(
        default=True,
        description="배경 음악 사용 여부"
    )
```

**체크포인트**:
- [ ] 코드 수정 완료
- [ ] 테스트 통과

#### 🔲 4.3 인트로에 배경 음악 통합
**파일**: `src/video/composition/video_composer.py`

**중요**: 볼륨 조정 → Trim 순서 (Daily English Mecca 패턴)

```python
def _create_intro_clip(self, config: VideoProjectConfig) -> VideoClip:
    # ... (기존 인트로 생성 코드)

    # 배경 음악 추가
    if config.use_background_music and config.background_music_path.exists():
        bg_music = AudioFileClip(str(config.background_music_path))

        # ⚠️ 중요: 볼륨 조정을 먼저!
        bg_music = bg_music.with_volume_scaled(config.background_music_volume)

        # 그 다음 trim (3초)
        bg_music = bg_music.with_subclipped(0, min(config.intro_duration, bg_music.duration))

        # 인트로 클립에 오디오 추가
        intro_clip = intro_clip.with_audio(bg_music)

    return intro_clip
```

**테스트**:
- [ ] 배경 음악이 재생되는지 확인
- [ ] 볼륨이 적절한지 확인 (너무 크지 않음)
- [ ] 3초 후 음악 종료 확인

**체크포인트**:
- [ ] 코드 수정 완료
- [ ] 테스트 영상 생성
- [ ] 배경 음악 정상 재생
- [ ] 볼륨 적절
- [ ] 켈리님 컨펌

#### 🔲 4.4 전체 통합 테스트
- [ ] 웹 UI에서 새 영상 생성
- [ ] 인트로 배경 음악 확인
- [ ] 뉴스 오디오 나레이션 확인 (배경 음악 없음)
- [ ] 전체 오디오 믹싱 품질 확인
- [ ] 켈리님 최종 승인

---

## 📝 Task 6: 한국어 TTS 지원 (Google Cloud)

### 목표
OpenAI TTS 대신 Google Cloud TTS로 한국어 음성 생성

### 사전 요구사항
- [ ] Google Cloud 계정
- [ ] TTS API 활성화
- [ ] 인증 키 발급

### Sub-Tasks

#### 🔲 6.1 Google Cloud TTS 설정
- [ ] Google Cloud Console에서 프로젝트 생성
- [ ] Cloud Text-to-Speech API 활성화
- [ ] 서비스 계정 생성 및 키 다운로드
- [ ] 환경 변수 설정 (`GOOGLE_APPLICATION_CREDENTIALS`)

**비용**:
- 무료 할당량: 월 100만 글자
- 초과 시: $4.00 / 100만 글자

**체크포인트**:
- [ ] API 활성화 완료
- [ ] 인증 키 다운로드 완료
- [ ] 켈리님 계정 설정 확인

#### 🔲 6.2 Google TTS Generator 구현
**파일**: `src/core/ai_services/google_tts_generator.py` (새로 생성)

```python
from google.cloud import texttospeech

class GoogleTTSGenerator:
    def generate(self, text: str, language: str = "ko-KR") -> GeneratedAudio:
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            name="ko-KR-Wavenet-A",  # 여성 음성
            # 또는 "ko-KR-Wavenet-C" (남성 음성)
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        # 저장 및 반환
        # ...
```

**체크포인트**:
- [ ] 클래스 구현 완료
- [ ] 테스트 통과
- [ ] 한국어 음성 생성 확인

#### 🔲 6.3 언어 감지 및 자동 전환
**파일**: `src/automation/pipeline.py`

```python
def _detect_language(self, text: str) -> str:
    """한글/영어 자동 감지"""
    korean_chars = sum(1 for c in text if 0xAC00 <= ord(c) <= 0xD7A3)
    return "ko" if korean_chars > len(text) * 0.3 else "en"

def generate_audio(self, text: str):
    lang = self._detect_language(text)

    if lang == "ko":
        # Google TTS 사용
        return self.google_tts.generate(text, language="ko-KR")
    else:
        # OpenAI TTS 사용 (기존)
        return self.openai_tts.generate(text)
```

**체크포인트**:
- [ ] 언어 감지 로직 구현
- [ ] 자동 전환 테스트
- [ ] 켈리님 컨펌

#### 🔲 6.4 전체 테스트
- [ ] 한국어 뉴스로 영상 생성
- [ ] 한국어 TTS 정상 작동
- [ ] 음질 확인
- [ ] 영어 뉴스로 영상 생성
- [ ] 영어 TTS 정상 작동 (OpenAI)
- [ ] 켈리님 최종 승인

---

## 🎯 작업 진행 방식

### 단계별 워크플로우

**각 Sub-Task마다**:
1. ✅ Claude가 코드 작성 및 설명
2. 🧪 Claude가 테스트 실행 (가능한 경우)
3. 📋 체크박스에 ✅ 표시
4. 👤 **켈리님 컨펌 요청**
5. ✅ 승인 받으면 다음 Sub-Task
6. ❌ 문제 있으면 수정 후 재테스트

**각 Main Task 완료 후**:
1. 🎬 전체 통합 테스트 (영상 생성)
2. 📹 영상 확인
3. 👤 **켈리님 최종 승인**
4. ✅ 다음 Task로 진행

---

## 📊 현재 진행 상황

| Task | 상태 | 진행률 | 예상 시간 |
|------|------|--------|-----------|
| Task 1: 한글 폰트 | ✅ 완료 | 100% | - |
| Task 2: 실제 테스트 | ⏳ 대기 | 0% | 30분 |
| Task 3: 인트로/아웃트로 | ⏳ 대기 | 0% | 2-3시간 |
| Task 4: 배경 음악 | ⏳ 대기 | 0% | 1-2시간 |
| Task 5: 이미지 재사용 | ✅ 완료 | 100% | - |
| Task 6: 한국어 TTS | ⏳ 대기 | 0% | 2-3시간 |

**다음 작업**: Task 2.1 - Docker 재시작

---

**마지막 업데이트**: 2025-10-19
**버전**: 2.0
**작성**: Claude
**승인**: Kelly님 확인 대기
