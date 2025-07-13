"""
Configuration module for News Summarizer.

Contains all configuration classes and constants used throughout the application.
"""

from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class SummaryConfig:
    """Configuration for summary generation."""
    max_chunk_tokens: int = 1000
    min_bullet_points: int = 3
    max_bullet_points: int = 5
    min_hashtags: int = 2
    max_hashtags: int = 4
    max_title_words: int = 7
    model_name: str = "facebook/bart-large-cnn"


# Gen Z Trading Vocabulary and Templates
FINANCIAL_STORY_TYPES = {
    'crypto': {
        'keywords': ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'blockchain', 'defi', 'nft', 'token', 'coin', 'doge', 'ada', 'sol'],
        'positive_slang': ['absolutely sending it', 'going to the moon', 'printing money', 'crushing it', 'ripping higher', 'catching massive bids'],
        'negative_slang': ['getting absolutely rekt', 'dumping hard', 'in complete freefall', 'getting obliterated', 'bleeding out'],
        'neutral_slang': ['trading sideways', 'chopping around', 'consolidating', 'range-bound action']
    },
    'stock_earnings': {
        'keywords': ['earnings', 'eps', 'revenue', 'quarterly', 'q1', 'q2', 'q3', 'q4', 'guidance', 'beat', 'miss'],
        'positive_slang': ['absolutely smashed expectations', 'dropped fire earnings', 'beat by a mile', 'crushed the numbers'],
        'negative_slang': ['missed big time', 'completely whiffed on earnings', 'disappointed the street', 'got wrecked by expectations'],
        'neutral_slang': ['met expectations', 'came in line', 'delivered as expected']
    },
    'stock_movement': {
        'keywords': ['stock', 'share', 'equity', 'nyse', 'nasdaq', 'trading', 'volume', 'price action'],
        'positive_slang': ['absolutely ripping', 'catching serious bids', 'momentum is insane', 'going parabolic'],
        'negative_slang': ['getting absolutely dumped', 'selling pressure is brutal', 'falling off a cliff', 'complete capitulation'],
        'neutral_slang': ['chopping around', 'sideways action', 'range-bound trading']
    },
    'fed_policy': {
        'keywords': ['fed', 'federal reserve', 'interest rate', 'jerome powell', 'fomc', 'monetary policy', 'inflation', 'cpi'],
        'positive_slang': ['dovish pivot sending markets', 'risk-on mode activated', 'growth stocks are mooning'],
        'negative_slang': ['hawkish stance crushing growth', 'risk-off mode engaged', 'bond yields spiking'],
        'neutral_slang': ['status quo maintained', 'as expected decision', 'no surprises here']
    },
    'market_general': {
        'keywords': ['market', 'spy', 'qqq', 'dow', 'nasdaq', 's&p', 'index', 'volatility', 'vix'],
        'positive_slang': ['markets are absolutely ripping', 'green across the board', 'bulls are in complete control'],
        'negative_slang': ['markets getting completely wrecked', 'red everywhere you look', 'bears are feasting'],
        'neutral_slang': ['mixed signals from the market', 'sideways grind continues', 'waiting for direction']
    }
}

GEN_Z_TRADING_VOCABULARY = {
    'emojis': {
        'positive': ['🚀', '📈', '🔥', '💎', '🎯', '💯'],
        'negative': ['📉', '😩', '💸', '⚡', '🔴'],
        'neutral': ['👀', '⏰', '📊', '🧐', '⚖️']
    },
    'transition_phrases': [
        'If you\'ve been watching the charts,',
        'For experienced traders,',
        'Smart money is probably',
        'This setup is giving serious',
        'Options traders who held through',
        'If you\'re DCAing into',
        'Technical analysis nerds will notice'
    ],
    'actionable_conclusions': [
        'Keep an eye on {} for continuation',
        'This might be the setup traders have been waiting for',
        'Volume confirmation could send this even higher',
        'Support/resistance levels are key to watch here',
        'IV is probably going crazy on options right now',
        'Perfect time to reassess your position sizing'
    ]
}
