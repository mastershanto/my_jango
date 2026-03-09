# FastAPI + Django + AI Integration Guide

This guide shows how to integrate FastAPI with Django to use OpenAI and local ML models for generating product descriptions and tags.

## Architecture Overview

```
┌──────────────────┐                    ┌──────────────────┐
│   Django App     │◄──────(HTTP)──────►│   FastAPI App    │
│   (Port 8000)    │                    │   (Port 8001)    │
│                  │                    │                  │
│  - Serves views  │                    │  - OpenAI API    │
│  - DB queries    │                    │  - Local ML      │
│  - Business logic│                    │    Models        │
└──────────────────┘                    └──────────────────┘
        ▲                                        ▲
        │                                        │
        └────────────────────────────────────────┘
             Separate processes, same machine
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.text
```

This installs:
- **FastAPI**: Modern async web framework
- **Uvicorn**: ASGI server for FastAPI
- **OpenAI**: OpenAI API client (for GPT models)
- **Transformers**: For local ML models (DistilGPT-2)
- **Torch**: Required by transformers
- **Httpx**: Async HTTP client for Django→FastAPI communication
- **Pydantic**: Data validation

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk_your_actual_api_key_here
DEBUG=True
FASTAPI_HOST=127.0.0.1
FASTAPI_PORT=8001
```

**Note:** Get a free OpenAI API key from https://platform.openai.com/api-keys (you get $5 free credits)

### 3. Create `.env` File

```bash
nano .env
# Add your OpenAI API key
```

## Running Both Services

You need to run **TWO separate processes**: Django and FastAPI.

### Terminal 1: Start Django

```bash
# Activate virtual environment
source .venv/bin/activate

# Run Django
python manage.py runserver
```

Django will run on `http://127.0.0.1:8000`

### Terminal 2: Start FastAPI

```bash
# Activate virtual environment (in another terminal)
source .venv/bin/activate

# Run FastAPI
python fastapi_app.py
# OR
uvicorn fastapi_app:app --reload --port 8001
```

FastAPI will run on `http://127.0.0.1:8001`

**Note:** The first time you run FastAPI, it will download the DistilGPT-2 model (~350MB). This is a one-time download.

## API Endpoints

### 1. OpenAI Endpoints (Requires API Key)

#### Generate Product Description (OpenAI)

```bash
curl -X POST "http://127.0.0.1:8001/ai/openai/description" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Blue Denim Jacket",
    "category": "Outerwear",
    "price": 89.99
  }'
```

**Response:**
```json
{
  "description": "This premium blue denim jacket offers timeless style and durability. Perfect for layering or wearing as a standalone piece, it combines classic comfort with modern sophistication.",
  "model_used": "OpenAI GPT-3.5"
}
```

#### Generate Tags (OpenAI)

```bash
curl -X POST "http://127.0.0.1:8001/ai/openai/tags" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Blue Denim Jacket",
    "description": "Premium blue denim jacket"
  }'
```

### 2. Local ML Model Endpoints (No API Key Needed)

#### Generate Product Description (Local)

```bash
curl -X POST "http://127.0.0.1:8001/ai/local/description" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Summer T-Shirt",
    "category": "Tops",
    "price": 29.99
  }'
```

#### Generate Tags (Local)

```bash
curl -X POST "http://127.0.0.1:8001/ai/local/tags" \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Summer T-Shirt"}'
```

### 3. Health Check

```bash
curl http://127.0.0.1:8001/health
```

## Using in Django Views

### Example 1: Simple Integration

```python
from services import get_ai_client

# In your view:
with get_ai_client() as client:
    # Try OpenAI first
    description = client.generate_description_openai(
        "Blue Jeans",
        "Bottoms", 
        59.99
    )
    
    # Fallback to local model if OpenAI fails
    if not description:
        description = client.generate_description_local(
            "Blue Jeans",
            "Bottoms",
            59.99
        )
```

### Example 2: API Endpoints in urls.py

