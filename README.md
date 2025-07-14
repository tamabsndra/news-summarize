# News Summarizer 📰✨

A modern Python package for summarizing news articles with a Gen Z/Millennial focus. Transform lengthy articles into engaging, casual summaries that capture attention and deliver key information in an accessible format.

## 🌟 Features

- **🧠 Smart Summarization**: Uses financial-specialized Pegasus model for high-quality financial text summarization
- **💹 AI-Powered Sentiment Analysis**: Advanced financial sentiment analysis using DistilRoBERTa model fine-tuned on financial news
- **🔄 Automatic Text Chunking**: Handles long articles by intelligently splitting content
- **🎯 Gen Z/Millennial Focus**: Optimized for casual, engaging tone with financial trading slang
- **📊 Structured Output**: Produces consistently formatted summaries with title, paragraph, and hashtags
- **🚀 Fast API**: REST API with async processing and rate limiting
- **🖥️ CLI Interface**: Command-line tool for batch processing
- **🧩 Modular Design**: Can be used as a library, CLI tool, or API service
- **🐳 Docker Ready**: Includes Docker configuration for easy deployment

## 📦 Installation

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd news-summarizer

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e ".[dev]"
```

### Docker Installation

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t news-summarizer .
docker run -p 8000:8000 news-summarizer
```

## 🚀 Usage

### 1. Python Library

```python
from src.news_summarizer import NewsArticleSummarizer, SummaryConfig

# Basic usage
summarizer = NewsArticleSummarizer()
summary = summarizer.summarize_article("Article Title", "Article content...")

print(summary)
# Output: {
#   'title': 'Short Catchy Title',
#   'paragraph': 'Engaging paragraph with Gen Z flair...',
#   'hashtags': '#News #Finance #Trading #Market'
# }

# With custom configuration
config = SummaryConfig(
    max_hashtags=3,
    max_title_words=5,
    min_bullet_points=2
)
summarizer = NewsArticleSummarizer(config)
summary = summarizer.summarize_article("Title", "Content...")
```

### 2. Command Line Interface

```bash
# Basic usage
python main.py "Article Title" "Article content..."

# Read from file
python main.py "Title" "$(cat article.txt)"

# With custom options
python main.py "Title" "Content" --max-hashtags 3 --format text --output summary.txt

# Using config file
python main.py "Title" "Content" --config config.json
```

### 3. REST API

#### Starting the API Server

```bash
# Development
python api_server.py

# Production with custom settings
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4

# Docker
docker-compose up -d
```

#### API Usage

```bash
# Health check
curl http://localhost:8000/health

# Synchronous summarization
curl -X POST "http://localhost:8000/summarize/sync" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Breaking News",
    "text": "Your article content here..."
  }'

# Asynchronous summarization
curl -X POST "http://localhost:8000/summarize" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Breaking News",
    "text": "Your article content here..."
  }'

# Check task status
curl -X GET "http://localhost:8000/task/{task_id}" \
  -H "Authorization: Bearer your-api-key"
```

#### Using the API Client

```python
from src.api.client import NewsApiClient

client = NewsApiClient(api_key="your-api-key")

# Health check
health = client.health_check()

# Synchronous summarization
result = client.summarize_sync("Title", "Content")

# Asynchronous summarization
task = client.summarize_async("Title", "Content")
result = client.wait_for_completion(task["task_id"])
```

## 📋 Configuration

### Summary Configuration

```python
from src.news_summarizer import SummaryConfig

config = SummaryConfig(
    max_chunk_tokens=1000,        # Maximum tokens per chunk
    min_bullet_points=3,          # Minimum number of bullet points
    max_bullet_points=5,          # Maximum number of bullet points
    min_hashtags=2,               # Minimum number of hashtags
    max_hashtags=4,               # Maximum number of hashtags
    max_title_words=7,            # Maximum words in title
    model_name="human-centered-summarization/financial-summarization-pegasus",  # Financial summarization model
    sentiment_model_name="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"  # Financial sentiment analysis model
)
```

### Environment Variables

