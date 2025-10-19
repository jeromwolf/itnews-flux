# Image Pool System - Quick Reference Guide

## 📊 개요

이미지 풀 시스템은 **DALL-E 비용을 최대 80% 절감**하는 시스템입니다.

### 비용 절감 효과
- **현재 비용**: 월 $7.20 (3 영상/일 × 30일 × $0.08)
- **도입 후 비용**: 월 ~$1.44 (20% 생성, 80% 풀 사용)
- **월간 절감**: ~$5.76
- **연간 절감**: ~$69.12
- **초기 투자**: ~$3.60 (45개 이미지)
- **ROI**: ~15일

---

## 🚀 사용 방법

### 1. 이미지 풀 미리보기 (무료)
```bash
python test_image_pool.py --dry-run
```
- 비용 없음
- 생성될 프롬프트와 예상 비용 확인

### 2. 테스트 풀 생성 (~$0.48)
```bash
python test_image_pool.py --test
```
- AI_ML + SECURITY 카테고리만 생성 (6개 이미지)
- 시스템 검증용

### 3. 선택 로직 테스트 (무료)
```bash
python test_image_pool.py --select
```
- 비용 없음
- 풀 사용/생성 전환 로직 확인

### 4. 전체 풀 생성 (~$3.60)
```bash
python test_image_pool.py --full
```
- 모든 카테고리 생성 (10개 카테고리 × 3개 이미지 = 30개)
- 확인 프롬프트 있음

### 5. 수동 풀 생성 (고급)
```bash
# 특정 카테고리만 생성
python scripts/generate_image_pool.py --categories ai_ml,security,mobile

# 모든 카테고리 생성
python scripts/generate_image_pool.py --categories all

# HD 품질 (2배 비용)
python scripts/generate_image_pool.py --categories all --quality hd

# 다른 스타일
python scripts/generate_image_pool.py --categories all --style natural
```

---

## 📁 구조

### 이미지 풀 위치
```
~/ContentCreatorResources/library/news_images/
├── ai_ml/
│   ├── ai_ml_01.png
│   ├── ai_ml_02.png
│   └── ai_ml_03.png
├── security/
│   ├── security_01.png
│   ├── security_02.png
│   └── security_03.png
└── ... (다른 카테고리들)
```

### 주요 파일
- `scripts/generate_image_pool.py` - 풀 생성 스크립트
- `src/video/image_selector.py` - 이미지 선택 로직
- `test_image_pool.py` - 테스트 스크립트
- `IMAGE_POOL_GUIDE.md` - 본 가이드

---

## 🔧 시스템 통합

### 자동 통합 완료 ✅

이미지 풀은 **이미 파이프라인에 통합**되어 있습니다:

1. **ContentPipeline** (`src/automation/pipeline.py`)
   - `ImageSelector` 사용 (자동)
   - 풀 우선, 없으면 생성

2. **PipelineConfig**
   - `use_image_pool: bool = True` (기본값)
   - 설정으로 on/off 가능

3. **웹 UI** (수동 영상 생성)
   - 자동으로 풀 사용
   - 비용 절감 효과 즉시 적용

### 사용 확인 방법

로그에서 이미지 소스 확인:
```
Image: /path/to/image.png (pool), $0.0000      # 풀 사용 (무료)
Image: /path/to/image.png (generated), $0.0800  # 새로 생성
```

파이프라인 종료 시 통계:
```
📊 Image Pool Statistics:
  Pool usage: 2/3 (67%)
  Savings: $0.1600
  Generation cost: $0.0800
  Categories in pool: 10
  Total pool images: 30
```

---

## 🎯 최적 사용 전략

### 1단계: 소규모 테스트
```bash
# 1. 미리보기
python test_image_pool.py --dry-run

# 2. 테스트 풀 생성 (2개 카테고리)
python test_image_pool.py --test

# 3. 실제 영상 1개 생성해서 테스트
python run_web.py  # 웹 UI에서 영상 생성

# 4. 로그 확인 - 풀 사용 확인
```

