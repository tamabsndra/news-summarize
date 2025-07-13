"""
API models and schemas for request/response validation.
"""

import re
from datetime import datetime
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator


class SummarizeRequest(BaseModel):
    """Request model for article summarization."""
    title: str = Field(..., min_length=1, max_length=500, description="Article title")
    text: str = Field(..., min_length=100, max_length=50000, description="Article text content")
    config: Optional[Dict[str, Any]] = Field(None, description="Optional configuration parameters")

    @field_validator('text')
    @classmethod
    def validate_text_content(cls, v):
        """Validate and clean text content."""
        # First clean HTML tags and entities
        cleaned_text = clean_html_text(v)

        # Validate length after cleaning
        if len(cleaned_text.strip()) < 100:
            raise ValueError('Text content must be at least 100 characters after HTML cleaning')

        return cleaned_text.strip()

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty."""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class SummarizeResponse(BaseModel):
    """Response model for successful summarization."""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status")
    summary: Optional[Dict[str, str]] = Field(None, description="Generated summary with title, paragraph, and hashtags")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    created_at: datetime = Field(..., description="Task creation timestamp")


class TaskStatusResponse(BaseModel):
    """Response model for task status check."""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status: pending, processing, completed, failed")
    summary: Optional[Dict[str, str]] = Field(None, description="Generated summary with title, paragraph, and hashtags if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    created_at: datetime = Field(..., description="Task creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="API health status")
    timestamp: datetime = Field(..., description="Current timestamp")
    model_loaded: bool = Field(..., description="Whether the model is loaded")


def clean_html_text(text: str) -> str:
    """
    Clean HTML tags and entities from text content.

    Args:
        text: Input text that may contain HTML

    Returns:
        Cleaned text without HTML tags
    """
    # Remove HTML tags but preserve inner text
    text = re.sub(r'<[^>]+>', '', text)

    # Remove common web artifacts
    text = re.sub(r'\[[^\]]*\]', '', text)  # Brackets like [Photo]
    text = re.sub(r'\([^)]*\)', '', text)  # Parentheses with metadata

    # Remove URLs
    text = re.sub(r'https?://[^\s]+', '', text)

    # Remove image captions and photo credits
    text = re.sub(r'AFP/Getty Images|AP|Reuters|Getty Images', '', text)
    text = re.sub(r'This picture taken on.*?\.', '', text)
    text = re.sub(r'Related article.*?$', '', text, flags=re.MULTILINE)

    # Remove navigation elements and web artifacts
    text = re.sub(r'CNN\s*—\s*', '', text)
    text = re.sub(r'&amp;|&lt;|&gt;|&quot;|&apos;',
                  lambda m: {'&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&apos;': "'"}.get(m.group(), m.group()), text)

    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())

    # Remove empty lines and clean up paragraph breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text
