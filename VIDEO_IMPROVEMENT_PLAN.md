# 영상 제작 시스템 개선 계획

**작성일**: 2025-10-19
**담당자**: Kelly & Claude Code
**목적**: 한글 지원 강화 및 인트로/아웃트로 개선

---

## 🎯 개선 목표

### 현재 문제점
1. ❌ **한글 폰트 깨짐**: Lower Third 자막에서 한글이 깨져서 표시됨
2. ❌ **영어 음성만 지원**: TTS가 영어로만 생성됨 (한글 뉴스도 영어 음성)
3. ❌ **단순한 인트로/아웃트로**: 단색 배경 + 텍스트만 있음 (이미지/로고 없음)

### 개선 목표
1. ✅ **한글 폰트 정상 표시**: AppleSDGothicNeo 또는 Nanum 폰트 사용
2. ✅ **한국어 음성 지원**: 한글 뉴스는 한국어 TTS로 생성
3. ✅ **전문적인 인트로/아웃트로**: 로고, 배경 이미지, 애니메이션 추가

---

## 📊 현재 상태 분석

### 1. 한글 폰트 문제 원인

**코드 위치**: `src/video/layout/lower_third.py:159-185`

```python
def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
    # 현재: 한글 폰트가 포함되지 않은 시스템 폰트만 시도
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",  # macOS (영어만)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux (영어만)
        "C:\\Windows\\Fonts\\arial.ttf",  # Windows (영어만)
    ]
```

**문제**:
- 위 폰트들은 **한글 글리프(glyph)가 없음**
- 한글 문자가 입력되면 → 폰트에서 렌더링 불가 → 깨진 문자(□□□) 표시

**해결 방안**:
- macOS: `AppleSDGothicNeo.ttc` 또는 `NanumGothic.ttc` 사용
- Linux: `Noto Sans CJK KR` 사용
- Windows: `Malgun Gothic` 사용

### 2. TTS 언어 문제

**코드 위치**: `src/core/ai_services/tts_generator.py`

```python
# 현재: 모든 뉴스를 영어 음성으로 생성
audio = self.client.audio.speech.create(
    model=model,
    voice=voice,
    input=text,  # 항상 영어 스크립트
)
```

**문제**:
- OpenAI TTS는 **영어 음성만 지원** (한글 텍스트 입력 시 영어 발음으로 읽음)
- 한글 뉴스도 영어 음성으로 읽힘 → 부자연스러움

**해결 방안**:
- **옵션 1**: Google Cloud TTS 추가 (한국어 음성 지원)
- **옵션 2**: Azure TTS 추가 (한국어 음성 지원)
- **옵션 3**: ElevenLabs TTS (다국어 지원, 프리미엄)
- **추천**: Google Cloud TTS (무료 할당량 + 고품질)

### 3. 인트로/아웃트로 단순함

**코드 위치**: `src/video/composition/video_composer.py:240-311`

```python
def _create_intro_clip(self, config: VideoProjectConfig) -> VideoClip:
    # 현재: 단색 배경 + 텍스트만
    intro_clip = ColorClip(
        size=(config.width, config.height),
        color=self._hex_to_rgb(config.primary_color),
        duration=config.intro_duration,
    )
```

**문제**:
- 단색 배경만 사용 (이미지/로고 없음)
- 정적 텍스트만 (애니메이션 없음)
- 브랜딩 요소 부족

**개선 방안**:
- 배경 이미지 추가 (DALL-E로 생성 또는 템플릿 사용)
- 로고 애니메이션 (Fade In + Scale)
- 텍스트 애니메이션 (Slide In + Fade)
- 배경 음악 추가 (옵션)

---

## 🛠️ 구현 계획

### Phase 1: 한글 폰트 수정 (우선순위: 최고)

**작업 내용**:
1. `lower_third.py` 폰트 로딩 로직 수정
2. 한글 폰트 자동 감지 및 로드
3. 폰트 폴백 체인 구축 (한글 → 영어 → 기본)
4. 테스트 및 검증

**예상 소요 시간**: 30분

**수정 파일**:
- `src/video/layout/lower_third.py`

