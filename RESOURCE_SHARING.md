# 리소스 공유 시스템 (Resource Sharing System)

**버전**: 2.0
**적용일**: 2025-10-11
**담당자**: Kelly & Claude Code

---

## 📌 개요

IT News Flux 프로젝트에 **프로젝트 간 리소스 공유 시스템**이 도입되었습니다.

### 왜 필요한가?

**문제점:**
- daily-english-mecca와 itnews-flux가 각각 독립적으로 리소스 저장
- 동일한 DALL-E 이미지나 TTS 음성을 중복 생성 → API 비용 낭비
- 프로젝트마다 수백 MB 리소스 중복 저장

**해결책:**
- **공유 리소스 풀**: `~/ContentCreatorResources/`
- **MD5 해시 기반 캐싱**: 동일 프롬프트/텍스트는 재사용
- **프로젝트별 격리**: 각 프로젝트의 작업 공간은 독립 유지

**효과:**
- OpenAI API 비용 30-50% 절감 예상
- 저장 공간 효율화 (중복 제거)
- 빠른 비디오 생성 (캐시 히트 시)

---

## 🏗️ 아키텍처

### 디렉토리 구조

```
~/ContentCreatorResources/          # 공유 리소스 풀 (프로젝트 외부)
├── cache/                           # MD5 기반 캐시
│   ├── images/                      # DALL-E 이미지 캐시
│   │   └── a3b2c1d4e5f6...png      # MD5 해시 파일명
│   ├── audio/                       # TTS 음성 캐시
│   │   └── f6e5d4c3b2a1...mp3
│   └── fonts/                       # 폰트 캐시
│
├── library/                         # 재사용 가능한 라이브러리
│   ├── backgrounds/                 # 배경 이미지
│   ├── music/                       # 배경 음악
│   │   ├── energetic/
│   │   ├── calm/
│   │   └── upbeat/
│   └── effects/                     # 효과음
│
└── templates/                       # 프로젝트별 템플릿
    ├── daily-english-mecca/
    └── itnews-flux/

./itnews-flux/                       # 프로젝트 로컬 (Git 저장소)
├── output/                          # 프로젝트 작업 공간
│   ├── projects/                    # 프로젝트별 작업 폴더
│   │   └── 20251011_153045/
│   │       ├── project.json         # 프로젝트 메타데이터
│   │       └── clips/               # 임시 클립 파일
│   └── videos/                      # 최종 비디오 출력
│       └── 20251011_153045.mp4
│
├── .resource_config.json            # 리소스 설정 파일 (새로 추가됨)
└── src/core/resource_manager.py     # 리소스 관리자 (새로 추가됨)
```

### 3-Tier 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: 공유 리소스 풀 (~/ContentCreatorResources/)       │
│ - 프로젝트 간 공유                                          │
│ - MD5 해시 기반 캐싱                                        │
│ - API 비용 절감                                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Tier 2: 프로젝트 작업 공간 (./output/projects/)            │
│ - 프로젝트별 격리                                           │
│ - 임시 파일 생성                                            │
│ - 클립 조합                                                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Tier 3: 최종 출력 (./output/videos/)                       │
│ - 완성된 비디오                                             │
│ - 유튜브 업로드 준비                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 사용 방법

### 1. ResourceManager 초기화

```python
from src.core.resource_manager import get_resource_manager

# 싱글톤 인스턴스 가져오기
resource_manager = get_resource_manager("itnews-flux")
```

### 2. 이미지 캐싱 활용

**기존 코드 (캐싱 없음):**
```python
# src/ai/image_generator.py
def generate_news_thumbnail(headline: str):
    prompt = f"Tech news thumbnail: {headline}"
    image_url = openai.Image.create(prompt=prompt)  # 매번 API 호출
    image_path = f"output/images/{uuid4()}.png"     # 랜덤 저장
    download_image(image_url, image_path)
    return image_path
```

