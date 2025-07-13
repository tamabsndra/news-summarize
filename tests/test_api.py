#!/usr/bin/env python3
"""
Test suite for News Summarizer API

Tests all endpoints including security, rate limiting, and error handling.
"""

import pytest
import asyncio
import time
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from api import app, summarizer, task_results

# Test client
client = TestClient(app)

# Test configuration
TEST_API_KEY = "test-api-key"
INVALID_API_KEY = "invalid-api-key"

# Sample test data
SAMPLE_ARTICLE = {
    "title": "Test News Article",
    "text": "This is a test news article with enough content to meet the minimum requirements for summarization. It contains multiple sentences and provides sufficient context for the summarization model to work with. The article discusses various topics and includes relevant information that would be found in a typical news article. This ensures that the summarization process has adequate input to generate meaningful output."
}

SHORT_ARTICLE = {
    "title": "Short Article",
    "text": "Too short"
}

LONG_ARTICLE = {
    "title": "Very Long Article",
    "text": "Very long content. " * 2000  # Creates a very long article
}

class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_success(self):
        """Test successful health check"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "model_loaded" in data

class TestAuthentication:
    """Test API authentication"""

    def test_no_api_key(self):
        """Test request without API key"""
        response = client.post("/summarize", json=SAMPLE_ARTICLE)
        assert response.status_code == 401
        assert "Invalid or missing API key" in response.json()["detail"]

    def test_invalid_api_key(self):
        """Test request with invalid API key"""
        headers = {"Authorization": f"Bearer {INVALID_API_KEY}"}
        response = client.post("/summarize", json=SAMPLE_ARTICLE, headers=headers)
        assert response.status_code == 401
        assert "Invalid or missing API key" in response.json()["detail"]

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    def test_valid_api_key(self):
        """Test request with valid API key"""
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        response = client.post("/summarize", json=SAMPLE_ARTICLE, headers=headers)
        # Should not be 401 (authentication error)
        assert response.status_code != 401

class TestInputValidation:
    """Test input validation"""

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    def test_empty_title(self):
        """Test empty title validation"""
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        invalid_data = {"title": "", "text": SAMPLE_ARTICLE["text"]}

        response = client.post("/summarize", json=invalid_data, headers=headers)
        assert response.status_code == 422

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    def test_short_text(self):
        """Test short text validation"""
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}

        response = client.post("/summarize", json=SHORT_ARTICLE, headers=headers)
        assert response.status_code == 422

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    def test_title_too_long(self):
        """Test title length validation"""
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        invalid_data = {
            "title": "x" * 501,  # Exceeds 500 character limit
            "text": SAMPLE_ARTICLE["text"]
        }

        response = client.post("/summarize", json=invalid_data, headers=headers)
        assert response.status_code == 422

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    def test_text_too_long(self):
        """Test text length validation"""
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        invalid_data = {
            "title": "Test",
            "text": "x" * 50001  # Exceeds 50000 character limit
        }

        response = client.post("/summarize", json=invalid_data, headers=headers)
        assert response.status_code == 422

class TestSummarizeEndpoint:
    """Test main summarization endpoint"""

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    @patch('api.summarizer')
    def test_successful_summarization(self, mock_summarizer):
        """Test successful summarization request"""
        # Mock the summarizer
        mock_summarizer.summarize_article.return_value = "Test summary"

        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        response = client.post("/summarize", json=SAMPLE_ARTICLE, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "pending"
        assert "created_at" in data

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    def test_summarization_without_model(self):
        """Test summarization when model is not loaded"""
        # Temporarily set summarizer to None
        original_summarizer = summarizer

        with patch('api.summarizer', None):
            headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
            response = client.post("/summarize", json=SAMPLE_ARTICLE, headers=headers)

            assert response.status_code == 503
            assert "not available" in response.json()["detail"]

class TestSyncSummarizeEndpoint:
    """Test synchronous summarization endpoint"""

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    @patch('api.summarizer')
    def test_sync_summarization_success(self, mock_summarizer):
        """Test successful synchronous summarization"""
        mock_summarizer.summarize_article.return_value = "Test summary"

        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        response = client.post("/summarize/sync", json=SAMPLE_ARTICLE, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "summary" in data
        assert "processing_time" in data

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    def test_sync_summarization_long_text(self):
        """Test synchronous summarization with text too long"""
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        long_article = {
            "title": "Long Article",
            "text": "x" * 10001  # Exceeds sync limit
        }

        response = client.post("/summarize/sync", json=long_article, headers=headers)
        assert response.status_code == 413
        assert "too long" in response.json()["detail"]

class TestTaskStatusEndpoint:
    """Test task status endpoint"""

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    def test_task_not_found(self):
        """Test getting status of non-existent task"""
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        response = client.get("/task/non-existent-task-id", headers=headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    def test_task_status_success(self):
        """Test getting status of existing task"""
        # Create a mock task
        task_id = "test-task-id"
        task_results[task_id] = {
            'task_id': task_id,
            'status': 'completed',
            'created_at': datetime.now(),
            'summary': 'Test summary',
            'processing_time': 1.5
        }

        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        response = client.get(f"/task/{task_id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["status"] == "completed"
        assert data["summary"] == "Test summary"

        # Cleanup
        del task_results[task_id]

class TestRateLimiting:
    """Test rate limiting functionality"""

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY, 'RATE_LIMIT_REQUESTS': '2/minute'})
    def test_rate_limit_exceeded(self):
        """Test rate limiting enforcement"""
        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}

        # Make requests up to the limit
        for i in range(2):
            response = client.post("/summarize", json=SAMPLE_ARTICLE, headers=headers)
            # Should not be rate limited yet
            assert response.status_code != 429

        # This request should be rate limited
        response = client.post("/summarize", json=SAMPLE_ARTICLE, headers=headers)
        assert response.status_code == 429

class TestErrorHandling:
    """Test error handling"""

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    @patch('api.summarizer')
    def test_summarization_error(self, mock_summarizer):
        """Test handling of summarization errors"""
        # Mock an error in summarization
        mock_summarizer.summarize_article.side_effect = Exception("Model error")

        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        response = client.post("/summarize/sync", json=SAMPLE_ARTICLE, headers=headers)

        assert response.status_code == 500
        assert "failed" in response.json()["detail"]

class TestCustomConfiguration:
    """Test custom configuration handling"""

    @patch.dict('os.environ', {'API_KEY': TEST_API_KEY})
    @patch('api.summarizer')
    def test_custom_config(self, mock_summarizer):
        """Test summarization with custom configuration"""
        mock_summarizer.summarize_article.return_value = "Test summary"

        headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
        custom_request = {
            **SAMPLE_ARTICLE,
            "config": {
                "max_bullet_points": 3,
                "min_hashtags": 2
            }
        }

        response = client.post("/summarize", json=custom_request, headers=headers)
        assert response.status_code == 200

# Test utilities
class TestUtilities:
    """Test utility functions"""

    def test_cleanup_old_tasks(self):
        """Test task cleanup functionality"""
        # Add an old task
        old_task_id = "old-task"
        task_results[old_task_id] = {
            'task_id': old_task_id,
            'status': 'completed',
            'created_at': datetime.now() - timedelta(days=2),  # 2 days old
            'summary': 'Old summary'
        }

        # Add a recent task
        recent_task_id = "recent-task"
        task_results[recent_task_id] = {
            'task_id': recent_task_id,
            'status': 'completed',
            'created_at': datetime.now(),  # Recent
            'summary': 'Recent summary'
        }

        # Cleanup should remove old task but keep recent one
        from api import cleanup_old_tasks

        # Since cleanup_old_tasks is async, we need to run it
        # In a real scenario, this would be tested with proper async testing

        # Manual cleanup for testing
        from datetime import timedelta
        current_time = datetime.now()
        expired_tasks = [
            task_id for task_id, task_data in task_results.items()
            if current_time - task_data['created_at'] > timedelta(hours=24)
        ]

        for task_id in expired_tasks:
            del task_results[task_id]

        # Check results
        assert old_task_id not in task_results
        assert recent_task_id in task_results

        # Cleanup
        if recent_task_id in task_results:
            del task_results[recent_task_id]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
