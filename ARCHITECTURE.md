# FastAPI + Django + AI Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Your Browser                            │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP Request
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Django (Port 8000)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Views (product_detail, generate_description_api, etc)  │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │ Imports & Uses
│  ┌──────────────────▼──────────────────────────────────────┐   │
│  │  services/django_client.py (AIServiceClient)           │   │
│  │  - generate_description_openai(...)                    │   │
│  │  - generate_description_local(...)                     │   │
│  │  - generate_tags_openai(...)                           │   │
│  │  - generate_tags_local(...)                            │   │
│  │  - is_service_available()                              │   │
│  └──────────────────┬──────────────────────────────────────┘   │
│                     │ HTTP POST
│                     │ (JSON requests)
└─────────────────────┼──────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI (Port 8001)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Endpoints:                                             │   │
│  │  • POST /ai/openai/description                          │   │
│  │  • POST /ai/openai/tags                                 │   │
│  │  • POST /ai/local/description                           │   │
│  │  • POST /ai/local/tags                                  │   │
│  │  • GET /health                                          │   │
│  │  • GET /docs (Interactive API docs)                     │   │
│  └─────────────┬────────────────────────┬─────────────────┘   │
│               │                         │                      │
│               │ Routes to               │ Routes to            │
│               ▼                         ▼                      │
│  ┌────────────────────────┐  ┌──────────────────────────┐     │
│  │ openai_service.py      │  │ ml_service.py            │     │
│  │ - OpenAI Client        │  │ - Transformers Pipeline  │     │
│  │ - API calls to GPT     │  │ - DistilGPT-2 Model     │     │
│  └────────┬───────────────┘  └──────────────┬───────────┘     │
│           │                                  │                 │
│           ▼                                  ▼                 │
└───────────┼──────────────────────────────────┼────────────────┘
            │                                  │
     HTTP to│                                  │ Runs
   OpenAI   │                                  │ Locally
            │                                  │
    ┌───────▼──────────┐          ┌────────────▼──────────┐
    │ OpenAI GPT-3.5   │          │ DistilGPT-2 Model    │
    │ (Cloud)          │          │ (CPU/GPU)            │
    ├──────────────────┤          ├─────────────────────┤
    │ Needs API key    │          │ No API key needed   │
    │ Slow (200-500ms) │          │ Fast (100-200ms)    │
    │ Better quality   │          │ Good quality        │
    │ Cost: $0.02/1K   │          │ Cost: Free          │
    └──────────────────┘          └─────────────────────┘
```

## Data Flow Examples

### Example 1: Generate Product Description (Local Model)

```
1. Django View:
   from services import get_ai_client
   with get_ai_client() as client:
       desc = client.generate_description_local(...)
                    ▼
2. Django Client makes HTTP POST request:
   POST http://127.0.0.1:8001/ai/local/description
   {
       "product_name": "Blue Jeans",
       "category": "Bottoms",
       "price": 59.99
   }
                    ▼
3. FastAPI Route Handler:
   @app.post("/ai/local/description")
   async def generate_description_local(request):
       return await ml_service.generate_product_description_local(...)
                    ▼
4. ml_service.py:
   - Loads DistilGPT-2 model (if not cached)
   - Generates text based on prompt
   - Returns description
                    ▼
5. Response back to Django:
   {
       "description": "High-quality blue jeans...",
       "model_used": "Local DistilGPT-2"
   }
                    ▼
6. Django View receives response and returns to user
```

### Example 2: Generate Tags (OpenAI)

```
1. JavaScript frontend calls Django API:
   fetch('/api/generate-tags/', {
       method: 'POST',
       body: JSON.stringify({
           product_name: "Summer T-Shirt",
           use_openai: true
       })
   })
                    ▼
2. Django View (generate_tags_api):
   - Receives request
   - Calls get_ai_client().generate_tags_openai(...)
                    ▼
3. FastAPI /ai/openai/tags endpoint:
   - HTTP POST request
   - Calls openai_service.generate_product_tags_openai()
                    ▼
4. OpenAI Service:
   - Creates prompt
   - API call to OpenAI with OPENAI_API_KEY
   - Receives generated tags
   - Parses and returns
                    ▼