```python
from EXAMPLES_DJANGO_INTEGRATION import (
    generate_description_api,
    generate_tags_api,
    ai_service_status,
)

urlpatterns = [
    path('api/generate-description/', generate_description_api, name='generate_description'),
    path('api/generate-tags/', generate_tags_api, name='generate_tags'),
    path('api/ai-status/', ai_service_status, name='ai_status'),
]
```

### Example 3: Frontend JavaScript

```javascript
// Generate description
async function generateDescription() {
    const response = await fetch('/api/generate-description/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            product_name: 'Blue Jeans',
            category: 'Bottoms',
            price: 59.99,
            use_openai: true  // or false for local model
        })
    });
    const data = await response.json();
    console.log('Description:', data.description);
}

// Check service status
async function checkAIService() {
    const response = await fetch('/api/ai-status/');
    const data = await response.json();
    console.log('AI Service:', data.status);
}
```

## Features Comparison

| Feature | OpenAI | Local ML |
|---------|--------|----------|
| **Quality** | Excellent | Good |
| **Speed** | Slow (API call) | Fast (local) |
| **Cost** | $0.02 per 1K tokens | Free |
| **API Key** | Required | Not needed |
| **Privacy** | Data sent to OpenAI | All local |
| **Best for** | High-quality, complex content | Quick, privacy-focused |

## File Structure

```
.
├── fastapi_app.py                    # Main FastAPI application
├── services/
│   ├── __init__.py
│   ├── openai_service.py            # OpenAI API calls
│   ├── ml_service.py                # Local ML model calls
│   └── django_client.py             # Django client to call FastAPI
├── clothstore/
│   ├── views.py                     # Django views
│   └── urls.py
├── config/
│   ├── settings.py                  # Django settings
│   └── urls.py
├── EXAMPLES_DJANGO_INTEGRATION.py   # Code examples
├── requirements.text                 # Python dependencies
└── .env.example                     # Environment template
```

## Troubleshooting

### FastAPI Service Not Responding

```bash
# Check if port 8001 is in use
lsof -i :8001

# Kill the process
kill -9 <PID>
```

### OpenAI API Key Invalid

- Get a key from: https://platform.openai.com/api-keys
- Make sure it's in `.env` file as `OPENAI_API_KEY=sk_...`
- Check it's not expired or revoked

### Model Download Fails

First FastAPI run downloads DistilGPT-2 (~350MB):
```bash
# Manually download if needed:
python -c "from transformers import pipeline; pipeline('text-generation', model='distilgpt2')"
```

### Django Can't Connect to FastAPI

Make sure both services are running:
```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: FastAPI
python fastapi_app.py
```

## API Documentation

When FastAPI is running, visit:
- **Interactive Docs**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

## Production Deployment

### Django + FastAPI on Same Server

```bash
# Use Gunicorn for Django
gunicorn config.wsgi --workers 4 --port 8000 &

# Use Uvicorn for FastAPI
uvicorn fastapi_app:app --workers 4 --port 8001 &
```

### Docker (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  django:
    build: .
    command: gunicorn config.wsgi --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  
  fastapi:
    build: .
    command: uvicorn fastapi_app:app --host 0.0.0.0 --port 8001
    ports:
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

## Security Notes

- ⚠️ **Never commit `.env` file** with real API keys
- Use environment variables in production
- Add `services.django_client.py` to handle timeouts
- Implement rate limiting for API endpoints
- Add authentication to your Django views

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.text`
2. ✅ Set up `.env` with your OpenAI key (if using OpenAI)
3. ✅ Run Django: `python manage.py runserver`
4. ✅ Run FastAPI: `python fastapi_app.py`
5. ✅ Test endpoints in your code or at http://127.0.0.1:8001/docs
6. ✅ Integrate into your Django views using `services.get_ai_client()`

## Useful Resources

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Transformers Library](https://huggingface.co/docs/transformers)
- [Django Integration](https://docs.djangoproject.com)
