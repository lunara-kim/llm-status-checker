# LLM 상태 확인 도구

사내 환경에서 외부 LLM 접속 상태를 실시간으로 확인하는 웹 애플리케이션입니다.

## 기능

- OpenAI GPT-4o 접속 상태 확인
- HuggingFace GLM-4.7 접속 상태 확인
- 실시간 상태 표시 (초록불/빨간불)
- 응답 시간 측정
- 자동 새로고침 (30초 간격)

## 설치 및 실행

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 설정 파일 수정:
```bash
# config.yaml 파일에서 API 키 설정
models:
  openai:
    api_key: "your-openai-api-key-here"
  huggingface:
    api_key: "your-huggingface-api-key-here"
```

3. 서버 실행:
```bash
python main.py
```

4. 웹 브라우저에서 접속:
```
http://localhost:9876
```

## 프로젝트 구조

```
llm-status-checker/
├── main.py              # FastAPI 백엔드
├── config.yaml          # 설정 파일
├── requirements.txt     # 의존성
├── static/
│   ├── style.css       # 스타일시트
│   └── script.js       # 프론트엔드 로직
└── templates/
    └── index.html      # 메인 페이지
```