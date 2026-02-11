import os
import yaml
import asyncio
import certifi
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
from typing import Dict, Any
from contextlib import asynccontextmanager
import database

oldValue = os.environ['SSL_CERT_FILE']

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 DB 초기화
    database.init_db()
    yield
    # 종료 시 정리 작업 (필요시)

app = FastAPI(title="LLM Status Checker", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ModelStatus(BaseModel):
    name: str
    status: str  # "success", "error", "checking", "disabled"
    response: str | None = None
    error: str | None = None
    response_time: float | None = None

def load_config():
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"설정 파일 로드 실패: {e}")

def test_openai_model(config: Dict[str, Any]) -> ModelStatus:
    model_config = config["models"]["openai"]
    
    if not model_config.get("enabled", True):
        return ModelStatus(name=model_config["name"], status="disabled")
    
    os.environ['SSL_CERT_FILE'] = oldValue
    status = ModelStatus(name=model_config["name"], status="checking")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        client = OpenAI(
            base_url=model_config["base_url"],
            api_key=model_config["api_key"]
        )
        
        response = client.chat.completions.create(
            model=model_config["model"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": model_config["test_message"]}
            ]
        )
        
        end_time = asyncio.get_event_loop().time()
        status.response_time = round((end_time - start_time) * 1000, 2)
        
        status.status = "success"
        status.response = response.choices[0].message.content
        
    except Exception as e:
        import traceback
        status.status = "error"
        status.error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
    
    return status

def test_huggingface_model(config: Dict[str, Any]) -> ModelStatus:
    model_config = config["models"]["huggingface"]
    
    if not model_config.get("enabled", True):
        return ModelStatus(name=model_config["name"], status="disabled")
    
    os.environ['SSL_CERT_FILE'] = certifi.where()
    status = ModelStatus(name=model_config["name"], status="checking")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        client = OpenAI(
            base_url=model_config["base_url"],
            api_key=model_config["api_key"]
        )
        
        response = client.chat.completions.create(
            model=model_config["model"],
            messages=[
                {"role": "user", "content": model_config["test_message"]}
            ]
        )
        
        end_time = asyncio.get_event_loop().time()
        status.response_time = round((end_time - start_time) * 1000, 2)
        
        status.status = "success"
        status.response = response.choices[0].message.content
        
    except Exception as e:
        status.status = "error"
        status.error = str(e)
    
    return status

def test_claude_model(config: Dict[str, Any]) -> ModelStatus:
    model_config = config["models"]["claude"]
    
    if not model_config.get("enabled", True):
        return ModelStatus(name=model_config["name"], status="disabled")
    
    os.environ['SSL_CERT_FILE'] = oldValue
    status = ModelStatus(name=model_config["name"], status="checking")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        client = Anthropic(
            api_key=model_config["api_key"]
        )
        
        response = client.messages.create(
            model=model_config["model"],
            max_tokens=1024,
            messages=[
                {"role": "user", "content": model_config["test_message"]}
            ]
        )
        
        end_time = asyncio.get_event_loop().time()
        status.response_time = round((end_time - start_time) * 1000, 2)
        
        status.status = "success"
        status.response = response.content[0].text
        
    except Exception as e:
        status.status = "error"
        status.error = str(e)
    
    return status

def test_gemini_model(config: Dict[str, Any]) -> ModelStatus:
    model_config = config["models"]["gemini"]
    
    if not model_config.get("enabled", True):
        return ModelStatus(name=model_config["name"], status="disabled")
    
    os.environ['SSL_CERT_FILE'] = certifi.where()
    status = ModelStatus(name=model_config["name"], status="checking")
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        genai.configure(api_key=model_config["api_key"])
        model = genai.GenerativeModel(model_config["model"])
        
        response = model.generate_content(model_config["test_message"])
        
        end_time = asyncio.get_event_loop().time()
        status.response_time = round((end_time - start_time) * 1000, 2)
        
        status.status = "success"
        status.response = response.text
        
    except Exception as e:
        status.status = "error"
        status.error = str(e)
    
    return status

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def _test_model_safe(model_key: str, test_fn, config: Dict[str, Any]) -> ModelStatus:
    """config에 모델이 없거나 비활성화된 경우 안전하게 처리"""
    models = config.get("models", {})
    if model_key not in models:
        return ModelStatus(name=model_key, status="disabled")
    return test_fn(config)

@app.get("/api/status")
async def get_status():
    try:
        config = load_config()
        
        # 각 모델별 테스트 함수 매핑
        model_tests = {
            "openai": test_openai_model,
            "huggingface": test_huggingface_model,
            "claude": test_claude_model,
            "gemini": test_gemini_model,
        }
        
        results = {}
        for key, test_fn in model_tests.items():
            status = _test_model_safe(key, test_fn, config)
            results[key] = status
            
            # DB에 상태 저장 (disabled 제외)
            if status.status != "disabled":
                database.save_status(
                    key,
                    status.status,
                    status.response_time,
                    status.error
                )
        
        return {
            **{k: v.dict() for k, v in results.items()},
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {e}")

@app.get("/api/history")
async def get_history(hours: int = 24):
    """히스토리 데이터 조회"""
    try:
        history = database.get_history(hours)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 실패: {e}")

@app.get("/api/stats")
async def get_stats(hours: int = 24):
    """가동률 통계 조회"""
    try:
        stats = database.get_uptime_stats(hours)
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9876)
