#!/usr/bin/env python3
"""
News Summarizer API

A FastAPI-based REST API for news article summarization.
Provides secure, reliable, and well-documented endpoints for summarizing news articles.
"""

import asyncio
import logging
import os
import re
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from news_summarizer import NewsArticleSummarizer, SummaryConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
summarizer: Optional[NewsArticleSummarizer] = None
task_results: Dict[str, Dict[str, Any]] = {}
limiter = Limiter(key_func=get_remote_address)

# Security configuration
API_KEY = os.getenv("API_KEY", "your-secure-api-key-here")
security = HTTPBearer(auto_error=False)

# Rate limiting configuration
RATE_LIMIT_REQUESTS = os.getenv("RATE_LIMIT_REQUESTS", "5/minute")
RATE_LIMIT_BURST = os.getenv("RATE_LIMIT_BURST", "10/hour")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown events"""
    # Startup
    logger.info("Starting News Summarizer API...")
    global summarizer

    try:
        logger.info("Loading summarization model...")
        summarizer = NewsArticleSummarizer()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

    # Cleanup old task results every hour
    asyncio.create_task(cleanup_old_tasks())

    yield

    # Shutdown
    logger.info("Shutting down News Summarizer API...")

# Initialize FastAPI app
app = FastAPI(
    title="News Summarizer API",
    description="Secure and reliable API for summarizing news articles for Gen Z/Millennial audiences",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Request/Response models
class SummarizeRequest(BaseModel):
    """Request model for article summarization"""
    title: str = Field(..., min_length=1, max_length=500, description="Article title")
    text: str = Field(..., min_length=100, max_length=50000, description="Article text content")
    config: Optional[Dict[str, Any]] = Field(None, description="Optional configuration parameters")

    @field_validator('text')
    @classmethod
    def validate_text_content(cls, v):
        """Validate and clean text content"""
        # First clean HTML tags and entities
        cleaned_text = clean_html_text(v)

        # Validate length after cleaning
        if len(cleaned_text.strip()) < 100:
            raise ValueError('Text content must be at least 100 characters after HTML cleaning')

        return cleaned_text.strip()

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty"""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

class SummarizeResponse(BaseModel):
    """Response model for successful summarization"""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status")
    summary: Optional[Dict[str, str]] = Field(None, description="Generated summary with title, paragraph, and hashtags")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    created_at: datetime = Field(..., description="Task creation timestamp")

class TaskStatusResponse(BaseModel):
    """Response model for task status check"""
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status: pending, processing, completed, failed")
    summary: Optional[Dict[str, str]] = Field(None, description="Generated summary with title, paragraph, and hashtags if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    created_at: datetime = Field(..., description="Task creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="API health status")
    timestamp: datetime = Field(..., description="Current timestamp")
    model_loaded: bool = Field(..., description="Whether the model is loaded")

# Utility functions
def clean_html_text(text: str) -> str:
    """
    Clean HTML tags and entities from text content

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

# Security functions
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for authenticated endpoints"""
    if not credentials or credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials

async def cleanup_old_tasks():
    """Clean up old task results to prevent memory leaks"""
    while True:
        try:
            current_time = datetime.now()
            expired_tasks = [
                task_id for task_id, task_data in task_results.items()
                if current_time - task_data['created_at'] > timedelta(hours=24)
            ]

            for task_id in expired_tasks:
                del task_results[task_id]

            if expired_tasks:
                logger.info(f"Cleaned up {len(expired_tasks)} expired tasks")

        except Exception as e:
            logger.error(f"Error cleaning up tasks: {e}")

        await asyncio.sleep(3600)  # Run every hour

