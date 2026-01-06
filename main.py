import os
import yaml
import asyncio
import certifi
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
from typing import Dict, Any

oldValue = os.environ['SSL_CERT_FILE']

app = FastAPI(title="LLM Status Checker")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ModelStatus(BaseModel):
    name: str
    status: str  # "success", "error", "checking"
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

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    try:
        config = load_config()
        
        openai_status = test_openai_model(config)
        hf_status = test_huggingface_model(config)
        
        return {
            "openai": openai_status.dict(),
            "huggingface": hf_status.dict(),
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9876)