**테스트 방법**:
```bash
python -c "
from src.video.layout.lower_third import LowerThirdGenerator
from src.video.models import VideoProjectConfig, LowerThirdConfig

config = VideoProjectConfig()
generator = LowerThirdGenerator(config)
lt_config = LowerThirdConfig(
    primary_text='Breaking News: AI Technology',
    secondary_text='속보: 인공지능 기술 발전'
)
image = generator.generate(lt_config, Path('output/test_korean_font.png'))
print('✅ 한글 폰트 테스트 완료')
"
```

---

### Phase 2: 한국어 TTS 지원 (우선순위: 중)

**작업 내용**:
1. Google Cloud TTS 통합
2. 언어 자동 감지 (한글 뉴스 → 한국어 TTS)
3. 음성 모델 선택 로직 추가
4. 비용 추적 업데이트

**예상 소요 시간**: 1-2시간

**필요 사항**:
- Google Cloud 계정 (무료 할당량: 월 100만 자)
- Google Cloud TTS API 활성화
- 서비스 계정 키 발급

**옵션**:
- **즉시 구현**: OpenAI TTS 유지 (영어만)
- **향후 구현**: Google Cloud TTS 추가 (한국어 지원)

**추천**: 향후 구현 (일단 영어 음성으로 진행)

---

### Phase 3: 인트로/아웃트로 개선 (우선순위: 중)

**작업 내용**:
1. 인트로/아웃트로 디자인 설계
2. 배경 이미지 생성 또는 준비
3. 로고 제작 (DALL-E 또는 Canva)
4. 애니메이션 효과 추가
5. 배경 음악 추가 (옵션)

**예상 소요 시간**: 2-3시간

**디자인 아이디어**:

#### 인트로 (3초)
```
┌─────────────────────────────────┐
│                                 │
│   [로고 이미지]                 │
│   Tech News Digest              │
│   IT 뉴스 요약                  │
│                                 │
│   Fade In + Scale 애니메이션    │
└─────────────────────────────────┘
```

#### 아웃트로 (3초)
```
┌─────────────────────────────────┐
│                                 │
│   구독 & 좋아요 부탁드립니다!   │
│   Subscribe for more!           │
│                                 │
│   [QR 코드 or 채널 링크]        │
└─────────────────────────────────┘
```

**수정 파일**:
- `src/video/composition/video_composer.py`

**리소스 필요**:
- 로고 이미지 (PNG, 투명 배경)
- 배경 이미지 (1920x1080, DALL-E 생성 가능)
- 배경 음악 (MP3, 옵션, 저작권 Free)

---

## 📅 구현 순서 (권장)

### 🔥 즉시 작업 (오늘)
1. **Phase 1: 한글 폰트 수정** (30분)
   - 가장 시급한 문제
   - 빠르게 수정 가능
   - 즉시 효과 확인 가능

### 📅 단기 작업 (이번 주)
2. **Phase 3: 인트로/아웃트로 개선** (2-3시간)
   - 로고 디자인 (DALL-E 또는 Canva)
   - 배경 이미지 준비
   - 애니메이션 효과 추가

### 🚀 장기 작업 (다음 주)
3. **Phase 2: 한국어 TTS 지원** (1-2시간)
   - Google Cloud 설정 필요
   - 비용 검토 필요
   - 선택적 기능

---

## 💰 비용 분석

### 현재 비용 (영상당)
```
스크립트 (GPT-4o):     $0.007
이미지 (DALL-E 3):     $0.080
음성 (OpenAI TTS):     $0.0075
─────────────────────────────
총 비용:               $0.023 (약 30원)
```

### 개선 후 예상 비용

#### 옵션 1: Google Cloud TTS 사용
```
스크립트:              $0.007
이미지:                $0.080
음성 (Google TTS):     $0.004  (저렴!)
인트로 로고 (1회):     $0.080  (재사용)
─────────────────────────────
총 비용:               $0.011 + 로고(1회)
```

#### 옵션 2: OpenAI TTS 유지
```
스크립트:              $0.007
이미지:                $0.080
음성 (OpenAI TTS):     $0.0075
인트로 로고 (1회):     $0.080  (재사용)
─────────────────────────────
총 비용:               $0.023 + 로고(1회)
```