**새 코드 (캐싱 적용):**
```python
# src/ai/image_generator.py
from src.core.resource_manager import get_resource_manager

def generate_news_thumbnail(headline: str):
    resource_manager = get_resource_manager("itnews-flux")
    prompt = f"Tech news thumbnail: {headline}"

    # 1. 캐시 확인
    cache_path = resource_manager.get_cached_image_path(prompt)

    if resource_manager.cache_exists(cache_path):
        print(f"✓ 이미지 캐시 히트: {cache_path.name}")
        return cache_path

    # 2. 캐시 미스 → API 호출
    print(f"✗ 이미지 캐시 미스 → DALL-E 생성")
    image_url = openai.Image.create(prompt=prompt)
    download_image(image_url, cache_path)

    # 3. 프로젝트에 리소스 참조 추가 (선택사항)
    resource_manager.add_resource_to_project(
        video_id=current_video_id,
        resource_type="image",
        resource_path=cache_path,
        metadata={"prompt": prompt, "source": "dall-e-3"}
    )

    return cache_path
```

### 3. TTS 음성 캐싱

**기존 코드:**
```python
# src/ai/tts_generator.py
def generate_narration(text: str, voice: str = "nova"):
    audio_data = openai.Audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    audio_path = f"output/audio/{uuid4()}.mp3"
    audio_data.stream_to_file(audio_path)
    return audio_path
```

**새 코드:**
```python
# src/ai/tts_generator.py
from src.core.resource_manager import get_resource_manager

def generate_narration(text: str, voice: str = "nova"):
    resource_manager = get_resource_manager("itnews-flux")

    # 1. 캐시 확인
    cache_path = resource_manager.get_cached_audio_path(text, voice)

    if resource_manager.cache_exists(cache_path):
        print(f"✓ 음성 캐시 히트: {cache_path.name}")
        return cache_path

    # 2. 캐시 미스 → TTS 생성
    print(f"✗ 음성 캐시 미스 → TTS 생성")
    audio_data = openai.Audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    audio_data.stream_to_file(cache_path)

    return cache_path
```

### 4. 배경 음악 가져오기

```python
# src/video/background_music.py
from src.core.resource_manager import get_resource_manager

def get_background_music(mood: str = "upbeat"):
    resource_manager = get_resource_manager("itnews-flux")

    # 공유 라이브러리에서 배경음악 가져오기
    music_files = resource_manager.get_library_music(mood=mood)

    if not music_files:
        print(f"⚠️ {mood} 음악 없음, 기본 음악 사용")
        return None

    # 랜덤 선택 또는 순차 선택
    return random.choice(music_files)
```

### 5. 프로젝트 생성 및 관리

```python
# src/video/video_creator.py
from src.core.resource_manager import get_resource_manager

def create_news_video(news_data: dict):
    resource_manager = get_resource_manager("itnews-flux")

    # 1. 프로젝트 생성
    video_id = resource_manager.create_project()
    print(f"✓ 프로젝트 생성: {video_id}")

    # 2. 작업 공간 가져오기
    project_dir = resource_manager.get_project_dir(video_id)
    clips_dir = project_dir / "clips"

    # 3. 클립 생성 (임시 파일은 작업 공간에)
    for i, segment in enumerate(news_data['segments']):
        clip_path = clips_dir / f"segment_{i}.mp4"
        create_segment_clip(segment, clip_path)

    # 4. 최종 비디오 출력 경로
    output_path = resource_manager.get_video_output_path(video_id)

    # 5. 비디오 합성
    concatenate_clips(clips_dir, output_path)

    return output_path
```

---

## 📊 통계 및 모니터링

### 리소스 사용량 확인

```python
from src.core.resource_manager import get_resource_manager

resource_manager = get_resource_manager("itnews-flux")
stats = resource_manager.get_stats()

print(f"공유 리소스:")
print(f"  - 캐시된 이미지: {stats['shared_resources']['cached_images']}개")
print(f"  - 캐시된 오디오: {stats['shared_resources']['cached_audio']}개")
print(f"  - 라이브러리 음악: {stats['shared_resources']['library_music']}개")

print(f"\n프로젝트:")
print(f"  - 총 프로젝트: {stats['projects']['total']}개")
print(f"  - 진행 중: {stats['projects']['in_progress']}개")
print(f"  - 완료: {stats['projects']['completed']}개")

print(f"\n저장 공간:")
print(f"  - 캐시: {stats['storage']['cache_size_mb']} MB")
print(f"  - 라이브러리: {stats['storage']['library_size_mb']} MB")
print(f"  - 프로젝트: {stats['storage']['projects_size_mb']} MB")
print(f"  - 비디오: {stats['storage']['videos_size_mb']} MB")
```

