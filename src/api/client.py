"""
API client for interacting with the News Summarizer API.
"""

import requests
import time
import os
from typing import Dict, Any, Optional


class NewsApiClient:
    """Client for interacting with the News Summarizer API."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the API
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv("API_KEY", "your-secure-api-key-here")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def summarize_async(self, title: str, text: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Submit article for asynchronous summarization.

        Args:
            title: Article title
            text: Article text content
            config: Optional configuration parameters

        Returns:
            Dictionary containing task_id and status
        """
        payload = {
            "title": title,
            "text": text
        }

        if config:
            payload["config"] = config

        try:
            response = requests.post(
                f"{self.base_url}/summarize",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def summarize_sync(self, title: str, text: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Submit article for synchronous summarization.

        Args:
            title: Article title
            text: Article text content (max 10,000 characters)
            config: Optional configuration parameters

        Returns:
            Dictionary containing summary and processing time
        """
        payload = {
            "title": title,
            "text": text
        }

        if config:
            payload["config"] = config

        try:
            response = requests.post(
                f"{self.base_url}/summarize/sync",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a summarization task.

        Args:
            task_id: Task ID returned from summarize_async

        Returns:
            Dictionary containing task status and results
        """
        try:
            response = requests.get(
                f"{self.base_url}/task/{task_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def wait_for_completion(self, task_id: str, timeout: int = 300, poll_interval: int = 5) -> Dict[str, Any]:
        """
        Wait for a task to complete.

        Args:
            task_id: Task ID to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds

        Returns:
            Final task status
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.get_task_status(task_id)

            if "error" in result:
                return result

            status = result.get("status")
            if status in ["completed", "failed"]:
                return result

            print(f"Task {task_id} status: {status}")
            time.sleep(poll_interval)

        return {"error": "Timeout waiting for task completion"}
