#!/usr/bin/env python3
"""
Example usage of the News Summarizer API

This script demonstrates how to use the API from another application.
"""

import requests
import time
import json
import os
from typing import Dict, Any, Optional

class NewsApiClient:
    """Client for interacting with the News Summarizer API"""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        """
        Initialize the API client

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
        """Check API health status"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def summarize_async(self, title: str, text: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Submit article for asynchronous summarization

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
        Submit article for synchronous summarization

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
        Get the status of a summarization task

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
        Wait for a task to complete

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

def main():
    """Example usage of the News Summarizer API"""

    # Initialize the client
    client = NewsApiClient()

    # Sample article for testing
    sample_article = {
        "title": "Major Technology Breakthrough Changes Industry",
        "text": """
        A groundbreaking technological innovation has emerged that promises to revolutionize
        the entire industry landscape. The breakthrough, announced by leading researchers at
        major tech companies, represents years of collaborative effort and substantial
        investment in cutting-edge development.

        The new technology addresses long-standing challenges that have plagued the industry
        for decades. Early testing phases have shown remarkable results, with efficiency
        improvements of up to 300% compared to current industry standards. This advancement
        is expected to reduce costs significantly while improving overall performance.

        Industry experts are calling this development a game-changer that will reshape
        competitive dynamics across multiple sectors. The innovation incorporates advanced
        machine learning algorithms and novel engineering approaches that were previously
        thought impossible to implement at scale.

        Major corporations have already begun investing heavily in this technology, with
        some analysts predicting it will become the new industry standard within the next
        five years. The economic implications are substantial, with potential market
        disruption affecting millions of jobs and creating new opportunities for skilled
        workers.

        The development team behind this breakthrough has announced plans for wider
        implementation and is working with regulatory bodies to ensure safe deployment.
        Initial pilot programs are expected to begin next quarter, with full commercial
        rollout planned for the following year.
        """
    }

    print("=== News Summarizer API Example ===\n")

    # 1. Health Check
    print("1. Checking API health...")
    health = client.health_check()
    print(f"Health status: {health}")

    if health.get("status") != "healthy":
        print("API is not healthy. Exiting.")
        return

    print("\n" + "="*50 + "\n")

    # 2. Synchronous Summarization (for shorter articles)
    print("2. Testing synchronous summarization...")
    sync_result = client.summarize_sync(
        title=sample_article["title"],
        text=sample_article["text"][:5000]  # Truncate for sync processing
    )

    if "error" in sync_result:
        print(f"Sync error: {sync_result['error']}")
    else:
        print(f"Sync processing time: {sync_result['processing_time']:.2f} seconds")
        print(f"Sync summary:\n{sync_result['summary']}")

    print("\n" + "="*50 + "\n")

    # 3. Asynchronous Summarization (recommended for longer articles)
    print("3. Testing asynchronous summarization...")
    async_result = client.summarize_async(
        title=sample_article["title"],
        text=sample_article["text"]
    )

    if "error" in async_result:
        print(f"Async error: {async_result['error']}")
        return

    task_id = async_result["task_id"]
    print(f"Task submitted with ID: {task_id}")

    # Wait for completion
    print("Waiting for task completion...")
    final_result = client.wait_for_completion(task_id)

    if "error" in final_result:
        print(f"Error: {final_result['error']}")
    else:
        print(f"Task completed!")
        print(f"Processing time: {final_result.get('processing_time', 'N/A')} seconds")
        print(f"Final summary:\n{final_result['summary']}")

    print("\n" + "="*50 + "\n")

    # 4. Custom Configuration Example
    print("4. Testing with custom configuration...")
    custom_config = {
        "max_bullet_points": 3,
        "min_hashtags": 2,
        "max_hashtags": 3
    }

    custom_result = client.summarize_sync(
        title=sample_article["title"],
        text=sample_article["text"][:5000],
        config=custom_config
    )

    if "error" in custom_result:
        print(f"Custom config error: {custom_result['error']}")
    else:
        print(f"Custom config summary:\n{custom_result['summary']}")

    print("\n" + "="*50 + "\n")

    # 5. Error Handling Example
    print("5. Testing error handling...")
    error_result = client.summarize_sync(
        title="",  # Empty title should cause validation error
        text="Short text"  # Too short should cause validation error
    )

    print(f"Expected error result: {error_result}")

    print("\nExample completed!")

def batch_processing_example():
    """Example of processing multiple articles in batch"""

    client = NewsApiClient()

    # Sample articles
    articles = [
        {
            "title": "Climate Change Summit Reaches Historic Agreement",
            "text": "World leaders gathered at the annual climate summit have reached a historic agreement on carbon emission reductions. The agreement, which took three days of intensive negotiations, commits all participating nations to ambitious targets for reducing greenhouse gas emissions by 2030. The deal represents a significant breakthrough in international climate policy and is expected to accelerate the transition to renewable energy sources worldwide."
        },
        {
            "title": "New Medical Treatment Shows Promise in Clinical Trials",
            "text": "A revolutionary new medical treatment has shown remarkable results in Phase III clinical trials, offering hope for patients with a previously incurable condition. The treatment, developed over a decade of research, has demonstrated a 85% success rate in treating the condition with minimal side effects. Medical experts are calling it a potential game-changer that could benefit millions of patients globally."
        },
        {
            "title": "Space Mission Discovers Potentially Habitable Planet",
            "text": "Scientists have announced the discovery of a potentially habitable exoplanet located 22 light-years from Earth. The planet, designated as K2-18b, shows signs of water vapor in its atmosphere and exists within the habitable zone of its star. This discovery represents a significant milestone in the search for life beyond our solar system and has implications for future space exploration missions."
        }
    ]

    print("=== Batch Processing Example ===\n")

    # Submit all articles for async processing
    tasks = []
    for i, article in enumerate(articles):
        print(f"Submitting article {i+1}: {article['title']}")
        result = client.summarize_async(article["title"], article["text"])

        if "error" in result:
            print(f"Error submitting article {i+1}: {result['error']}")
        else:
            tasks.append({
                "task_id": result["task_id"],
                "article_title": article["title"],
                "submitted_at": result["created_at"]
            })

    print(f"\nSubmitted {len(tasks)} tasks for processing")

    # Wait for all tasks to complete
    completed_tasks = []
    for task in tasks:
        print(f"Waiting for: {task['article_title']}")
        result = client.wait_for_completion(task["task_id"])

        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            completed_tasks.append({
                "title": task["article_title"],
                "summary": result["summary"],
                "processing_time": result.get("processing_time", 0)
            })

    # Display results
    print(f"\n=== Results ({len(completed_tasks)} completed) ===")
    for i, task in enumerate(completed_tasks):
        print(f"\n{i+1}. {task['title']}")
        print(f"Processing time: {task['processing_time']:.2f}s")
        print(f"Summary:\n{task['summary']}")
        print("-" * 50)

if __name__ == "__main__":
    # Run the main example
    main()

    # Uncomment to run batch processing example
    # print("\n" + "="*70 + "\n")
    # batch_processing_example()
