#!/usr/bin/env python3
"""
Fast news summarization script using optimized configuration.
"""

import json
import time
import sys
from pathlib import Path

from src.news_summarizer import NewsArticleSummarizer, FastSummaryConfig

def main():
    """Run fast summarization on test article."""
    # Load test article
    test_file = Path("examples/examples/test_article.json")

    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Test file not found: {test_file}")
        sys.exit(1)

    title = article_data["title"]
    text = article_data["text"]

    print("🚀 Fast News Summarizer")
    print("=" * 50)
    print(f"Article: {title}")
    print(f"Length: {len(text)} characters, {len(text.split())} words")
    print("=" * 50)

    # Initialize with fast configuration
    print("Initializing fast summarizer...")
    start_time = time.time()
    summarizer = NewsArticleSummarizer(FastSummaryConfig())
    init_time = time.time() - start_time
    print(f"✅ Initialized in {init_time:.2f} seconds")
    print(f"🔧 Fast mode enabled: {summarizer.fast_mode}")

    # Perform summarization
    print("\nProcessing article...")
    start_time = time.time()
    result = summarizer.summarize_article(title, text)
    processing_time = time.time() - start_time

    # Display results
    print("\n" + "=" * 50)
    print("📋 SUMMARY RESULTS")
    print("=" * 50)
    print(f"⏱️  Processing time: {processing_time:.2f} seconds")
    print(f"🎯 Total time: {init_time + processing_time:.2f} seconds")
    print()
    print(f"📰 Title: {result['title']}")
    print(f"😊 Sentiment: {result['sentiment']}")
    print(f"📝 Summary:")
    print(f"   {result['paragraph']}")
    print(f"🏷️  Tags: {result['hashtags']}")

    # Performance feedback
    print("\n" + "=" * 50)
    if processing_time <= 15:
        print("🎉 Excellent! Processing time under 15 seconds!")
    elif processing_time <= 20:
        print("✅ Good! Processing time under 20 seconds!")
    else:
        print("⚠️  Processing time still over 20 seconds")

    print(f"Performance target: ≤20s (current: {processing_time:.1f}s)")
    print("=" * 50)

if __name__ == "__main__":
    main()
