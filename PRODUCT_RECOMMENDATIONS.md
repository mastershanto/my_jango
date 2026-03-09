# Product Recommendation System

Complete product recommendation system using both OpenAI and local ML models integrated with Django and FastAPI.

## Features

### 1. **OpenAI-Powered Recommendations**
- ✅ Personalized product recommendations based on user preferences
- ✅ Find similar products to a given product
- ✅ Get detailed reasoning for recommendations
- ✅ Natural language understanding
- ✅ Better quality recommendations (requires API key)

### 2. **Local ML-Powered Recommendations**
- ✅ Content-based filtering using DistilBERT embeddings
- ✅ Fast recommendations (no API latency)
- ✅ Free - no API key needed
- ✅ Privacy-focused (all processing local)
- ✅ Good quality recommendations

### 3. **Recommendation Types**
- **User Preference-Based**: "I want casual summer outfit"
- **Similar Products**: "Show me products like this jacket"
- **Category Recommendations**: "Top products in Tops category"
- **Trending Products**: Popular and featured items

## API Endpoints

### FastAPI Endpoints (Port 8001)

#### OpenAI Recommendations

**POST /ai/openai/recommendations**
```bash
curl -X POST "http://127.0.0.1:8001/ai/openai/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_preference": "I want casual summer clothes without spending too much",
    "category": "Tops",
    "count": 5
  }'
```

Response:
```json
{
  "recommendations": [
    {
      "product_name": "Lightweight Cotton T-Shirt",
      "category": "Tops",
      "reasoning": "Perfect lightweight option for summer"
    },
    {
      "product_name": "Summer Tank Top",
      "category": "Tops",
      "reasoning": "Great for hot weather"
    }
  ],
  "model_used": "OpenAI GPT-3.5"
}
```

**POST /ai/openai/similar-products**
```bash
curl -X POST "http://127.0.0.1:8001/ai/openai/similar-products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Blue Denim Jacket",
    "count": 3
  }'
```

Response:
```json
["Black Denim Jacket", "Casual Linen Jacket", "Denim Shirt"]
```

#### Local ML Recommendations

**POST /ai/local/recommendations**
```bash
curl -X POST "http://127.0.0.1:8001/ai/local/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_preference": "casual summer clothes",
    "category": "",
    "count": 5
  }'
```

**POST /ai/local/similar-products**
```bash
curl -X POST "http://127.0.0.1:8001/ai/local/similar-products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Blue Denim Jacket",
    "count": 3
  }'
```

**POST /ai/local/category-recommendations**
```bash
curl -X POST "http://127.0.0.1:8001/ai/local/category-recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Tops",
    "count": 5
  }'
```

## Django Integration

### Using in Views

```python
from services import get_ai_client

# Get recommendations
with get_ai_client() as client:
    # OpenAI recommendations
    recommendations = client.get_recommendations_openai(
        user_preference="casual summer outfit",
        category="Tops",
        count=5
    )
    
    # Local ML recommendations
    recommendations = client.get_recommendations_local(
        user_preference="casual summer outfit",
        count=5
    )
    
    # Similar products
    similar = client.get_similar_products_local(
        product_name="Blue Denim Jacket",
        count=3
    )
    
    # Category recommendations
    category = client.get_category_recommendations(
        category="Tops",
        count=5
    )
```

### Available Methods in AIServiceClient

```python
# Recommendations
client.get_recommendations_openai(user_preference, category="", count=5)
client.get_recommendations_local(user_preference, category="", count=5)

# Similar Products
client.get_similar_products_openai(product_name, count=3)
client.get_similar_products_local(product_name, count=3)

# Category-based
client.get_category_recommendations(category, count=5)
```

## API Endpoints for Django Views

### POST /ai/api/recommendations/

Get personalized recommendations

**Request:**
```json
{
  "user_preference": "I want casual summer clothes",
  "category": "Tops",
  "count": 5,
  "use_openai": true
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "product_name": "Lightweight T-Shirt",
      "category": "Tops",
      "reasoning": "Perfect for summer"
    }
  ],
  "model": "OpenAI GPT-3.5",
  "count": 1
}
```

### POST /ai/api/similar-products/

Find similar products

**Request:**
```json
{
  "product_name": "Blue Denim Jacket",
  "count": 3,
  "use_openai": false
}
```

### GET /ai/api/category-recommendations/

Get category-based recommendations

**Request:**
```
GET /ai/api/category-recommendations/?category=Tops&count=5
```

## JavaScript Frontend Examples

### Get Recommendations

