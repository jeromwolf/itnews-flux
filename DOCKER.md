# Tech News Digest - Docker 가이드

Docker를 사용하여 Tech News Digest를 실행하는 방법입니다.

## 📋 필수 조건

- Docker Desktop 설치 (macOS/Windows) 또는 Docker Engine (Linux)
- Docker Compose v2.0+
- OpenAI API 키

## 🚀 빠른 시작

### 1. 환경 변수 설정

```bash
# .env.docker를 .env로 복사
cp .env.docker .env

# .env 파일 편집하여 API 키 입력
# OPENAI_API_KEY=your-actual-api-key
```

### 2. Docker 이미지 빌드

```bash
# 이미지 빌드
docker-compose build

# 또는 캐시 없이 빌드
docker-compose build --no-cache
```

### 3. 컨테이너 실행

```bash
# 백그라운드에서 실행
docker-compose up -d

# 또는 포그라운드에서 실행 (로그 확인)
docker-compose up
```

### 4. 접속

브라우저에서 접속:
- 📊 Dashboard: http://localhost:8000/dashboard
- 📰 News: http://localhost:8000/news
- 🎬 Videos: http://localhost:8000/videos
- ⚙️ Settings: http://localhost:8000/settings
- 📚 API Docs: http://localhost:8000/api/docs

## 🔧 유용한 명령어

### 컨테이너 관리

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f web

# 컨테이너 중지
docker-compose stop

# 컨테이너 시작 (이미 생성된 경우)
docker-compose start

# 컨테이너 중지 및 삭제
docker-compose down

# 컨테이너 + 볼륨 삭제 (데이터 초기화)
docker-compose down -v
```

### 개발 모드

```bash
# 소스 코드 변경 시 자동 리로드
docker-compose up --build

# 특정 서비스만 재시작
docker-compose restart web
```

### 쉘 접속

```bash
# 웹 컨테이너 쉘 접속
docker-compose exec web bash

# Python 인터프리터 실행
docker-compose exec web python

# 특정 명령 실행
docker-compose exec web python test_web.py
```

### 데이터 백업

```bash
# 출력 파일 백업
docker cp itnews-flux-web:/app/output ./backup/output

# 로그 백업
docker cp itnews-flux-web:/app/logs ./backup/logs

# 설정 백업
docker cp itnews-flux-web:/app/config ./backup/config
```

## 📦 서비스 구성

### web (메인 애플리케이션)
- 포트: 8000
- 역할: FastAPI 웹 서버
- 볼륨:
  - `./output` - 생성된 영상 파일
  - `./logs` - 로그 파일
  - `./config` - 설정 파일

### redis (캐시)
- 포트: 6379
- 역할: 뉴스 데이터 및 세션 캐싱
- 볼륨: `redis-data` (영구 저장)

## 🔍 트러블슈팅

### 포트 충돌

```bash
# 다른 포트 사용
# docker-compose.yml 수정:
ports:
  - "8001:8000"  # 8001 포트로 변경
```

### 권한 문제

```bash
# 출력 디렉토리 권한 설정
chmod -R 777 output logs config
```

### 빌드 실패

```bash
# 캐시 삭제 후 재빌드
docker-compose build --no-cache

# 이미지 완전 삭제 후 재빌드
docker-compose down --rmi all
docker-compose build
```

### 컨테이너가 계속 재시작

```bash
# 로그 확인
docker-compose logs web

# 헬스체크 상태 확인
docker inspect itnews-flux-web | grep -A 10 Health
```

### Redis 연결 실패

```bash
# Redis 컨테이너 상태 확인
docker-compose ps redis

# Redis 로그 확인
docker-compose logs redis

# Redis 재시작
docker-compose restart redis
```

## 🔐 프로덕션 배포

### 환경 변수

프로덕션 환경에서는 `.env` 파일 대신 시크릿 관리 도구 사용 권장:
- AWS Secrets Manager
- Google Cloud Secret Manager
- HashiCorp Vault
- Docker Secrets (Swarm mode)

### Docker Swarm

```bash
# Swarm 초기화
docker swarm init

# 스택 배포
docker stack deploy -c docker-compose.yml itnews-flux

# 서비스 확인
docker service ls

# 스택 제거
docker stack rm itnews-flux
```

### Kubernetes

Kubernetes 배포를 위한 manifest 파일은 `k8s/` 디렉토리 참조.

## 📊 리소스 제한

`docker-compose.yml`에 리소스 제한 추가:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## 🔄 자동 재시작

```yaml
services:
  web:
    restart: always  # 항상 재시작
    # restart: unless-stopped  # 수동 중지 시 제외
    # restart: on-failure  # 실패 시에만
```

## 📝 로그 관리

```bash
# 로그 크기 제한
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 🌐 역방향 프록시 (Nginx)

Nginx를 프록시로 사용하는 경우:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📞 지원

문제 발생 시:
1. 로그 확인: `docker-compose logs`
2. GitHub Issues: https://github.com/yourusername/itnews-flux/issues
3. Discord 커뮤니티 (예정)

---

**마지막 업데이트**: 2025-10-09