**결론**: Google Cloud TTS 사용 시 오히려 비용 절감!

---

## 🎨 디자인 가이드

### 색상 팔레트
```
Primary:    #0066cc (파란색 - 신뢰감)
Secondary:  #003d7a (진한 파란색 - 전문성)
Accent:     #00cc66 (녹색 - 기술)
Background: #f5f5f5 (밝은 회색)
Text:       #1a1a1a (거의 검정)
```

### 폰트 가이드
```
영어:
- 제목: Arial Bold / Helvetica Bold
- 본문: Arial / Helvetica

한글:
- 제목: Apple SD Gothic Neo Bold / Nanum Gothic Bold
- 본문: Apple SD Gothic Neo Regular / Nanum Gothic

크기:
- 인트로 제목: 80px
- Lower Third 주제목: 48px
- Lower Third 부제목: 32px
```

### 애니메이션 타이밍
```
Fade In:    0.5초
Fade Out:   0.5초
Hold:       2초
Total:      3초 (인트로/아웃트로)
```

---

## ✅ 체크리스트

### Phase 1: 한글 폰트 수정
- [ ] `lower_third.py` 한글 폰트 경로 추가
- [ ] 폰트 폴백 로직 구현
- [ ] 한글 텍스트 테스트
- [ ] 영어+한글 혼합 텍스트 테스트
- [ ] 로그 확인 (폰트 로딩 성공 여부)
- [ ] 실제 영상 생성 테스트

### Phase 2: 한국어 TTS (선택)
- [ ] Google Cloud 계정 생성
- [ ] Cloud TTS API 활성화
- [ ] 서비스 계정 키 발급
- [ ] `tts_generator.py` 언어 감지 로직 추가
- [ ] Google TTS 클라이언트 통합
- [ ] 한국어 음성 테스트
- [ ] 비용 추적 업데이트

### Phase 3: 인트로/아웃트로 개선
- [ ] 로고 디자인 (DALL-E 프롬프트 작성)
- [ ] 로고 이미지 생성
- [ ] 배경 이미지 준비
- [ ] 인트로 클립 개선 (이미지 + 애니메이션)
- [ ] 아웃트로 클립 개선 (CTA 추가)
- [ ] 배경 음악 추가 (선택)
- [ ] 전체 영상 테스트

---

## 🚀 다음 단계

켈리님께서 선택해주세요:

### 옵션 A: 한글 폰트만 즉시 수정 (추천)
```bash
✅ 즉시 시작 가능
✅ 30분 소요
✅ 바로 효과 확인
```

### 옵션 B: 한글 폰트 + 인트로/아웃트로 개선
```bash
⏰ 3-4시간 소요
🎨 디자인 작업 필요
🎬 완성도 높은 영상
```

### 옵션 C: 전체 개선 (한글 폰트 + TTS + 인트로/아웃트로)
```bash
⏰ 1-2일 소요
💰 Google Cloud 설정 필요
🚀 완벽한 프로덕션 품질
```

---

## 📝 참고 자료

### 한글 폰트 경로
```bash
# macOS
/System/Library/Fonts/AppleSDGothicNeo.ttc
/System/Library/AssetsV2/.../NanumGothic.ttc

# Linux
/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc

# Windows
C:\Windows\Fonts\malgun.ttf
```

### Google Cloud TTS 가격
```
무료 할당량: 월 100만 자 (Standard)
유료: $4 / 100만 자 (Standard)
     $16 / 100만 자 (WaveNet, 고품질)

예상 사용량: 월 3,000자 (매일 1개 영상, 100자)
예상 비용: $0 (무료 할당량 내)
```

### DALL-E 3 로고 생성 프롬프트 예시
```
"Professional tech news channel logo featuring
a modern abstract design with circuit patterns,
blue gradient color scheme, clean and minimalist style,
suitable for YouTube channel branding,
high resolution 1024x1024"
```

---

**마지막 업데이트**: 2025-10-19
**다음 리뷰**: 구현 완료 후
**우선순위**: Phase 1 (한글 폰트) > Phase 3 (인트로/아웃트로) > Phase 2 (한국어 TTS)
