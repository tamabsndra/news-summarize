# News Summarizer API 🚀

REST API yang aman dan handal untuk meringkas artikel berita dengan format yang menarik untuk audiens Gen Z/Millennial.

## 🌟 Fitur Utama

- **Asynchronous Processing** - Tidak akan crash meskipun proses lama
- **Secure Authentication** - API key authentication dengan rate limiting
- **Reliable Performance** - Built-in error handling dan recovery
- **Well Documented** - OpenAPI/Swagger documentation
- **Easy to Use** - Simple REST endpoints
- **Scalable** - Docker ready dengan Redis support

## 📋 Daftar Isi

- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Request/Response Examples](#request-response-examples)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Testing](#testing)
- [Monitoring](#monitoring)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd news-summarizer

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config.example.env .env
# Edit .env file dengan konfigurasi Anda
```

### 2. Start API Server

```bash
# Development
python api.py

# Production dengan Uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000

# Docker (recommended)
docker-compose up -d
```

### 3. Test API

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## 🔐 Authentication

API menggunakan Bearer token authentication. Setiap request harus menyertakan header:

```bash
Authorization: Bearer your-api-key-here
```

**⚠️ Keamanan:**
- Ganti default API key di environment variables
- Simpan API key dengan aman
- Gunakan HTTPS di production

## 📡 API Endpoints

### Health Check
```
GET /health
```
Check status API dan model.

### Asynchronous Summarization (Recommended)
```
POST /summarize
```
Submit artikel untuk diproses secara asynchronous.

### Task Status
```
GET /task/{task_id}
```
Cek status dan hasil dari task yang sedang diproses.

### Synchronous Summarization
```
POST /summarize/sync
```
Proses artikel secara synchronous (untuk artikel pendek).

## 📝 Request/Response Examples

### 1. Health Check

**Request:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "model_loaded": true
}
```

### 2. Asynchronous Summarization

**Request:**
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Breaking News: Major Tech Breakthrough",
    "text": "A revolutionary new technology has been developed that promises to change the industry forever. The breakthrough, announced by leading researchers, represents years of collaborative effort and substantial investment in cutting-edge development. Early testing phases have shown remarkable results with efficiency improvements of up to 300% compared to current industry standards..."
  }'
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 3. Check Task Status

**Request:**
```bash
curl -X GET "http://localhost:8000/task/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer your-api-key"
```

**Response (Completed):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "summary": "• **Revolutionary technology breakthrough announced by leading researchers** || A groundbreaking technological innovation has emerged that promises to revolutionize the entire industry landscape.\n• **Efficiency improvements of up to 300% compared to current standards** || Early testing phases have shown remarkable results with significant performance enhancements.\n• **Major corporations investing heavily in the new technology** || Industry experts are calling this development a game-changer that will reshape competitive dynamics.\n\n|ht|#Technology #Innovation #Breakthrough #Industry\n|st|Revolutionary Tech Breakthrough Changes Industry\n|ot|A revolutionary new technology has been developed that promises to change the industry forever. The breakthrough represents years of collaborative effort and substantial investment, with early testing showing 300% efficiency improvements. This development is expected to become the new industry standard within five years.",
  "processing_time": 12.5,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:12Z"
}
```

### 4. Synchronous Summarization

**Request:**
```bash
curl -X POST "http://localhost:8000/summarize/sync" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Quick News Update",
    "text": "Short article content for immediate processing..."
  }'
```

**Response:**
```json
{
  "status": "completed",
  "summary": "• **Quick news update processed immediately** || Short article content summarized for immediate use.\n\n|ht|#News #Update\n|st|Quick News Update\n|ot|Short article content for immediate processing provides quick information for readers.",
  "processing_time": 3.2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 5. Custom Configuration

**Request:**
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Custom Article",
    "text": "Article content...",
    "config": {
      "max_bullet_points": 3,
      "min_hashtags": 2,
      "max_hashtags": 3
    }
  }'
