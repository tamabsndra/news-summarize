#!/usr/bin/env python3
"""
Main entry point for News Summarizer API server.
"""

import uvicorn
from src.api.app import create_app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
