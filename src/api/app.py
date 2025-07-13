"""
Main FastAPI application for News Summarizer API.
"""

import asyncio
import logging
import os
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
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from news_summarizer import NewsArticleSummarizer, SummaryConfig
from .models import SummarizeRequest, SummarizeResponse, TaskStatusResponse, HealthResponse

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
    """Manage application lifecycle - startup and shutdown events."""
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


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
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

    # Add routes
    setup_routes(app)

    return app


def setup_routes(app: FastAPI):
    """Setup API routes."""

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
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
        """Submit article for asynchronous summarization."""
        if summarizer is None:
            raise HTTPException(
                status_code=503,
                detail="Summarization service is not available"
            )

        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Initialize task
        task_results[task_id] = {
            'task_id': task_id,
            'status': 'pending',
            'created_at': datetime.now(),
            'title': summarize_request.title,
            'text': summarize_request.text
        }

        # Start background processing
        background_tasks.add_task(
            process_summarization,
            task_id,
            summarize_request.title,
            summarize_request.text,
            summarize_request.config
        )

        return SummarizeResponse(
            task_id=task_id,
            status="pending",
            created_at=task_results[task_id]['created_at']
        )

    @app.get("/task/{task_id}", response_model=TaskStatusResponse)
    @limiter.limit(RATE_LIMIT_BURST)
    async def get_task_status(
        request: Request,
        task_id: str,
        credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
    ):
        """Get the status of a summarization task."""
        if task_id not in task_results:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        task_data = task_results[task_id]
        return TaskStatusResponse(**task_data)

    @app.post("/summarize/sync", response_model=Dict[str, Any])
    @limiter.limit("2/minute")
    async def summarize_article_sync(
        request: Request,
        summarize_request: SummarizeRequest,
        credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
    ):
        """Submit article for synchronous summarization."""
        if summarizer is None:
            raise HTTPException(
                status_code=503,
                detail="Summarization service is not available"
            )

        # Check text length for sync processing
        if len(summarize_request.text) > 10000:
            raise HTTPException(
                status_code=413,
                detail="Text too long for synchronous processing"
            )

        try:
            start_time = time.time()

            # Apply custom config if provided
            if summarize_request.config:
                custom_config = SummaryConfig(**summarize_request.config)
                local_summarizer = NewsArticleSummarizer(custom_config)
                summary = local_summarizer.summarize_article(
                    summarize_request.title,
                    summarize_request.text
                )
            else:
                summary = summarizer.summarize_article(
                    summarize_request.title,
                    summarize_request.text
                )

            processing_time = time.time() - start_time

            return {
                "status": "completed",
                "summary": summary,
                "processing_time": processing_time,
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error(f"Synchronous summarization error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Summarization failed: {str(e)}"
            )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler."""
        logger.error(f"Global exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "message": str(exc)}
        )


# Security functions
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for authenticated endpoints."""
    if not credentials or credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials


async def cleanup_old_tasks():
    """Clean up old task results to prevent memory leaks."""
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
    """Process summarization in background."""
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


# Create the app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
