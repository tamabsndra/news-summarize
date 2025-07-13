"""
Main CLI application for News Summarizer.
"""

import argparse
import json
import sys
from typing import Optional

from news_summarizer import NewsArticleSummarizer, SummaryConfig


def create_cli_app() -> argparse.ArgumentParser:
    """Create the CLI application with argument parsing."""
    parser = argparse.ArgumentParser(
        description="News Summarizer CLI - Generate Gen Z/Millennial-focused summaries"
    )

    parser.add_argument(
        "title",
        help="Article title"
    )

    parser.add_argument(
        "text",
        help="Article text content (or - to read from stdin)"
    )

    parser.add_argument(
        "--config",
        help="Path to JSON configuration file",
        type=str
    )

    parser.add_argument(
        "--output",
        help="Output file (default: stdout)",
        type=str
    )

    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "--max-bullet-points",
        type=int,
        default=5,
        help="Maximum number of bullet points"
    )

    parser.add_argument(
        "--max-hashtags",
        type=int,
        default=4,
        help="Maximum number of hashtags"
    )

    parser.add_argument(
        "--max-title-words",
        type=int,
        default=7,
        help="Maximum words in title"
    )

    return parser


def load_config(config_path: str) -> Optional[SummaryConfig]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        return SummaryConfig(**config_data)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return None


def format_output(summary: dict, format_type: str) -> str:
    """Format the summary output."""
    if format_type == "json":
        return json.dumps(summary, indent=2)
    else:
        # Text format
        return f"Title: {summary['title']}\n\nParagraph:\n{summary['paragraph']}\n\nHashtags: {summary['hashtags']}"


def main():
    """Main CLI entry point."""
    parser = create_cli_app()
    args = parser.parse_args()

    # Read text input
    if args.text == "-":
        text = sys.stdin.read()
    else:
        text = args.text

    # Load configuration
    config = None
    if args.config:
        config = load_config(args.config)
        if config is None:
            sys.exit(1)
    else:
        # Use CLI arguments to create config
        config = SummaryConfig(
            max_bullet_points=args.max_bullet_points,
            max_hashtags=args.max_hashtags,
            max_title_words=args.max_title_words
        )

    try:
        # Initialize summarizer
        summarizer = NewsArticleSummarizer(config)

        # Generate summary
        summary = summarizer.summarize_article(args.title, text)

        # Format output
        formatted_output = format_output(summary, args.format)

        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(formatted_output)
        else:
            print(formatted_output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