```

## ⚠️ Error Handling

API mengembalikan error codes yang jelas:

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | Success | Request berhasil |
| 401 | Unauthorized | API key salah atau missing |
| 422 | Validation Error | Input tidak valid |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Model tidak tersedia |

**Example Error Response:**
```json
{
  "error": "Validation Error",
  "message": "Text content must be at least 100 characters",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🚦 Rate Limiting

API menggunakan rate limiting untuk mencegah abuse:

- **Default**: 5 requests per minute
- **Burst**: 10 requests per hour
- **Sync endpoint**: 2 requests per minute

Rate limits dapat dikonfigurasi melalui environment variables:

```bash
RATE_LIMIT_REQUESTS=5/minute
RATE_LIMIT_BURST=10/hour
```

## ⚙️ Configuration

### Environment Variables

```bash
# Security
API_KEY=your-secure-api-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Rate Limiting
RATE_LIMIT_REQUESTS=5/minute
RATE_LIMIT_BURST=10/hour

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Redis (optional)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=

# Model
MODEL_CACHE_DIR=./models
MAX_CONCURRENT_TASKS=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

### Input Validation

| Field | Min Length | Max Length | Required | Notes |
|-------|------------|------------|----------|-------|
| title | 1 | 500 | Yes | - |
| text | 100 | 50,000 | Yes | **HTML content supported** - automatically cleaned |
| config | - | - | No | - |

### HTML Content Support

API secara otomatis membersihkan HTML tags dan entities dari text input:

**✅ Supported HTML Elements:**
- `<p>`, `<span>`, `<div>`, `<a>`, `<strong>`, `<em>`, `<h1-h6>`
- HTML entities (`&amp;`, `&quot;`, `&lt;`, `&gt;`, `&apos;`)
- URLs dan links
- Web artifacts dan metadata

**📝 Example:**
```json
{
  "title": "News Article",
  "text": "<p>This is <strong>important</strong> news with <a href='#'>links</a></p>"
}
```

**🧹 Automatically cleaned to:**
```
"This is important news with links"
```

## 🐳 Deployment

### Docker Compose (Recommended)

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_KEY=your-secure-api-key
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
```

**Start services:**
```bash
docker-compose up -d
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export API_KEY=your-secure-api-key
export REDIS_URL=redis://localhost:6379

# Start with Gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Production Considerations

1. **Reverse Proxy**: Gunakan Nginx/Apache
2. **SSL Certificate**: Setup HTTPS
3. **Load Balancing**: Multiple instances
4. **Monitoring**: Prometheus + Grafana
5. **Logging**: Centralized logging
6. **Database**: PostgreSQL untuk production

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest test_api.py -v

# Run specific test class
pytest test_api.py::TestAuthentication -v

# Run with coverage
pytest --cov=api test_api.py
```

### Test Coverage

- Authentication & Authorization
- Input validation
- Rate limiting
- Error handling
- Async processing
- Task management
- Custom configuration

## 📊 Monitoring

### Health Endpoints

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed metrics (if enabled)
curl http://localhost:8000/metrics
```

### Logging

API menggunakan structured logging:

```python
2024-01-15 10:30:00 - api - INFO - Starting News Summarizer API...
2024-01-15 10:30:05 - api - INFO - Model loaded successfully
2024-01-15 10:30:10 - api - INFO - Created summarization task 550e8400-e29b-41d4-a716-446655440000
2024-01-15 10:30:22 - api - INFO - Completed summarization for task 550e8400-e29b-41d4-a716-446655440000 in 12.50s
```

### Performance Metrics

- Request latency
- Task completion times
- Error rates
- Memory usage
- Model performance

## 🔧 Troubleshooting

### Common Issues

1. **Model Loading Error**
   ```bash
   # Check available memory
   free -h
   # Ensure GPU is available (if using)
   nvidia-smi
   ```

2. **Rate Limit Exceeded**
   ```bash
   # Check current limits
   curl -I http://localhost:8000/health
   # Adjust in environment variables
   ```

3. **Task Timeout**
   ```bash
   # Check task status
   curl -H "Authorization: Bearer your-key" http://localhost:8000/task/task-id
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Start API in debug mode
python api.py
```

## 📖 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### OpenAPI Specification

API menggunakan OpenAPI 3.0 specification dengan:
- Detailed endpoint descriptions
- Request/response schemas
- Authentication requirements
- Error responses
- Example requests

## 🛡️ Security Best Practices

1. **API Key Management**
   - Rotate keys regularly
   - Use environment variables
   - Monitor usage patterns

2. **Rate Limiting**
   - Implement proper limits
   - Monitor abuse patterns
   - Use Redis for distributed limiting

3. **Input Validation**
   - Validate all inputs
   - Sanitize content
   - Prevent injection attacks

4. **HTTPS**
   - Use SSL certificates
   - Redirect HTTP to HTTPS
   - Implement HSTS headers

## 🤝 Integration Examples

### Python Client

```python
from example_usage import NewsApiClient

client = NewsApiClient(
    base_url="https://your-api.com",
    api_key="your-secure-api-key"
)

# Async processing
result = client.summarize_async("Title", "Article content...")
summary = client.wait_for_completion(result["task_id"])
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'https://your-api.com',
  headers: {
    'Authorization': 'Bearer your-secure-api-key',
    'Content-Type': 'application/json'
  }
});

// Async processing
const response = await client.post('/summarize', {
  title: 'Article Title',
  text: 'Article content...'
});

const taskId = response.data.task_id;
```

### cURL Examples

```bash
# Submit article
curl -X POST "https://your-api.com/summarize" \
  -H "Authorization: Bearer your-key" \
  -H "Content-Type: application/json" \
  -d '{"title": "Title", "text": "Content..."}'

# Check status
curl -X GET "https://your-api.com/task/task-id" \
  -H "Authorization: Bearer your-key"
```

## 📈 Performance Optimization

### Model Optimization

1. **GPU Usage**: Enable CUDA if available
2. **Model Caching**: Cache loaded models
3. **Batch Processing**: Process multiple articles
4. **Memory Management**: Monitor memory usage

### API Optimization

1. **Async Processing**: Use background tasks
2. **Connection Pooling**: Reuse connections
3. **Response Compression**: Enable gzip
4. **Caching**: Redis for frequent requests

## 🆘 Support

### Getting Help

1. **Documentation**: Check this README
2. **API Docs**: Visit `/docs` endpoint
3. **Issues**: Create GitHub issue
4. **Examples**: See `example_usage.py`

### Contributing

1. Fork repository
2. Create feature branch
3. Add tests
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**🎉 Selamat! API News Summarizer siap digunakan!**

API ini dirancang untuk memberikan performa tinggi, keamanan yang baik, dan kemudahan penggunaan. Untuk pertanyaan lebih lanjut, silakan buka issue di repository atau hubungi tim development.
