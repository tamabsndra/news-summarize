#!/usr/bin/env python3
"""
API usage example for News Summarizer.

This script demonstrates how to use the API client.
"""

from src.api.client import NewsApiClient


def main():
    """Example usage of the News Summarizer API."""

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
        """
    }

    print("🚀 News Summarizer API - Usage Example")
    print("=" * 50)

    # 1. Health Check
    print("\n1. Checking API health...")
    health = client.health_check()
    print(f"Health status: {health}")

    if health.get("status") != "healthy":
        print("❌ API is not healthy. Make sure the API server is running.")
        return

    print("\n" + "=" * 50)

    # 2. Synchronous Summarization
    print("\n2. Testing synchronous summarization...")
    sync_result = client.summarize_sync(
        title=sample_article["title"],
        text=sample_article["text"]
    )

    if "error" in sync_result:
        print(f"❌ Sync error: {sync_result['error']}")
    else:
        print(f"✅ Sync processing time: {sync_result['processing_time']:.2f} seconds")
        print(f"Summary: {sync_result['summary']}")

    print("\n" + "=" * 50)

    # 3. Asynchronous Summarization
    print("\n3. Testing asynchronous summarization...")
    async_result = client.summarize_async(
        title=sample_article["title"],
        text=sample_article["text"]
    )

    if "error" in async_result:
        print(f"❌ Async error: {async_result['error']}")
        return

    task_id = async_result["task_id"]
    print(f"✅ Task submitted with ID: {task_id}")

    # Wait for completion
    print("⏳ Waiting for task completion...")
    final_result = client.wait_for_completion(task_id)

    if "error" in final_result:
        print(f"❌ Error: {final_result['error']}")
    else:
        print(f"✅ Task completed!")
        print(f"Processing time: {final_result.get('processing_time', 'N/A')} seconds")
        print(f"Final summary: {final_result['summary']}")

    print("\n" + "=" * 50)
    print("✅ API usage example completed!")


if __name__ == "__main__":
    main()
