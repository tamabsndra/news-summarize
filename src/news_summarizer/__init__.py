"""
News Summarizer Package

A Python package for summarizing news articles with Gen Z/Millennial focus.
"""

from .core import NewsArticleSummarizer
from .config import SummaryConfig, FastSummaryConfig
from .utils import clean_text, extract_key_data

__version__ = "1.0.0"
__all__ = ["NewsArticleSummarizer", "SummaryConfig", "FastSummaryConfig", "clean_text", "extract_key_data"]


def summarize_news_article(title: str, article_text: str, config: SummaryConfig = None) -> dict:
    """
    Convenience function for quick article summarization.

    Args:
        title: Article title
        article_text: Article content
        config: Optional configuration

    Returns:
        Dictionary with summary components
    """
    summarizer = NewsArticleSummarizer(config)
    return summarizer.summarize_article(title, article_text)
