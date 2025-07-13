# News Summarizer for Gen Z/Millennials 📰✨

A Python-based tool that automatically converts long news articles into engaging, casual summaries tailored for younger audiences. Perfect for creating quick, relatable content that captures attention and delivers key information in an accessible format.

## Features

- **Smart Summarization**: Uses Facebook's BART model for high-quality text summarization
- **Automatic Text Chunking**: Handles long articles by intelligently splitting them into manageable chunks
- **Structured Output**: Produces consistently formatted summaries with bullet points, hashtags, and journalistic paragraphs
- **Gen Z/Millennial Focus**: Optimized for casual, engaging tone that resonates with younger audiences
- **Configurable**: Easily customizable parameters for different use cases
- **Modular Design**: Can be used as a standalone script or imported as a module

## Installation

1. **Clone or download the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **First run will download the BART model** (this may take a few minutes)

## Quick Start

### Basic Usage

```python
from news_summarizer import NewsArticleSummarizer

# Initialize the summarizer
summarizer = NewsArticleSummarizer()

# Your news article text
article_text = """
Your long news article text goes here...
"""

# Generate summary
summary = summarizer.summarize_article(article_text)
print(summary)
```

### Convenience Function

```python
from news_summarizer import summarize_news_article

# One-liner usage
summary = summarize_news_article(article_text)
print(summary)
```

### Running the Example

```bash
python news_summarizer.py
```

## Output Format

The tool generates summaries in this specific format:

```
• **Descriptive bullet point title here** || Summary of the key point
• **Another important point about the news** || Details about this aspect
• **Third major point from the article** || More information here

|ht|#RelevantHashtag #NewsTag #TopicTag
|st|Short Catchy Title Here
|ot|Engaging journalistic paragraph that covers who, what, when, where, why, and how. This paragraph provides context and includes relevant quotes when available. It ends with a strong takeaway or closing thought that ties everything together.
```

### Example Output

```
• **Apple announces revolutionary iPhone 15 Pro Max** || Tech giant Apple announced today that it will be releasing a new iPhone model with revolutionary camera technology.
• **48-megapixel main camera with advanced computational photography** || The iPhone 15 Pro Max will feature a 48-megapixel main camera with advanced computational photography capabilities.
• **Tim Cook reveals device availability starting next** || Apple CEO Tim Cook revealed during the keynote presentation that the new device will be available starting next month.

|ht|#Apple #Iphone #Technology #Launch
|st|Apple Announces Revolutionary iPhone 15 Pro Max
|ot|Apple made headlines today. Tech giant Apple announced today that it will be releasing a new iPhone model with revolutionary camera technology. The iPhone 15 Pro Max will feature a 48-megapixel main camera with advanced computational photography capabilities. This development could reshape the landscape moving forward.
```

## Configuration

### Custom Configuration

```python
from news_summarizer import NewsArticleSummarizer, SummaryConfig

# Create custom configuration
config = SummaryConfig(
    max_chunk_tokens=800,        # Maximum tokens per chunk
    min_bullet_points=3,         # Minimum number of bullet points
    max_bullet_points=5,         # Maximum number of bullet points
    min_hashtags=2,              # Minimum number of hashtags
    max_hashtags=4,              # Maximum number of hashtags
    max_title_words=10,          # Maximum words in short title
    model_name="facebook/bart-large-cnn"  # Hugging Face model name
)

# Initialize with custom config
summarizer = NewsArticleSummarizer(config)
```

### Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_chunk_tokens` | 1000 | Maximum tokens per text chunk |
| `min_bullet_points` | 3 | Minimum number of bullet points |
| `max_bullet_points` | 5 | Maximum number of bullet points |
| `min_hashtags` | 2 | Minimum number of hashtags |
| `max_hashtags` | 4 | Maximum number of hashtags |
| `max_title_words` | 10 | Maximum words in short title |
| `model_name` | "facebook/bart-large-cnn" | Hugging Face model to use |

## API Reference

### `NewsArticleSummarizer`

Main class for news summarization.

#### Methods

- `__init__(config: Optional[SummaryConfig] = None)`: Initialize the summarizer
- `summarize_article(article_text: str) -> str`: Generate formatted summary

### `summarize_news_article(article_text: str, config: Optional[SummaryConfig] = None) -> str`

Convenience function for one-off summarization.

## Requirements

- Python 3.7+
- PyTorch
- Transformers (Hugging Face)
- NLTK
- See `requirements.txt` for full list

## Performance Notes

- **First run**: Model download may take 3-5 minutes
- **GPU acceleration**: Automatically uses GPU if available
- **Memory usage**: Approximately 2-3GB RAM for the BART model
- **Processing time**: ~5-15 seconds per article depending on length

## Text Processing Features

- **HTML tag removal**: Automatically strips HTML tags
- **Metadata cleaning**: Removes common web artifacts like `[Photo]`, `(AP)`
- **Smart chunking**: Preserves sentence boundaries when splitting long texts
- **Fallback handling**: Graceful degradation if model fails

## Troubleshooting

### Common Issues

1. **Model download fails**: Check internet connection and try again
2. **Out of memory**: Reduce `max_chunk_tokens` in configuration
3. **Poor summaries**: Try different model (e.g., `facebook/bart-large`)
4. **Empty output**: Ensure input text is substantial (>100 words)

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - see LICENSE file for details.

## Models Used

- **Primary**: `facebook/bart-large-cnn` - Optimized for news summarization
- **Alternative**: Any Hugging Face summarization model can be configured

## Acknowledgments

- Built with Hugging Face Transformers
- Uses Facebook's BART model for summarization
- NLTK for text processing
