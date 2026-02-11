# LLM 상태 확인 도구

사내 환경에서 외부 LLM 접속 상태를 실시간으로 확인하는 웹 애플리케이션입니다.

## 주요 기능

### 실시간 상태 모니터링
- **OpenAI GPT-4o** 접속 상태 확인
- **HuggingFace GLM-4.7** 접속 상태 확인
- **Anthropic Claude-3.7-Sonnet** 접속 상태 확인
- **Google Gemini-1.5-Pro** 접속 상태 확인
- 실시간 상태 표시 (초록불/빨간불)
- 응답 시간 측정
- 자동 새로고침 (30초 간격)

### 히스토리 대시보드
- 📊 **최근 24시간 응답시간 그래프** - 모델별 응답 속도를 시계열로 시각화
- 📈 **가동률(uptime %) 통계** - 각 모델의 안정성을 한눈에 확인
- 💾 **SQLite 기반 히스토리 저장** - 가벼운 로컬 DB로 상태 이력 관리
- 📉 **평균/최소/최대 응답시간** - 성능 지표 요약

### Docker 지원
- 🐳 간편한 컨테이너 배포
- 🔄 자동 재시작 및 헬스체크
- 📁 데이터 영구 저장 (볼륨 마운트)

## 빠른 시작

### Docker Compose 사용 (권장)

1. **설정 파일 생성:**
```bash
cp config.yaml.example config.yaml
# config.yaml 편집하여 API 키 입력
```

2. **컨테이너 실행:**
```bash
docker-compose up -d
```

3. **웹 브라우저에서 접속:**
```
http://localhost:9876
```

4. **로그 확인:**
```bash
docker-compose logs -f
```

5. **중지 및 제거:**
```bash
docker-compose down
```

### Docker 직접 사용

```bash
# 이미지 빌드
docker build -t llm-status-checker .

# 컨테이너 실행
docker run -d \
  --name llm-status-checker \
  -p 9876:9876 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/data:/app/data \
  llm-status-checker
```

### Python 직접 실행

1. **의존성 설치:**
```bash
pip install -r requirements.txt
```

2. **설정 파일 수정:**
```bash
cp config.yaml.example config.yaml
# config.yaml 파일에서 API 키 설정
```

예시:
```yaml
models:
  openai:
    enabled: true
    api_key: "sk-..."
  
  huggingface:
    enabled: false
    api_key: "hf_..."
  
  claude:
    enabled: true
    api_key: "sk-ant-..."
  
  gemini:
    enabled: false
    api_key: "AIza..."
```

3. **서버 실행:**
```bash
python main.py
```

4. **웹 브라우저에서 접속:**
```
http://localhost:9876
```

## 설정 상세

`config.yaml` 파일에서 각 모델별로 다음을 설정할 수 있습니다:

- `enabled`: 활성화 여부 (true/false)
- `name`: 표시 이름
- `api_key`: API 키
- `model`: 모델 ID
- `base_url`: API 엔드포인트
- `test_message`: 테스트 메시지

## 프로젝트 구조

```
llm-status-checker/
├── main.py              # FastAPI 백엔드
├── database.py          # SQLite 히스토리 저장 로직
├── config.yaml          # 설정 파일 (사용자 생성)
├── config.yaml.example  # 설정 예시
├── requirements.txt     # Python 의존성
├── Dockerfile           # Docker 이미지 빌드 설정
├── docker-compose.yml   # Docker Compose 설정
├── .dockerignore        # Docker 빌드 제외 파일
├── data/                # SQLite DB 저장 디렉토리 (자동 생성)
├── static/
│   ├── style.css       # 스타일시트
│   └── script.js       # 프론트엔드 로직 (차트 포함)
└── templates/
    └── index.html      # 메인 페이지 (탭 UI)
```

## API 엔드포인트

- `GET /` - 메인 웹 페이지
- `GET /api/status` - 현재 상태 조회 (JSON)
- `GET /api/history?hours=24` - 히스토리 데이터 조회
- `GET /api/stats?hours=24` - 가동률 통계 조회

## 기술 스택

- **백엔드**: FastAPI, Python 3.11+
- **프론트엔드**: Vanilla JS, Bootstrap 5, Chart.js
- **데이터베이스**: SQLite
- **배포**: Docker, Docker Compose

## 라이선스

MIT License

## 기여

Pull Request를 환영합니다!
