"""
Utility functions for text processing and data extraction.
"""

import re
import random
from typing import List, Dict, Any
from nltk.tokenize import word_tokenize

from .config import FINANCIAL_STORY_TYPES, GEN_Z_TRADING_VOCABULARY


def clean_text(text: str) -> str:
    """
    Clean and normalize input text.

    Args:
        text: Raw text input

    Returns:
        Cleaned text
    """
    # Remove HTML tags but preserve inner text
    text = re.sub(r'<[^>]+>', '', text)

    # Remove common web artifacts
    text = re.sub(r'\[[^\]]*\]', '', text)  # Brackets like [Photo]
    text = re.sub(r'\([^)]*\)', '', text)  # Parentheses with metadata

    # Remove URLs
    text = re.sub(r'https?://[^\s]+', '', text)

    # Remove image captions and photo credits
    text = re.sub(r'AFP/Getty Images|AP|Reuters|Getty Images', '', text)
    text = re.sub(r'This picture taken on.*?\.', '', text)
    text = re.sub(r'Related article.*?$', '', text, flags=re.MULTILINE)

    # Remove navigation elements and web artifacts
    text = re.sub(r'CNN\s*—\s*', '', text)
    text = re.sub(r'&amp;|&lt;|&gt;|&quot;|&apos;',
                  lambda m: {'&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&apos;': "'"}.get(m.group(), m.group()), text)

    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())

    # Remove empty lines and clean up paragraph breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text


def extract_key_data(text: str) -> Dict[str, Any]:
    """
    Extract key financial data from text.

    Args:
        text: Article text

    Returns:
        Dictionary with extracted financial data
    """
    text_lower = text.lower()

    # Extract prices
    prices = re.findall(r'\$([0-9,]+\.?[0-9]*)', text)

    # Extract percentages
    percentages = re.findall(r'([0-9]+\.?[0-9]*)\s*%', text)

    # Extract companies/stocks
    companies = re.findall(r'\b[A-Z]{2,5}\b', text)  # Stock symbols

    # Extract dates
    dates = re.findall(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}', text_lower)

    # Extract quarters
    quarters = re.findall(r'(q[1-4]|first quarter|second quarter|third quarter|fourth quarter)', text_lower)

    return {
        'prices': prices[:5],  # Limit to first 5
        'percentages': percentages[:5],
        'companies': list(set(companies[:10])),  # Unique companies
        'dates': dates[:3],
        'quarters': quarters[:2]
    }


def analyze_story_context(text: str, summary: str) -> tuple:
    """
    Analyze story context to determine type and sentiment.

    Args:
        text: Article text
        summary: Article summary

    Returns:
        Tuple of (story_type, sentiment, main_subject)
    """
    combined_text = f"{text} {summary}".lower()

    # Determine story type
    story_type = 'market_general'  # Default
    max_matches = 0

    for story_key, story_data in FINANCIAL_STORY_TYPES.items():
        matches = sum(1 for keyword in story_data['keywords'] if keyword in combined_text)
        if matches > max_matches:
            max_matches = matches
            story_type = story_key

    # Determine sentiment
    sentiment = 'neutral'  # Default

    # Count positive/negative indicators
    positive_words = ['gain', 'rise', 'up', 'increase', 'growth', 'bull', 'strong', 'beat', 'profit']
    negative_words = ['loss', 'fall', 'down', 'decrease', 'decline', 'bear', 'weak', 'miss', 'deficit']

    pos_count = sum(1 for word in positive_words if word in combined_text)
    neg_count = sum(1 for word in negative_words if word in combined_text)

    if pos_count > neg_count + 1:
        sentiment = 'positive'
    elif neg_count > pos_count + 1:
        sentiment = 'negative'

    # Extract main subject
    main_subject = extract_main_subject(text)

    return story_type, sentiment, main_subject


def extract_main_subject(text: str) -> str:
    """
    Extract the main subject from text.

    Args:
        text: Article text

    Returns:
        Main subject string
    """
    # Extract potential company names and stock symbols
    companies = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    stocks = re.findall(r'\b[A-Z]{2,5}\b', text)

    # Common financial terms
    financial_terms = re.findall(r'\b(bitcoin|ethereum|tesla|apple|microsoft|amazon|meta|google|nvidia|amd)\b', text, re.IGNORECASE)

    if financial_terms:
        return financial_terms[0].title()
    elif stocks:
        return stocks[0]
    elif companies:
        return companies[0]
    else:
        return "Market"


