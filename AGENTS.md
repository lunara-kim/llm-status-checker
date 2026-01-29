# AGENTS.md

This file provides guidance for agentic coding assistants working in the llm-status-checker repository.

## Project Overview

LLM Status Checker is a FastAPI web application for monitoring real-time connectivity to external LLM APIs (OpenAI, HuggingFace, Anthropic, Google Gemini). It provides a dashboard showing connection status, response times, and API responses with auto-refresh every 30 seconds.

**Tech Stack:**
- Backend: FastAPI 0.104.1 with Uvicorn
- Frontend: HTML, CSS (Bootstrap 5.1.3), vanilla JavaScript
- Language: Python 3.10
- Data Validation: Pydantic 2.5.0
- Configuration: YAML (config.yaml)

## Commands

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 9876 --reload
```

### Testing

```bash
# Run a specific test file
python test_anthropic.py

# Run all tests (if pytest is added)
pytest tests/

# Run a single test file
pytest tests/test_example.py

# Run with coverage
pytest tests/ --cov=.
```

### Linting and Formatting (Recommended)

```bash
# Install development tools
pip install black ruff mypy pytest

# Format code
black .

# Check formatting
black --check .

# Lint code
ruff check .

# Type checking
mypy main.py --ignore-missing-imports

# Run all checks together
black --check . && ruff check . && mypy main.py --ignore-missing-imports
```

## Code Style Guidelines

### Python Style

**Type Hints:**
- Use modern union syntax: `str | None` instead of `Optional[str]`
- Always annotate function parameters and return types
- Use Pydantic BaseModel for data models with explicit field types

```python
from typing import Dict, Any
from pydantic import BaseModel

class ModelStatus(BaseModel):
    name: str
    status: str  # "success", "error", "checking", "disabled"
    response: str | None = None
    error: str | None = None
    response_time: float | None = None

def test_model(config: Dict[str, Any]) -> ModelStatus:
    # Implementation
    pass
```

**Imports:**
- Standard library imports first, then third-party, then local
- Group imports with blank lines between groups
- Use `from module import Class` for commonly used classes
- Use `import module` for less commonly used modules

```python
import os
import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
```

**Error Handling:**
- Use try-except blocks around external API calls
- Provide detailed error messages with traceback for debugging
- Handle both network errors and API-specific errors
- Raise HTTPException for API endpoint errors

```python
try:
    start_time = asyncio.get_event_loop().time()
    response = client.chat.completions.create(...)
    status.response_time = round((end_time - start_time) * 1000, 2)
    status.status = "success"
except Exception as e:
    import traceback
    status.status = "error"
    status.error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
```

**Naming Conventions:**
- Classes: PascalCase (ModelStatus, FastAPI)
- Functions and variables: snake_case (test_openai_model, load_config)
- Constants: UPPER_SNAKE_CASE (rarely used, usually in config)
- Private methods: prefix with underscore (_private_method)

**FastAPI Conventions:**
- Use `@app.get()` or `@app.post()` decorators for route definitions
- Return Pydantic models directly, they auto-serialize to JSON
- Use `response_class=HTMLResponse` for HTML endpoints
- Use templates from Jinja2 for HTML responses

```python
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    config = load_config()
    return {"openai": openai_status.dict(), "timestamp": ...}
```

**Configuration:**
- Load configuration from config.yaml using YAML safe_load
- Use UTF-8 encoding for file operations
- Keep API keys and sensitive data in config.yaml (not in code)
- Support enabled/disabled flags for optional features

### JavaScript Style

**Naming and Structure:**
- Use camelCase for functions and variables (updateModelStatus, checkStatus)
- Use async/await for asynchronous operations
- Use const for variables that don't change, let for those that do
- Use meaningful variable names (statusDot, responseTime)

**DOM Manipulation:**
- Use template literals for dynamic strings with IDs
- Use classList methods for class manipulation (add, remove)
- Set textContent for text updates (not innerHTML to prevent XSS)
- Use querySelector for selecting child elements

```javascript
async function updateModelStatus(modelName, data) {
    const indicator = document.getElementById(`${modelName}-indicator`);
    const statusDot = indicator.querySelector('.status-dot');
    
    if (data.status === 'success') {
        statusDot.classList.add('success');
        statusText.textContent = '정상';
    }
}
```

**Error Handling:**
- Use try-catch around async operations
- Provide user-friendly error messages
- Use console.error for debugging
- Update UI to reflect error states

### CSS Style

**Naming:**
- Use kebab-case for class names (model-card, status-indicator)
- Use semantic class names that describe purpose, not appearance
- Prefix state modifiers with status name (status-dot.success)

**Structure:**
- Group related styles together
- Use CSS variables for repeated values (consider adding them)
- Keep specificity low (avoid over-nesting)
- Use flexbox for layouts

```css
.model-card {
    transition: all 0.3s ease;
    border: none;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.status-dot.success {
    background-color: #28a745;
    animation: none;
}
```

## Project Structure

```
llm-status-checker/
├── main.py              # FastAPI application with API endpoints
├── test_anthropic.py    # Standalone test script for Anthropic API
├── config.yaml          # Configuration file (API keys, model settings)
├── requirements.txt     # Python dependencies
├── static/
│   ├── style.css       # Application styles
│   └── script.js       # Frontend JavaScript logic
├── templates/
│   └── index.html      # Main HTML template
├── backend/            # Backend modules (empty, consider using)
├── config/             # Configurations (empty, consider using)
└── frontend/           # Frontend source (empty, consider using)
```

## Testing Guidelines

- Test files should be named `test_*.py` or `*_test.py`
- Test functions should be named `test_*`
- Use pytest for structured testing (add to requirements.txt)
- Test both success and error cases for API calls
- Mock external API calls in unit tests to avoid actual API usage

## Important Notes

- Korean language is used for UI text and comments (maintain this)
- Application runs on port 9876 by default
- Auto-refresh is set to 30 seconds in script.js
- SSL certificate handling differs by API (uses certifi for some, original for others)
- Response time is measured in milliseconds and rounded to 2 decimal places
- Four supported LLM providers: OpenAI, HuggingFace, Anthropic, Gemini

## Development Workflow

1. Make changes to code
2. Test manually with `python main.py`
3. Run tests: `pytest` (if available) or `python test_*.py`
4. Run linting: `black --check . && ruff check .` (if tools installed)
5. Update config.yaml if adding new models or endpoints
6. Test the web interface at http://localhost:9876
