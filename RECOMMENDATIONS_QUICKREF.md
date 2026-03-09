# Product Recommendation System - Quick Reference

## What Was Added

### New Service Files

1. **`services/openai_recommendation_service.py`**
   - `get_product_recommendations_openai()` - Get recommendations using OpenAI GPT-3.5
   - `get_similar_products_openai()` - Find similar products
   - `get_recommendation_reasoning_openai()` - Get reasoning for recommendations

2. **`services/recommendation_service.py`**
   - `get_product_recommendations_local()` - Get recommendations using local ML (DistilBERT)
   - `get_similar_products_local()` - Find similar products locally
   - `get_category_recommendations_local()` - Filter by category
   - `get_trending_products_local()` - Get trending/featured products

### Updated Files

1. **`fastapi_app.py`**
   - Added 5 new FastAPI endpoints for recommendations
   - Added Pydantic models for recommendation requests/responses
   - Integrated both OpenAI and local ML recommendation services

2. **`services/django_client.py`**
   - Added 5 new methods to `AIServiceClient` class
   - `get_recommendations_openai()` and `get_recommendations_local()`
   - `get_similar_products_openai()` and `get_similar_products_local()`
   - `get_category_recommendations()`

3. **`EXAMPLES_DJANGO_INTEGRATION.py`**
   - Added `get_recommendations_api()` - Django view for recommendations
   - Added `get_similar_products_api()` - Django view for similar products
   - Added `category_recommendations_api()` - Category filtering
   - Added `product_recommendations_page()` - Dedicated recommendations page

4. **`ai_urls.py`**
   - Added URL patterns for all recommendation endpoints
   - Routes for API endpoints and recommendation page

### New Documentation & Examples

1. **`PRODUCT_RECOMMENDATIONS.md`** - Complete guide for recommendation system
2. **`RECOMMENDATIONS_TEMPLATE.html`** - Beautiful frontend template with search UI

## Quick Start: Using Recommendations

### In Python/Django Views

```python
from services import get_ai_client

with get_ai_client() as client:
    # Get recommendations based on user preference
    recommendations = client.get_recommendations_local(
        user_preference="casual summer outfit",
        category="Tops",
        count=5
    )
    
    # Format:
    # [
    #   {
    #     "product_name": "Summer T-Shirt",
    #     "category": "Tops",
    #     "reasoning": "Matches your preference...",
    #     "similarity_score": 0.87
    #   },
    #   ...
    # ]
```

### In JavaScript/Frontend

```javascript
// POST to Django API
const response = await fetch('/ai/api/recommendations/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        user_preference: "casual summer outfit",
        category: "Tops",
        count: 5,
        use_openai: false  // true for OpenAI, false for local
    })
});

const data = await response.json();
// data.recommendations contains the recommendations
```

## API Endpoints

### FastAPI (Port 8001)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ai/openai/recommendations` | POST | OpenAI-based recommendations |
| `/ai/openai/similar-products` | POST | OpenAI similar products |
| `/ai/local/recommendations` | POST | Local ML recommendations |
| `/ai/local/similar-products` | POST | Local ML similar products |
| `/ai/local/category-recommendations` | POST | Category-based recommendations |

### Django (Port 8000)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ai/api/recommendations/` | POST | Get recommendations |
| `/ai/api/similar-products/` | POST | Get similar products |
| `/ai/api/category-recommendations/` | GET/POST | Category recommendations |
| `/ai/recommendations/` | GET | Recommendations page UI |

## Features Comparison

### OpenAI Recommendations
- ✅ Natural language understanding
- ✅ Context-aware suggestions
- ✅ Better reasoning explanations
- ⏱️ Slightly slower (200-500ms)
- 💰 Costs money (~$0.02 per 5 requests)

### Local ML Recommendations
- ✅ Fast (50-150ms)
- ✅ Completely free
- ✅ Privacy-focused (no external API calls)
- ✅ Works offline
- ✅ DistilBERT embeddings for semantic similarity

## Implementation Examples

### Example 1: Simple Product Page with Recommendations

```python
# views.py
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    with get_ai_client() as client:
        # Get similar products
        similar = client.get_similar_products_local(
            product_name=product.name,
            count=3
        )
    
    context = {
        'product': product,
        'similar_products': similar,
    }
    return render(request, 'product_detail.html', context)
```

