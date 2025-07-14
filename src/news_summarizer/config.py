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
    min_hashtags: int = 3
    max_hashtags: int = 5
    max_title_words: int = 10
    model_name: str = "human-centered-summarization/financial-summarization-pegasus"
    sentiment_model_name: str = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"


@dataclass
class FastSummaryConfig(SummaryConfig):
    """Performance-optimized configuration for faster summarization."""
    max_chunk_tokens: int = 800   # Smaller chunks for faster processing
    min_bullet_points: int = 2    # Fewer bullet points
    max_bullet_points: int = 3
    min_hashtags: int = 2         # Fewer hashtags for faster generation
    max_hashtags: int = 3
    max_title_words: int = 6      # Shorter titles


# Gen Z Trading Vocabulary and Templates
FINANCIAL_STORY_TYPES = {
    'crypto': {
        'keywords': ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'blockchain', 'defi', 'nft', 'token', 'coin', 'doge', 'ada', 'sol', 'l2', 'airdrops'],
        'positive_slang': [
            'absolutely sending it',
            'going to the moon',
            'printing money',
            'crushing it',
            'ripping higher',
            'catching massive bids',
            'vibes are immaculate',
            'the bulls woke up fr',
            'full degen mode activated'
        ],
        'negative_slang': [
            'getting absolutely rekt',
            'dumping hard',
            'in complete freefall',
            'getting obliterated',
            'bleeding out',
            'rug vibes detected',
            'zero incoming?',
            'hodlers crying in the club rn'
        ],
        'neutral_slang': [
            'trading sideways',
            'chopping around',
            'consolidating',
            'range-bound action',
            'cooling off after that pump',
            'waiting for confirmation'
        ]
    },
    'stock_earnings': {
        'keywords': ['earnings', 'eps', 'revenue', 'quarterly', 'q1', 'q2', 'q3', 'q4', 'guidance', 'beat', 'miss', 'forward outlook'],
        'positive_slang': [
            'absolutely smashed expectations',
            'dropped fire earnings',
            'beat by a mile',
            'crushed the numbers',
            'Wall Street eating this up',
            'numbers came in 🔥',
            'straight W on the report'
        ],
        'negative_slang': [
            'missed big time',
            'completely whiffed on earnings',
            'disappointed the street',
            'got wrecked by expectations',
            'guidance in the gutter',
            'massive L on the earnings call'
        ],
        'neutral_slang': [
            'met expectations',
            'came in line',
            'delivered as expected',
            'steady but not spicy',
            'numbers were mid'
        ]
    },
    'stock_movement': {
        'keywords': ['stock', 'share', 'equity', 'nyse', 'nasdaq', 'trading', 'volume', 'price action', 'pre-market', 'after-hours'],
        'positive_slang': [
            'absolutely ripping',
            'catching serious bids',
            'momentum is insane',
            'going parabolic',
            'chart looking like stairs to heaven',
            'every dip getting bought',
            'bulls got laser eyes rn'
        ],
        'negative_slang': [
            'getting absolutely dumped',
            'selling pressure is brutal',
            'falling off a cliff',
            'complete capitulation',
            'buy the dip? more like dip the dip',
            'bears out for blood today'
        ],
        'neutral_slang': [
            'chopping around',
            'sideways action',
            'range-bound trading',
            'no conviction either way',
            'waiting for catalyst'
        ]
    },
    'fed_policy': {
        'keywords': ['fed', 'federal reserve', 'interest rate', 'jerome powell', 'fomc', 'monetary policy', 'inflation', 'cpi', 'core pce'],
        'positive_slang': [
            'dovish pivot sending markets',
            'risk-on mode activated',
            'growth stocks are mooning',
            'Powell just said send it',
            'liquidity taps turned back on'
        ],
        'negative_slang': [
            'hawkish stance crushing growth',
            'risk-off mode engaged',
            'bond yields spiking',
            'rate hikes still haunting us',
            'Powell dropped the hammer'
        ],
        'neutral_slang': [
            'status quo maintained',
            'as expected decision',
            'no surprises here',
            'market already priced this in',
            'FOMC day drama as usual'
        ]
    },
    'market_general': {
        'keywords': ['market', 'spy', 'qqq', 'dow', 'nasdaq', 's&p', 'index', 'volatility', 'vix', 'macro'],
        'positive_slang': [
            'markets are absolutely ripping',
            'green across the board',
            'bulls are in complete control',
            'risk appetite is back',
            'bears left the chat'
        ],
        'negative_slang': [
            'markets getting completely wrecked',
            'red everywhere you look',
            'bears are feasting',
            'volatility spiking hard',
            'everything just nuked'
        ],
        'neutral_slang': [
            'mixed signals from the market',
            'sideways grind continues',
            'waiting for direction',
            'nothing burger kind of day',
            'choppy waters ahead'
        ]
    }
}

GEN_Z_TRADING_VOCABULARY = {
    'emojis': {
        'positive': ['🚀', '📈', '🔥', '💎', '🎯', '💯', '📀', '🤑', '🧠', '✅'],
        'negative': ['📉', '😩', '💸', '⚡', '🔴', '☠️', '😭', '🕳️', '😵‍💫'],
        'neutral': ['👀', '⏰', '📊', '🧐', '⚖️', '🤔', '🤷', '📆', '🔍']
    },
    'transition_phrases': [
        'If you\'ve been watching the charts,',
        'For experienced traders,',
        'Smart money is probably',
        'This setup is giving serious',
        'Options traders who held through',
        'If you\'re DCAing into',
        'Technical analysis nerds will notice',
        'So here\'s the deal,',
        'The market\'s been wild lately, and',
        'As expected after the CPI news,',
        'Not financial advice, but',
        'After that breakout yesterday,',
        'Bulls might wanna pay attention here,',
        'When liquidity dries up like this,',
        'Based on the 4H candle,'
    ],
    'actionable_conclusions': [
        'Keep an eye on {} for continuation',
        'This might be the setup traders have been waiting for',
        'Volume confirmation could send this even higher',
        'Support/resistance levels are key to watch here',
        'IV is probably going crazy on options right now',
        'Perfect time to reassess your position sizing',
        'Might be a good time to scale in slowly',
        'Breakout confirmed, could retest before mooning 🌕',
        'Tighten those stop losses if you\'re still in {}',
        'Could be a classic fakeout — stay sharp ⚔️',
        'Momentum is dying, don\'t get trapped',
        'Solid RR ratio if you\'re playing the bounce',
        'Sellers getting exhausted, but volume\'s sus 🤨',
        'This chop is wrecking leverage plays left and right',
        'Might be time to hedge or go flat if unsure'
    ]
}