### 오래된 프로젝트 정리

```bash
# Dry run (시뮬레이션)
python -c "
from src.core.resource_manager import get_resource_manager
rm = get_resource_manager('itnews-flux')
rm.cleanup_old_projects(older_than_days=30, dry_run=True)
"

# 실제 삭제
python -c "
from src.core.resource_manager import get_resource_manager
rm = get_resource_manager('itnews-flux')
rm.cleanup_old_projects(older_than_days=30, dry_run=False)
"
```

---

## 🔑 API 메서드 레퍼런스

### ResourceManager 클래스

```python
class ResourceManager:
    def __init__(self, project_name: str = "itnews-flux", config_path: Optional[str] = None)
        """ResourceManager 초기화"""

    # === 캐시 관리 ===
    def get_cached_image_path(self, prompt: str) -> Path
        """이미지 캐시 경로 반환 (MD5 해시 기반)"""

    def get_cached_audio_path(self, sentence: str, voice: str = "nova") -> Path
        """오디오 캐시 경로 반환 (MD5 해시 기반)"""

    def cache_exists(self, cache_path: Path) -> bool
        """캐시 파일 존재 여부 확인"""

    # === 프로젝트 관리 ===
    def create_project(self, video_id: Optional[str] = None) -> str
        """새 프로젝트 생성 (타임스탬프 기반 ID)"""

    def get_project_dir(self, video_id: str) -> Path
        """프로젝트 디렉토리 경로 반환"""

    def get_video_output_path(self, video_id: str) -> Path
        """최종 비디오 출력 경로 반환"""

    def add_resource_to_project(self, video_id: str, resource_type: str,
                                resource_path: Path, metadata: Optional[Dict] = None)
        """프로젝트에 리소스 참조 추가 (추적 목적)"""

    # === 라이브러리 관리 ===
    def get_library_music(self, mood: str = "energetic") -> List[Path]
        """라이브러리에서 배경음악 가져오기"""

    def copy_to_library(self, source_path: Path, category: str, subcategory: Optional[str] = None)
        """파일을 라이브러리로 복사"""

    # === 통계 & 정리 ===
    def get_stats(self) -> Dict
        """리소스 통계 반환"""

    def cleanup_old_projects(self, older_than_days: int = 30, dry_run: bool = True)
        """오래된 프로젝트 정리"""
```

### 편의 함수

```python
def get_resource_manager(project_name: str = "itnews-flux") -> ResourceManager
    """싱글톤 ResourceManager 인스턴스 반환"""
```

---

## 🔄 마이그레이션 가이드 (기존 코드 적용)

### Step 1: Import 추가

```python
# 모든 AI 서비스 파일에 추가
from src.core.resource_manager import get_resource_manager
```

### Step 2: 초기화

```python
# 파일 상단 또는 __init__ 메서드에서
resource_manager = get_resource_manager("itnews-flux")
```

### Step 3: 기존 경로를 캐시 경로로 교체

**Before:**
```python
image_path = f"output/images/{uuid4()}.png"
audio_path = f"output/audio/{uuid4()}.mp3"
```

**After:**
```python
image_path = resource_manager.get_cached_image_path(prompt)
audio_path = resource_manager.get_cached_audio_path(text, voice)
```

### Step 4: 파일 생성 전 캐시 확인

```python
if not resource_manager.cache_exists(image_path):
    # API 호출하여 생성
    generate_image(prompt, image_path)
else:
    print(f"✓ 캐시 히트: {image_path.name}")
```

### Step 5: 프로젝트 생성 로직 통합

```python
# OLD:
video_id = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs(f"output/projects/{video_id}")

# NEW:
video_id = resource_manager.create_project()
project_dir = resource_manager.get_project_dir(video_id)
```

---

## 💡 Best Practices

### 1. 항상 싱글톤 사용
```python
# ✓ GOOD
resource_manager = get_resource_manager("itnews-flux")

# ✗ BAD (매번 새 인스턴스 생성)
resource_manager = ResourceManager("itnews-flux")
```

### 2. 캐시 히트 로깅
```python
if resource_manager.cache_exists(cache_path):
    print(f"✓ 캐시 히트: {cache_path.name} (API 비용 절감)")
    return cache_path
```

