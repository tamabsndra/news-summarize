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
    positive_words = ['gain', 'rise', 'up', 'increase', 'growth', 'bull', 'strong', 'beat', 'profit', 'bullish', 'buy', 'buy the dip', 'buy the rumor', 'buy the news', 'buy the hype', 'buy the pump', 'buy the rally', 'buy the breakout', 'buy the momentum', 'buy the trend', 'buy the support', 'buy the resistance', 'buy the breakout', 'buy the momentum', 'buy the trend', 'buy the support', 'buy the resistance']
    negative_words = ['loss', 'fall', 'down', 'decrease', 'decline', 'bear', 'weak', 'miss', 'deficit', 'bearish', 'sell', 'sell the rumor', 'sell the news', 'sell the hype', 'sell the pump', 'sell the rally', 'sell the breakout', 'sell the momentum', 'sell the trend', 'sell the support', 'sell the resistance', 'sell the breakout', 'sell the momentum', 'sell the trend', 'sell the support', 'sell the resistance']

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
    financial_terms = re.findall(r'\b(bitcoin|ethereum|tesla|apple|microsoft|amazon|meta|google|nvidia|amd|btc|eth|crypto|stock|market|trading|price|earnings|revenue|profit|loss|fed|interest|rate|inflation|gdp|unemployment|dollar|euro|currency|bond|yield|nasdaq|sp500|dow)\b', text, re.IGNORECASE)

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
    financial_keywords = ['bitcoin', 'crypto', 'stock', 'trading', 'market', 'investment', 'finance', 'earnings', 'tech', 'ai', 'startup', 'ethereum', 'btc', 'eth', 'crypto', 'stock', 'market', 'trading', 'price', 'earnings', 'revenue', 'profit', 'loss', 'fed', 'interest', 'rate', 'inflation', 'gdp', 'unemployment', 'dollar', 'euro', 'currency', 'bond', 'yield', 'nasdaq', 'sp500', 'dow']

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

def generate_short_title(text: str, max_words: int = 10) -> str:
    """
    Generate a short, meaningful title from text using intelligent word scoring.
    """
    if not text or not text.strip():
        return "News Update"

    original_words = text.split()
    clean_words = [re.sub(r'[^\w]', '', word.lower()) for word in original_words]

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

    action_words_scoring = {
        'announces': 0.5, 'reports': 0.3, 'reveals': 0.4, 'shows': 0.2, 'confirms': 0.5,
        'launches': 0.8, 'releases': 0.6, 'beats': 1.0, 'surges': 1.0, 'rises': 0.9,
        'gains': 0.8, 'jumps': 1.0, 'improves': 0.7, 'accelerates': 0.9,
        'outperforms': 1.0, 'soars': 1.0, 'climbs': 0.9, 'expands': 0.6,
        'misses': -1.0, 'falls': -0.9, 'plunges': -1.0, 'crashes': -1.0, 'decreases': -0.6,
        'loses': -0.8, 'declines': -0.7, 'drops': -0.6, 'slows': -0.5, 'cuts': -0.7,
        'warns': -0.9, 'halts': -1.0, 'underperforms': -1.0, 'downgrades': -1.0,
        'says': 0.0, 'breaks': 0.2, 'hits': 0.3, 'reaches': 0.4, 'crosses': 0.3,
        'meets': 0.1, 'expects': 0.1, 'files': 0.0, 'updates': 0.1, 'adds': 0.2,
        'sets': 0.2, 'resumes': 0.3
    }

    financial_terms = {
        'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'stock', 'market',
        'trading', 'price', 'earnings', 'revenue', 'profit', 'loss', 'fed',
        'interest', 'rate', 'inflation', 'gdp', 'unemployment', 'dollar',
        'euro', 'currency', 'bond', 'yield', 'nasdaq', 'sp500', 'dow'
    }

    word_scores = {}
    for i, (original, clean) in enumerate(zip(original_words, clean_words)):
        if not clean or clean in filler_words:
            continue

        score = 0

        # Position bias
        if i < 5: score += 3
        elif i < 10: score += 2
        elif i < 15: score += 1

        # Capitalization bias
        if original[0].isupper():
            score += 2

        # Action words
        score += action_words_scoring.get(clean, 0)

        # Financial terms
        if clean in financial_terms:
            score += 3

        # Proper noun / brand name boost
        if original[0].isupper() and len(original) > 1:
            score += 1

        word_scores[i] = score

    if not word_scores:
        return ' '.join(original_words[:max_words])

    # Sort by score (desc), then position (asc)
    top_indices = sorted(word_scores.items(), key=lambda x: (-x[1], x[0]))
    selected = sorted([idx for idx, _ in top_indices[:max_words]])
    title_words = [original_words[i] for i in selected]

    # Final formatting
    title = ' '.join(title_words).strip()
    title = re.sub(r'\s+', ' ', title)

    return title or "News Update"