### 2단계: 주요 카테고리 확장
```bash
# 가장 많이 사용되는 카테고리 추가
python scripts/generate_image_pool.py --categories ai_ml,security,mobile,startup_funding
```

### 3단계: 전체 시스템 가동
```bash
# 모든 카테고리 생성
python test_image_pool.py --full

# 또는
python scripts/generate_image_pool.py --categories all
```

---

## 📈 모니터링

### 비용 절감 추적

1. **실시간 로그**
   ```bash
   # 파이프라인 실행 시 자동 출력
   tail -f logs/itnews-flux.log | grep "Image Pool Statistics"
   ```

2. **Python에서 확인**
   ```python
   from src.video.image_selector import create_image_selector

   selector = create_image_selector()
   status = selector.get_pool_status()

   print(f"Pool usage: {status['pool_usage_rate']:.0%}")
   print(f"Total savings: ${status['total_savings']:.2f}")
   ```

3. **월간 리포트**
   - 매월 말에 로그 확인
   - 절감 금액 계산
   - 필요시 카테고리 추가

---

## 🔄 풀 업데이트

### 언제 업데이트?
- 새로운 카테고리 추가 시
- 이미지 스타일 변경 시
- 계절별 이미지 변경 (선택사항)

### 방법
```bash
# 특정 카테고리만 재생성
python scripts/generate_image_pool.py --categories ai_ml

# 또는 수동 삭제 후 재생성
rm -rf ~/ContentCreatorResources/library/news_images/ai_ml/
python scripts/generate_image_pool.py --categories ai_ml
```

---

## ⚙️ 설정

### 풀 사용 비활성화
```python
# src/automation/pipeline.py
config = PipelineConfig(
    use_image_pool=False,  # 풀 사용 안 함, 항상 생성
)
```

### 커스텀 풀 디렉토리
```python
from src.video.image_selector import ImageSelector

selector = ImageSelector(
    pool_dir=Path("/custom/path/to/pool"),
    use_pool=True,
)
```

---

## 🐛 트러블슈팅

### 문제: 풀 이미지가 사용되지 않음

**확인 1**: 풀 디렉토리 존재 여부
```bash
ls -la ~/ContentCreatorResources/library/news_images/
```

**확인 2**: 카테고리별 이미지 수
```bash
find ~/ContentCreatorResources/library/news_images/ -name "*.png" | wc -l
```

**확인 3**: 로그에서 풀 상태 확인
```bash
grep "Pool status" logs/itnews-flux.log
```

**해결**:
```bash
# 풀 재생성
python test_image_pool.py --full
```

### 문제: 특정 카테고리 이미지가 항상 생성됨

**원인**: 해당 카테고리가 풀에 없음

**확인**:
```bash
ls ~/ContentCreatorResources/library/news_images/ | grep <category>
```

**해결**:
```bash
# 해당 카테고리 추가
python scripts/generate_image_pool.py --categories <category>
```

### 문제: 이미지 품질이 낮음

**원인**: Standard 품질로 생성됨 (비용 절감)

**해결** (선택):
```bash
# HD 품질로 재생성 (2배 비용)
python scripts/generate_image_pool.py --categories all --quality hd
```

---

## 💡 팁

1. **초기에는 Standard 품질 사용**
   - HD는 2배 비용 ($0.12/이미지)
   - Standard도 충분히 고품질

2. **주요 카테고리부터 시작**
   - AI_ML, SECURITY, MOBILE, STARTUP_FUNDING
   - 가장 자주 사용되는 카테고리

3. **정기적으로 풀 사용률 체크**
   - 80% 이상이면 최적
   - 낮으면 카테고리 추가 고려

4. **계절별 이미지 업데이트 (선택)**
   - 분기별 또는 반기별
   - 최신 트렌드 반영

---

## 📞 문의

문제가 있거나 개선 아이디어가 있다면:
1. GitHub Issues에 등록
2. TASKS.md에 태스크 추가
3. 로그 첨부하여 문의

---

**마지막 업데이트**: 2025-10-19
**버전**: 1.0
**상태**: Production Ready ✅