async def process_summarization(task_id: str, title: str, text: str, config: Optional[Dict[str, Any]] = None):
    """Process summarization in background"""
    task_results[task_id]['status'] = 'processing'
    task_results[task_id]['started_at'] = datetime.now()

    try:
        logger.info(f"Starting summarization for task {task_id}")

        # Apply custom config if provided
        if config:
            custom_config = SummaryConfig(**config)
            local_summarizer = NewsArticleSummarizer(custom_config)
            summary = local_summarizer.summarize_article(title, text)
        else:
            summary = summarizer.summarize_article(title, text)

        # Update task results
        completed_at = datetime.now()
        processing_time = (completed_at - task_results[task_id]['started_at']).total_seconds()

        task_results[task_id].update({
            'status': 'completed',
            'summary': summary,
            'completed_at': completed_at,
            'processing_time': processing_time
        })

        logger.info(f"Completed summarization for task {task_id} in {processing_time:.2f}s")

    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        task_results[task_id].update({
            'status': 'failed',
            'error': str(e),
            'completed_at': datetime.now()
        })

# API Routes

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        model_loaded=summarizer is not None
    )

@app.post("/summarize", response_model=SummarizeResponse)
@limiter.limit(RATE_LIMIT_REQUESTS)
async def summarize_article(
    request: Request,
    summarize_request: SummarizeRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """
    Summarize a news article asynchronously.

    This endpoint accepts a news article title and text, then processes it
    asynchronously to generate a formatted summary suitable for Gen Z/Millennial audiences.

    The response includes a task_id that can be used to check the status and
    retrieve the results using the /task/{task_id} endpoint.
    """
    if not summarizer:
        raise HTTPException(
            status_code=503,
            detail="Summarization service is not available. Please try again later."
        )

    # Generate unique task ID
    task_id = str(uuid.uuid5(uuid.NAMESPACE_URL, summarize_request.title))

    # Initialize task tracking
    task_results[task_id] = {
        'task_id': task_id,
        'status': 'pending',
        'created_at': datetime.now(),
        'title': summarize_request.title,
        'text_length': len(summarize_request.text)
    }

    # Start background processing
    background_tasks.add_task(
        process_summarization,
        task_id,
        summarize_request.title,
        summarize_request.text,
        summarize_request.config
    )

    logger.info(f"Created summarization task {task_id}")

    return SummarizeResponse(
        task_id=task_id,
        status='pending',
        created_at=task_results[task_id]['created_at']
    )

@app.get("/task/{task_id}", response_model=TaskStatusResponse)
@limiter.limit(RATE_LIMIT_BURST)
async def get_task_status(
    request: Request,
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """
    Get the status and results of a summarization task.

    Use this endpoint to check the progress of your summarization request
    and retrieve the results once processing is complete.
    """
    if task_id not in task_results:
        raise HTTPException(
            status_code=404,
            detail="Task not found. Task may have expired or never existed."
        )

    task_data = task_results[task_id]

    return TaskStatusResponse(
        task_id=task_id,
        status=task_data['status'],
        summary=task_data.get('summary'),
        error=task_data.get('error'),
        processing_time=task_data.get('processing_time'),
        created_at=task_data['created_at'],
        completed_at=task_data.get('completed_at')
    )

@app.post("/summarize/sync", response_model=Dict[str, Any])
@limiter.limit("2/minute")
async def summarize_article_sync(
    request: Request,
    summarize_request: SummarizeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """
    Synchronous summarization endpoint for shorter articles.

    ⚠️ Warning: This endpoint processes requests synchronously and may timeout
    for very long articles. Use the async /summarize endpoint for better reliability.
    """
    if not summarizer:
        raise HTTPException(
            status_code=503,
            detail="Summarization service is not available. Please try again later."
        )

    # Limit sync processing to shorter articles
    if len(summarize_request.text) > 10000:
        raise HTTPException(
            status_code=413,
            detail="Article too long for synchronous processing. Use the async /summarize endpoint."
        )

    try:
        start_time = time.time()

        # Apply custom config if provided
        if summarize_request.config:
            custom_config = SummaryConfig(**summarize_request.config)
            local_summarizer = NewsArticleSummarizer(custom_config)
            summary = local_summarizer.summarize_article(summarize_request.title, summarize_request.text)
        else:
            summary = summarizer.summarize_article(summarize_request.title, summarize_request.text)

        processing_time = time.time() - start_time

        logger.info(f"Completed synchronous summarization in {processing_time:.2f}s")

        return {
            "status": "completed",
            "summary": summary,
            "processing_time": processing_time,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"Error in synchronous summarization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Summarization failed: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