```bash
# API Configuration
API_KEY=your-secure-api-key-here
RATE_LIMIT_REQUESTS=5/minute
RATE_LIMIT_BURST=10/hour

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
```

## 🏗️ Project Structure

```
news-summarizer/
├── src/
│   ├── news_summarizer/          # Core summarization package
│   │   ├── __init__.py
│   │   ├── core.py              # Main summarizer class
│   │   ├── config.py            # Configuration and constants
│   │   └── utils.py             # Utility functions
│   ├── api/                     # FastAPI application
│   │   ├── __init__.py
│   │   ├── app.py              # Main API application
│   │   ├── models.py           # Pydantic models
│   │   └── client.py           # API client
│   └── cli/                     # Command line interface
│       ├── __init__.py
│       └── main.py             # CLI application
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── examples/                   # Usage examples
│   ├── basic_usage.py
│   ├── api_usage.py
│   └── test_article.json
├── main.py                     # CLI entry point
├── api_server.py              # API server entry point
├── requirements.txt           # Dependencies
├── pyproject.toml            # Modern Python packaging
├── setup.py                  # Package setup
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile               # Docker image configuration
└── README.md               # This file
```

## 🔌 API Endpoints

### Health Check
- `GET /health` - Check API health and model status

### Summarization
- `POST /summarize` - Asynchronous summarization (recommended)
- `POST /summarize/sync` - Synchronous summarization (for short articles)
- `GET /task/{task_id}` - Check task status and results

### Rate Limits
- **Default**: 5 requests per minute
- **Burst**: 10 requests per hour
- **Sync endpoint**: 2 requests per minute

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/

# Run API tests (requires running API server)
pytest tests/unit/test_api.py
```

## 📊 Output Format

The summarizer generates structured output optimized for Gen Z/Millennial audiences:

```json
{
  "title": "Market Absolutely Ripping Today",
  "paragraph": "Bitcoin is absolutely sending it today 🚀 The numbers are going parabolic, and smart money is probably taking notice. This crypto surge represents a significant shift in market sentiment, with trading volume hitting new highs. Perfect time to reassess your position sizing.",
  "hashtags": "#Bitcoin #Crypto #Trading #Market"
}
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone <repository-url>
cd news-summarizer
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/
flake8 src/ tests/

# Type checking
mypy src/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🚦 Performance & Monitoring

### Performance Notes
- **First run**: Model download may take 3-5 minutes
- **GPU acceleration**: Automatically uses GPU if available
- **Memory usage**: Approximately 2-3GB RAM for BART model
- **Processing time**: ~5-15 seconds per article depending on length

### Health Monitoring
- Health check endpoint: `/health`
- Metrics: Response time, success rate, model status
- Logging: Structured logging with configurable levels

## 🔧 Troubleshooting

### Common Issues

1. **Model download fails**
   - Check internet connection
   - Verify Hugging Face Hub access
   - Try: `pip install --upgrade transformers`

2. **Out of memory errors**
   - Reduce `max_chunk_tokens` in configuration
   - Use CPU instead of GPU
   - Process shorter articles

3. **API authentication errors**
   - Check API key in environment variables
   - Verify Authorization header format
   - Ensure API key matches server configuration

4. **Poor summary quality**
   - Try different model (e.g., `facebook/bart-large`)
   - Adjust configuration parameters
   - Ensure input text is substantial (>100 words)

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for specific components
logging.getLogger('src.news_summarizer').setLevel(logging.DEBUG)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Hugging Face Transformers](https://huggingface.co/transformers/)
- Uses Facebook's BART model for summarization
- [FastAPI](https://fastapi.tiangolo.com/) for the REST API
- [NLTK](https://www.nltk.org/) for text processing

## 📞 Support

- 📧 Email: [support@example.com](mailto:support@example.com)
- 💬 Issues: [GitHub Issues](https://github.com/yourusername/news-summarizer/issues)
- 📚 Documentation: [GitHub Wiki](https://github.com/yourusername/news-summarizer/wiki)

---

Made with ❤️ for the Gen Z/Millennial trading community
