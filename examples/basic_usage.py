#!/usr/bin/env python3
"""
Basic usage example for News Summarizer.

This script demonstrates the main functionality of the summarizer.
"""

from src.news_summarizer import NewsArticleSummarizer, SummaryConfig, summarize_news_article


def main():
    """Example usage of the News Summarizer."""

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

    print("🚀 News Summarizer - Basic Usage Example")
    print("=" * 50)

    # Method 1: Using the convenience function
    print("\n1. Using convenience function:")
    summary = summarize_news_article(
        sample_article["title"],
        sample_article["text"]
    )
    print(f"Title: {summary['title']}")
    print(f"Paragraph: {summary['paragraph']}")
    print(f"Hashtags: {summary['hashtags']}")

    print("\n" + "=" * 50)

    # Method 2: Using the class directly
    print("\n2. Using NewsArticleSummarizer class:")
    summarizer = NewsArticleSummarizer()
    summary = summarizer.summarize_article(
        sample_article["title"],
        sample_article["text"]
    )
    print(f"Title: {summary['title']}")
    print(f"Paragraph: {summary['paragraph']}")
    print(f"Hashtags: {summary['hashtags']}")

    print("\n" + "=" * 50)

    # Method 3: Using custom configuration
    print("\n3. Using custom configuration:")
    config = SummaryConfig(
        max_bullet_points=3,
        min_hashtags=2,
        max_hashtags=3,
        max_title_words=5
    )

    summarizer = NewsArticleSummarizer(config)
    summary = summarizer.summarize_article(
        sample_article["title"],
        sample_article["text"]
    )
    print(f"Title: {summary['title']}")
    print(f"Paragraph: {summary['paragraph']}")
    print(f"Hashtags: {summary['hashtags']}")

    print("\n" + "=" * 50)
    print("✅ Basic usage example completed!")


if __name__ == "__main__":
    main()