### 3. 프로젝트 리소스 추적 (선택사항)
```python
# 디버깅 및 감사(audit) 목적으로 추천
resource_manager.add_resource_to_project(
    video_id=video_id,
    resource_type="image",
    resource_path=cache_path,
    metadata={"prompt": prompt}
)
```

### 4. 정기적인 통계 확인
```bash
# 주간 리포트 생성
python scripts/resource_report.py
```

---

## 🐛 트러블슈팅

### 문제 1: "Permission denied" 오류
**원인**: `~/ContentCreatorResources/` 디렉토리 권한 문제

**해결**:
```bash
chmod -R 755 ~/ContentCreatorResources
```

### 문제 2: 캐시 히트가 예상보다 낮음
**원인**: 프롬프트 문자열이 미묘하게 다름 (공백, 줄바꿈 등)

**해결**: 프롬프트 정규화
```python
def normalize_prompt(prompt: str) -> str:
    return " ".join(prompt.strip().split())

prompt = normalize_prompt(user_input)
cache_path = resource_manager.get_cached_image_path(prompt)
```

### 문제 3: 디스크 공간 부족
**원인**: 오래된 캐시 파일 누적

**해결**: 자동 정리 활성화
```json
// .resource_config.json
{
  "auto_cleanup": {
    "enabled": true,
    "older_than_days": 30
  }
}
```

---

## 📈 예상 효과

### API 비용 절감
- **현재 (캐싱 없음)**: 매 비디오마다 DALL-E 3 API 호출 ($0.04/이미지)
- **캐싱 적용 후**: 동일 프롬프트 재사용 시 API 호출 없음
- **예상 절감**: 월 30-50% (프로젝트 간 공유 효과)

### 성능 향상
- **이미지 생성**: 10-15초 → 0.1초 (캐시 히트 시)
- **음성 생성**: 3-5초 → 0.1초 (캐시 히트 시)
- **전체 비디오 생성**: 5분 → 2-3분 (캐시 히트율 60% 가정)

### 저장 공간 효율
- **이전**: 프로젝트별 중복 저장 (itnews-flux 520MB + daily-english-mecca 548MB = 1.07GB)
- **이후**: 공유 리소스 풀 (약 600MB, 중복 제거)
- **절감률**: 약 44%

---

## 🔗 관련 프로젝트

### daily-english-mecca
- **목적**: YouTube Shorts 영어 학습 비디오
- **포맷**: 9:16 세로
- **리소스 공유**: 동일한 ResourceManager 사용
- **위치**: `/Users/blockmeta/.../KellyGoogleSpace/daily-english-mecca/`

**공유 시나리오 예시:**
1. daily-english-mecca에서 "Technology news headline" 이미지 생성
2. itnews-flux에서 동일한 프롬프트 사용 시 캐시 히트 → API 비용 절감

---

## 📚 추가 자료

- **설정 파일**: `.resource_config.json` - 리소스 풀 경로 설정
- **소스 코드**: `src/core/resource_manager.py` - ResourceManager 구현
- **통합 가이드**: 이 문서
- **관련 문서**: `daily-english-mecca/CLAUDE.md` - 원본 프로젝트 컨텍스트

---

## ❓ FAQ

**Q1: 기존 코드를 모두 수정해야 하나요?**
A: 아니오. 점진적으로 적용 가능합니다. 기존 코드는 그대로 작동하며, 새 기능 개발 시 ResourceManager를 사용하세요.

**Q2: 다른 프로젝트가 추가되면?**
A: 동일한 `.resource_config.json`을 복사하고 `get_resource_manager("새-프로젝트-이름")`을 호출하면 됩니다.

**Q3: 캐시를 수동으로 삭제해도 되나요?**
A: 네. `~/ContentCreatorResources/cache/` 폴더를 안전하게 삭제 가능합니다. 다음 생성 시 자동으로 재생성됩니다.

**Q4: 웹 버전에서 Electron 데스크탑으로 마이그레이션 시?**
A: ResourceManager는 플랫폼 독립적입니다. 코드 변경 없이 작동합니다.

---

**문의사항**: GitHub Issues 또는 Kelly에게 직접 연락

**마지막 업데이트**: 2025-10-11