5. FastAPI response to Django:
   {
       "tags": ["summer", "casual", "t-shirt", "men"],
       "model_used": "OpenAI GPT-3.5"
   }
                    ▼
6. Django returns JSON to frontend:
   {
       "tags": ["summer", "casual", "t-shirt", "men"],
       "model": "OpenAI"
   }
```

## File Dependencies

```
Django Application
    ├── clothstore/views.py
    │   └── imports: from services import get_ai_client
    │
    ├── clothstore/urls.py
    │   └── imports: from ai_urls import urlpatterns
    │
    └── services/
        ├── __init__.py (exports get_ai_client)
        ├── django_client.py
        │   └── imports: httpx
        └── ml_service.py
            └── imports: transformers


FastAPI Application (fastapi_app.py)
    ├── imports: from services.openai_service import ...
    ├── imports: from services.ml_service import ...
    │
    ├── services/
    │   ├── openai_service.py
    │   │   └── imports: openai
    │   └── ml_service.py
    │       └── imports: transformers
    │
    └── External APIs:
        ├── OpenAI API (if using OpenAI models)
        └── HuggingFace Model Hub (if downloading DistilGPT-2)
```

## Deployment Architecture

### Development (Single Machine)

```
Same Machine, Running Two Processes:

Process 1: Django dev server
python manage.py runserver  # :8000

Process 2: FastAPI dev server
python fastapi_app.py       # :8001
```

### Production (Recommended)

```
Load Balancer (nginx)
    │
    ├── Django (Gunicorn)
    │   - Port 8000
    │   - Workers: 4
    │   - Handles web requests
    │   - Database queries
    │
    └── FastAPI (Uvicorn)
        - Port 8001
        - Workers: 4
        - AI inferences
        - Can scale independently
```

### Production (Docker)

```
Docker Compose:

Service: Django
    - Build: Dockerfile
    - Port: 8000
    - Env: OPENAI_API_KEY

Service: FastAPI
    - Build: Dockerfile
    - Port: 8001
    - Env: OPENAI_API_KEY

Network: Internal Docker network
```

## Response Time Comparison

```
Operation              | Local Model    | OpenAI API
─────────────────────────────────────────────────────
Description Gen        | 100-200ms      | 200-500ms
Tags Generation        | 80-150ms       | 300-600ms
Concurrent Requests    | Limited by CPU | API Rate Limits
─────────────────────────────────────────────────────
Typical Workflow:

First Request (no cache):
  Local Model: 500ms (model download first time)
  OpenAI: 300ms (API network latency)

Follow-up Requests:
  Local Model: 100-150ms
  OpenAI: 200-400ms
```

## Error Handling Flow

```
Django View
    │
    └─► get_ai_client()
        │
        ├─► FastAPI Endpoint Not Available
        │   └─► Exception ─► Logger ─► Return None
        │
        ├─► Network Error
        │   └─► httpx.ConnectError ─► Logger ─► Return None
        │
        ├─► API Error (OpenAI)
        │   └─► openai.APIError ─► Logger ─► Return None
        │
        └─► Model Loading Error (Local)
            └─► RuntimeError ─► Logger ─► Return None

Result: Graceful degradation, no crashes
```

## Security Model

```
Architecture Security:

1. API Keys Security:
   - Store in .env file (not in git)
   - Load from environment variables
   - Never expose in logs

2. Network Communication:
   - Both services on localhost (127.0.0.1)
   - No external exposure in development
   - Use HTTPS in production

3. Input Validation:
   - Pydantic models validate all inputs
   - Type hints ensure safety
   - Max length constraints on strings

4. Rate Limiting:
   - Can add rate limiter to FastAPI
   - OpenAI API has built-in limits
   - Local model has CPU limits
```

## Scaling Considerations

```
Vertical Scaling:
├── Django: Add more Gunicorn workers
├── FastAPI: Add more Uvicorn workers
└── Hardware: GPU for faster inference

Horizontal Scaling:
├── Multiple Django instances (load balanced)
├── Multiple FastAPI instances (load balanced)
└── Shared cache (Redis) for model caching

Optimization:
├── Model Caching in memory
├── Response Caching (Redis)
├── Batch Processing
└── GPU Acceleration for ML model
```

This is a flexible, scalable architecture that can grow with your needs!
