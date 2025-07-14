#!/usr/bin/env python3
"""
Performance benchmark script for news summarizer optimizations.
"""

import json
import time
import logging
from pathlib import Path

from src.news_summarizer import NewsArticleSummarizer, SummaryConfig, FastSummaryConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_test_article():
    """Load the test article from examples."""
    test_file = Path("examples/examples/test_article.json")
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Test file not found: {test_file}")
        return None

def benchmark_configuration(config, config_name):
    """Benchmark a specific configuration."""
    logger.info(f"\n{'='*50}")
    logger.info(f"Testing configuration: {config_name}")
    logger.info(f"{'='*50}")

    # Load test article
    article_data = load_test_article()
    if not article_data:
        return None

    title = article_data["title"]
    text = article_data["text"]

    logger.info(f"Article length: {len(text)} characters")
    logger.info(f"Article words: {len(text.split())} words")

    # Initialize summarizer
    start_time = time.time()
    summarizer = NewsArticleSummarizer(config)
    init_time = time.time() - start_time
    logger.info(f"Initialization time: {init_time:.2f} seconds")

    # Perform summarization
    start_time = time.time()
    try:
        result = summarizer.summarize_article(title, text)
        processing_time = time.time() - start_time

        logger.info(f"Processing time: {processing_time:.2f} seconds")
        logger.info(f"Generated title: {result['title']}")
        logger.info(f"Generated hashtags: {result['hashtags']}")
        logger.info(f"Paragraph length: {len(result['paragraph'])} characters")

        return {
            "config_name": config_name,
            "init_time": init_time,
            "processing_time": processing_time,
            "total_time": init_time + processing_time,
            "result": result
        }

    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        return None

def main():
    """Run performance benchmarks."""
    logger.info("Starting News Summarizer Performance Benchmark")
    logger.info("="*60)

    # Test configurations
    configs = [
        (SummaryConfig(), "Standard Configuration"),
        (FastSummaryConfig(), "Fast Configuration (Optimized)")
    ]

    results = []

    for config, name in configs:
        result = benchmark_configuration(config, name)
        if result:
            results.append(result)

    # Compare results
    if len(results) >= 2:
        logger.info(f"\n{'='*50}")
        logger.info("PERFORMANCE COMPARISON")
        logger.info(f"{'='*50}")

        standard_time = results[0]["processing_time"]
        fast_time = results[1]["processing_time"]
        improvement = ((standard_time - fast_time) / standard_time) * 100
        speedup = standard_time / fast_time

        logger.info(f"Standard config processing time: {standard_time:.2f} seconds")
        logger.info(f"Fast config processing time: {fast_time:.2f} seconds")
        logger.info(f"Performance improvement: {improvement:.1f}%")
        logger.info(f"Speedup factor: {speedup:.2f}x")

        if fast_time <= 20:
            logger.info("✅ Target of ≤20 seconds achieved!")
        else:
            logger.warning("⚠️  Target of ≤20 seconds not yet achieved")

        if fast_time <= 15:
            logger.info("🎯 Preferred target of ≤15 seconds achieved!")

    logger.info(f"\n{'='*50}")
    logger.info("Benchmark completed!")
    logger.info(f"{'='*50}")

if __name__ == "__main__":
    main()