def generate_hashtags(text: str, min_count: int = 2, max_count: int = 4) -> List[str]:
    """
    Generate hashtags from text.

    Args:
        text: Article text
        min_count: Minimum number of hashtags
        max_count: Maximum number of hashtags

    Returns:
        List of hashtags
    """
    # Extract potential hashtag words
    words = word_tokenize(text.lower())

    # Financial/trading keywords
    financial_keywords = ['bitcoin', 'crypto', 'stock', 'trading', 'market', 'investment', 'finance', 'earnings', 'tech', 'ai', 'startup']

    # Extract relevant words
    relevant_words = [word for word in words if word in financial_keywords]

    # Add some generic hashtags
    base_hashtags = ['#News', '#Finance', '#Trading', '#Market', '#Investment']

    # Create hashtags from relevant words
    hashtags = [f"#{word.title()}" for word in relevant_words[:3]]

    # Add base hashtags if needed
    hashtags.extend(base_hashtags)

    # Remove duplicates and limit count
    hashtags = list(set(hashtags))
    hashtags = hashtags[:max_count]

    # Ensure minimum count
    while len(hashtags) < min_count:
        hashtags.append(random.choice(base_hashtags))

    return hashtags


def generate_short_title(text: str, max_words: int = 7) -> str:
    """
    Generate a short, meaningful title from text using intelligent word scoring.

    Args:
        text: Article text or summary
        max_words: Maximum number of words

    Returns:
        Short title with most important words
    """
    if not text or not text.strip():
        return "News Update"

    # Clean text and tokenize
    clean_text_input = re.sub(r'[^\w\s]', ' ', text.lower())
    words = clean_text_input.split()

    if len(words) <= max_words:
        return ' '.join(text.split()[:max_words])

    # Define filler words to filter out
    filler_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
        'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'there',
        'here', 'where', 'when', 'how', 'why', 'what', 'which', 'who', 'whom', 'whose',
        'very', 'much', 'many', 'most', 'more', 'some', 'any', 'all', 'each', 'every',
        'as', 'so', 'too', 'also', 'just', 'only', 'even', 'still', 'yet', 'already',
        'than', 'then', 'now', 'today', 'yesterday', 'tomorrow', 'said', 'says', 'about'
    }

    # Score words based on importance
    word_scores = {}
    original_words = text.split()

    for i, word in enumerate(original_words):
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if clean_word and clean_word not in filler_words:
            score = 0

            # Position scoring (earlier words get higher scores)
            if i < 5:
                score += 3
            elif i < 10:
                score += 2
            elif i < 15:
                score += 1

            # Capitalization scoring
            if word[0].isupper():
                score += 2

            # Action word scoring
            action_words = {'announces', 'reports', 'reveals', 'shows', 'says', 'confirms',
                          'launches', 'releases', 'drops', 'rises', 'falls', 'increases',
                          'decreases', 'beats', 'misses', 'surges', 'crashes', 'breaks',
                          'hits', 'reaches', 'crosses', 'gains', 'loses', 'jumps', 'plunges'}

            if clean_word in action_words:
                score += 2

            # Financial terms scoring
            financial_terms = {'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'stock', 'market',
                             'trading', 'price', 'earnings', 'revenue', 'profit', 'loss', 'fed',
                             'interest', 'rate', 'inflation', 'gdp', 'unemployment', 'dollar',
                             'euro', 'currency', 'bond', 'yield', 'nasdaq', 'sp500', 'dow'}

            if clean_word in financial_terms:
                score += 3

            # Company/proper noun scoring
            if word[0].isupper() and len(word) > 1:
                score += 1

            word_scores[i] = score

    # Select top words while preserving order
    sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
    selected_indices = sorted([idx for idx, score in sorted_words[:max_words]])

    # Build title from selected words in original order
    title_words = [original_words[i] for i in selected_indices if i < len(original_words)]

    if not title_words:
        return ' '.join(original_words[:max_words])

    title = ' '.join(title_words)

    # Clean up title
    title = re.sub(r'^\W+', '', title)  # Remove leading non-word characters
    title = title.strip()

    if not title:
        return "News Update"

    return title