```javascript
async function getRecommendations() {
    const response = await fetch('/ai/api/recommendations/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_preference: 'casual summer outfit',
            category: 'Tops',
            count: 5,
            use_openai: true  // or false for local model
        })
    });
    
    const data = await response.json();
    console.log('Recommendations:', data.recommendations);
    
    // Display recommendations
    displayRecommendations(data.recommendations);
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations');
    
    recommendations.forEach(rec => {
        const div = document.createElement('div');
        div.innerHTML = `
            <h3>${rec.product_name}</h3>
            <p>Category: ${rec.category}</p>
            <p>${rec.reasoning}</p>
        `;
        container.appendChild(div);
    });
}
```

### Get Similar Products

```javascript
async function getSimilarProducts(productName) {
    const response = await fetch('/ai/api/similar-products/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            product_name: productName,
            count: 3,
            use_openai: false
        })
    });
    
    const data = await response.json();
    console.log('Similar products:', data.similar_products);
}
```

## Comparison: OpenAI vs Local ML

| Feature | OpenAI | Local ML |
|---------|--------|----------|
| **Quality** | Excellent | Good |
| **Speed** | Medium (200-500ms) | Fast (50-150ms) |
| **Cost** | ~$0.02 per 5 requests | Free |
| **Privacy** | Data sent to OpenAI | All local |
| **API Key** | Required | Not needed |
| **Best For** | High-quality recommendations | Fast, privacy-focused |
| **Scaling** | API limits | CPU-bound |
| **Model** | GPT-3.5 Turbo | DistilBERT + ML |

## Integration Steps

### 1. Check FastAPI is Running

```bash
# Terminal 2
python fastapi_app.py
```

### 2. Add URLs to Django (config/urls.py)

```python
from django.urls import path, include

urlpatterns = [
    # ... other urls
    path("ai/", include("ai_urls")),
]
```

### 3. In Your Templates

```html
<!-- Add buttons/forms to trigger recommendations -->
<button onclick="getRecommendations()">Get Recommendations</button>
<div id="recommendations"></div>
```

### 4. Use in Views or Templates

```python
# In views.py
from services import get_ai_client

def product_list_with_recommendations(request):
    user_preference = request.GET.get('preference', '')
    
    with get_ai_client() as client:
        recommendations = client.get_recommendations_local(
            user_preference, 
            count=6
        )
    
    context = {
        'recommendations': recommendations,
    }
    return render(request, 'products.html', context)
```

## Advanced Usage

### Hybrid Approach: Try OpenAI, Fallback to Local

```python
with get_ai_client() as client:
    # Try OpenAI first for better quality
    recommendations = client.get_recommendations_openai(
        "summer outfit",
        count=5
    )
    
    # Fallback to local model if OpenAI fails
    if not recommendations:
        recommendations = client.get_recommendations_local(
            "summer outfit",
            count=5
        )
```

### Batch Processing

See `MANAGEMENT_COMMAND_EXAMPLE.py` for Django management command to batch generate recommendations.

### Caching Recommendations

```python
from django.core.cache import cache

def get_recommendations_cached(user_id, preference, use_cache=True):
    cache_key = f"recommendations_{user_id}_{preference}"
    
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    with get_ai_client() as client:
        recommendations = client.get_recommendations_local(preference, count=5)
    
    # Cache for 1 hour
    cache.set(cache_key, recommendations, 3600)
    
    return recommendations
```

## Model Details

### OpenAI Model
- **Model**: GPT-3.5 Turbo
- **Tokens**: Limited by API
- **Context**: Understands natural language perfectly
- **Quality**: Highest

### Local ML Models
- **Text Embedding**: DistilBERT (sentence transformations)
- **Similarity Metric**: Cosine similarity
- **Category Bonus**: +0.15 boost for same category
- **Speed**: <200ms per request

## Testing

Run the test suite:

```bash
python test_fastapi_integration.py
```

## Troubleshooting

### Slow Recommendations

- **OpenAI is slow**: Network latency, consider caching
- **Local model is slow**: Increase CPU, or use smaller model

### Empty Results

- Check if products exist in database
- Verify user_preference text is descriptive
- Try different category filters

### API Errors

- Ensure FastAPI is running on port 8001
- Check OPENAI_API_KEY if using OpenAI
- Review error logs in terminal

## Production Considerations

1. **Caching**: Add Redis for frequently accessed recommendations
2. **Rate Limiting**: Implement API rate limits
3. **Database Integration**: Fetch real products from Django DB instead of sample data
4. **Async Processing**: Use Celery for background recommendation generation
5. **Monitoring**: Track recommendation quality and user satisfaction
6. **A/B Testing**: Test OpenAI vs Local ML recommendation quality

## Next Steps

1. ✅ Set up endpoints
2. ✅ Test with example requests
3. ✅ Integrate into product pages
4. ✅ Add recommendation widgets to templates
5. ✅ Implement caching
6. ✅ Monitor performance
7. ✅ Gather user feedback

---

For more examples, see [EXAMPLES_DJANGO_INTEGRATION.py](EXAMPLES_DJANGO_INTEGRATION.py)
