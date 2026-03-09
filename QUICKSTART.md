# FastAPI + Django Integration - Quick Start

## 📁 What Was Created

```
your_project/
├── fastapi_app.py                    # FastAPI server (runs on port 8001)
├── services/
│   ├── __init__.py
│   ├── openai_service.py            # OpenAI integration
│   ├── ml_service.py                # Local ML model (DistilGPT-2)
│   └── django_client.py             # Client for calling FastAPI from Django
├── EXAMPLES_DJANGO_INTEGRATION.py   # Example Django views & API endpoints
├── MANAGEMENT_COMMAND_EXAMPLE.py    # Batch processing example
├── ai_urls.py                       # Django URL patterns for AI API
├── test_fastapi_integration.py      # Test script
├── setup_fastapi.sh                 # Setup helper script
├── README_FASTAPI_SETUP.md          # Full documentation
├── .env.example                     # Environment template
└── requirements.text                # Updated with new packages
```

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.text
```

### Step 2: Configure OpenAI (Optional)

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
nano .env
```

Get free credits: https://platform.openai.com/api-keys

### Step 3: Run Both Servers

**Terminal 1 - Django**
```bash
python manage.py runserver
```

**Terminal 2 - FastAPI**
```bash
python fastapi_app.py
```

## 🧪 Test It

```bash
# In a third terminal or Python shell
python test_fastapi_integration.py
```

## 💻 Use in Your Django Views

```python
from services import get_ai_client

# In your view:
with get_ai_client() as client:
    # Generate description using local ML (no API key needed)
    desc = client.generate_description_local(
        "Blue Jeans",
        "Bottoms",
        59.99
    )
    
    # Or use OpenAI (requires API key)
    desc = client.generate_description_openai(
        "Blue Jeans",
        "Bottoms",
        59.99
    )
    
    # Generate tags
    tags = client.generate_tags_local("Blue Jeans")
```

## 🌐 Available Endpoints

### Local ML Model (No API Key)
- `POST /ai/local/description` - Generate description
- `POST /ai/local/tags` - Generate tags

### OpenAI (Requires API Key)
- `POST /ai/openai/description` - Generate description
- `POST /ai/openai/tags` - Generate tags

### Utilities
- `GET /health` - Check if service is running
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

## 📊 Examples

### Example 1: In Django Views
See `EXAMPLES_DJANGO_INTEGRATION.py`

### Example 2: Batch Processing
See `MANAGEMENT_COMMAND_EXAMPLE.py`
```bash
python manage.py generate_ai_descriptions --model=local --batch=50
```

### Example 3: Django URLs
See `ai_urls.py`

## 🚀 Features

✅ **Two AI Options:**
- Local ML model (DistilGPT-2) - Fast, free, no API key
- OpenAI GPT-3.5 - Better quality, requires API key

✅ **Easy Integration:**
- Drop-in client for Django
- Non-blocking async operations
- Error handling & fallbacks

✅ **Separate Services:**
- Django on port 8000
- FastAPI on port 8001
- Independent scaling

✅ **Production Ready:**
- Async/await support
- Type hints (Pydantic)
- Error handling
- Health checks

## 🔧 Configuration

Edit `.env`:
```
OPENAI_API_KEY=sk_your_key_here
DEBUG=True
FASTAPI_HOST=127.0.0.1
FASTAPI_PORT=8001
```

## 📖 Full Documentation

See `README_FASTAPI_SETUP.md` for:
- Detailed setup instructions
- All API endpoints
- Production deployment
- Troubleshooting
- Docker configuration

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Copy `.env.example` to `.env` (and set OPENAI_API_KEY if using OpenAI)
3. ✅ Start Django and FastAPI servers
4. ✅ Test with `test_fastapi_integration.py`
5. ✅ Integrate into your views using `get_ai_client()`
6. ✅ View API docs at `http://127.0.0.1:8001/docs`

## 💡 Pro Tips

- **Fallback Pattern:** Try OpenAI first, fallback to local model if API fails
- **Batch Processing:** Use the management command for bulk description generation
- **Caching:** Implement Redis caching to avoid repeated API calls
- **Rate Limiting:** Add rate limits for production use
- **Background Tasks:** Use Celery for async processing

## ❓ Having Issues?

1. Check FastAPI is running: `curl http://127.0.0.1:8001/health`
2. Test API manually: Visit `http://127.0.0.1:8001/docs`
3. Check logs in both terminal windows
4. See Troubleshooting section in README_FASTAPI_SETUP.md

## 📝 License

Same as your Django project
