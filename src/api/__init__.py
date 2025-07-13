"""
API Package for News Summarizer

FastAPI-based REST API for news article summarization.
"""

from api.app import create_app
from api.models import SummarizeRequest, SummarizeResponse, TaskStatusResponse, HealthResponse
from api.client import NewsApiClient

__all__ = ["create_app", "SummarizeRequest", "SummarizeResponse", "TaskStatusResponse", "HealthResponse", "NewsApiClient"]