### Example 2: Personalized Homepage

```python
# views.py
def home_with_recommendations(request):
    query = request.GET.get('preference', 'casual wear')
    
    with get_ai_client() as client:
        featured = client.get_recommendations_local(
            user_preference=query,
            count=6
        )
    
    context = {'featured_products': featured}
    return render(request, 'home.html', context)
```

### Example 3: Search Results with AI Enhancement

```python
# views.py
def search_with_recommendations(request):
    query = request.GET.get('q', '')
    
    # Get traditional search results
    products = Product.objects.filter(name__icontains=query)
    
    # Get AI recommendations for the query
    with get_ai_client() as client:
        ai_recommendations = client.get_recommendations_local(
            user_preference=query,
            count=5
        )
    
    context = {
        'search_results': products,
        'ai_recommendations': ai_recommendations,
    }
    return render(request, 'search.html', context)
```

## Integration with Django Templates

### Step 1: Add URL (config/urls.py)

```python
urlpatterns = [
    # ...
    path("ai/", include("ai_urls")),
]
```

### Step 2: Use Template (recommendations.html)

```html
<div id="recommendations"></div>

<script>
async function getRecommendations() {
    const response = await fetch('/ai/api/recommendations/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            user_preference: 'casual summer outfit',
            count: 5,
            use_openai: false
        })
    });
    
    const data = await response.json();
    
    const html = data.recommendations
        .map(rec => `
            <div class="product-card">
                <h3>${rec.product_name}</h3>
                <p>${rec.category}</p>
                <p>${rec.reasoning}</p>
            </div>
        `).join('');
    
    document.getElementById('recommendations').innerHTML = html;
}
</script>
```

## Testing the Recommendations

```bash
# Test OpenAI endpoint
curl -X POST "http://127.0.0.1:8001/ai/openai/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_preference": "summer outfit",
    "count": 3
  }'

# Test local ML endpoint
curl -X POST "http://127.0.0.1:8001/ai/local/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_preference": "summer outfit",
    "count": 3
  }'
```

## Performance Tips

1. **Cache recommendations** for popular searches
2. **Limit count to 5-10** for better performance
3. **Use local ML for real-time** needs, OpenAI for quality
4. **Batch process** recommendations during off-peak hours
5. **Pre-compute** recommendations for top categories

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Service not running" | Start FastAPI: `python fastapi_app.py` |
| Empty recommendations | Check if products exist in sample data |
| Slow responses | Use local ML for faster response time |
| OpenAI errors | Verify OPENAI_API_KEY in .env |
| CORS errors | Ensure FastAPI CORS middleware is configured |

## Next Steps

1. ✅ Start both Django and FastAPI servers
2. ✅ Visit API docs at `http://127.0.0.1:8001/docs`
3. ✅ Test endpoints with curl or Postman
4. ✅ Integrate into your templates using examples above
5. ✅ Use `RECOMMENDATIONS_TEMPLATE.html` as reference
6. ✅ Customize for your specific use case

## Files Summary

```
New/Updated Files:
├── fastapi_app.py                           (✏️ Updated - Added endpoints)
├── services/
│   ├── __init__.py                          (✏️ Updated - Added exports)
│   ├── django_client.py                     (✏️ Updated - Added methods)
│   ├── openai_recommendation_service.py     (✨ New)
│   └── recommendation_service.py            (✨ New)
├── EXAMPLES_DJANGO_INTEGRATION.py           (✏️ Updated - Added examples)
├── ai_urls.py                               (✏️ Updated - Added routes)
├── PRODUCT_RECOMMENDATIONS.md               (✨ New - Full documentation)
└── RECOMMENDATIONS_TEMPLATE.html            (✨ New - Frontend example)
```

---

**Total Endpoints Added:** 8 (5 FastAPI + 3 Django API views)  
**Services Created:** 2 (OpenAI + Local ML)  
**New Methods:** 5 (in AIServiceClient)  
**Template Added:** 1 (Beautiful recommendation UI)

---

For detailed information, see [PRODUCT_RECOMMENDATIONS.md](PRODUCT_RECOMMENDATIONS.md)
