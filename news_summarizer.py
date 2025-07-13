#!/usr/bin/env python3
"""
News Summarization Tool for Gen Z/Millennial Audiences

This script takes scraped news articles and converts them into engaging,
casual summaries with a specific format including bullet points, hashtags,
and journalistic paragraphs.
"""

import re
import logging
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from transformers import pipeline, AutoTokenizer
import torch

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gen Z Trader Vocabulary and Templates
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

@dataclass
class SummaryConfig:
    """Configuration for summary generation"""
    max_chunk_tokens: int = 1000
    min_bullet_points: int = 3
    max_bullet_points: int = 5
    min_hashtags: int = 2
    max_hashtags: int = 4
    max_title_words: int = 7  # Reduced from 50 to create truly short titles
    model_name: str = "facebook/bart-large-cnn"

class NewsArticleSummarizer:
    """
    A class to summarize news articles for younger audiences with specific formatting.
    """

    def __init__(self, config: Optional[SummaryConfig] = None):
        """
        Initialize the summarizer with configuration and load the model.

        Args:
            config: Configuration object for summarization parameters
        """
        self.config = config or SummaryConfig()
        self.device = 0 if torch.cuda.is_available() else -1

        logger.info(f"Loading model: {self.config.model_name}")
        self.summarizer = pipeline(
            "summarization",
            model=self.config.model_name,
            device=self.device,
            return_tensors=False
        )

        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        logger.info("Model loaded successfully")

    def _clean_text(self, text: str) -> str:
        """Clean and normalize input text"""
        import re

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
        text = re.sub(r'&amp;|&lt;|&gt;|&quot;|&apos;', lambda m: {'&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&apos;': "'"}.get(m.group(), m.group()), text)

        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove empty lines and clean up paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)

        return text

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks that fit within token limits.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            token_count = len(self.tokenizer.encode(test_chunk))

            if token_count <= self.config.max_chunk_tokens:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _generate_base_summary(self, text: str) -> str:
        """Generate a base summary from the input text"""
        chunks = self._chunk_text(text)

        if not chunks:
            return ""

        # If single chunk, summarize directly
        if len(chunks) == 1:
            try:
                result = self.summarizer(
                    chunks[0],
                    max_length=200,
                    min_length=50,
                    do_sample=False
                )
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and 'summary_text' in result[0]:
                        return result[0]['summary_text']
                    elif isinstance(result[0], str):
                        return result[0]
                return str(result)
            except Exception as e:
                logger.error(f"Error summarizing single chunk: {e}")
                return chunks[0][:500]  # Fallback to truncation

        # For multiple chunks, summarize each then combine
        chunk_summaries = []
        for chunk in chunks:
            try:
                result = self.summarizer(
                    chunk,
                    max_length=100,
                    min_length=20,
                    do_sample=False
                )
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and 'summary_text' in result[0]:
                        chunk_summaries.append(result[0]['summary_text'])
                    elif isinstance(result[0], str):
                        chunk_summaries.append(result[0])
                    else:
                        chunk_summaries.append(str(result[0]))
                else:
                    chunk_summaries.append(chunk[:200])  # Fallback
            except Exception as e:
                logger.error(f"Error summarizing chunk: {e}")
                chunk_summaries.append(chunk[:200])  # Fallback

        # Combine and re-summarize
        combined = " ".join(chunk_summaries)
        if len(self.tokenizer.encode(combined)) <= self.config.max_chunk_tokens:
            try:
                result = self.summarizer(
                    combined,
                    max_length=250,
                    min_length=100,
                    do_sample=False
                )
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and 'summary_text' in result[0]:
                        return result[0]['summary_text']
                    elif isinstance(result[0], str):
                        return result[0]
                return str(result)
            except Exception as e:
                logger.error(f"Error in final summarization: {e}")
                return combined

        return combined

    def _generate_hashtags(self, text: str) -> List[str]:
        """Generate relevant hashtags from the text"""
        # Extract key terms
        words = word_tokenize(text.lower())

        # Filter for important words
        important_words = []
        for word in words:
            if (len(word) > 3 and
                word.isalpha() and
                word not in ['this', 'that', 'with', 'have', 'will', 'been', 'were', 'said', 'they', 'their', 'them', 'than', 'from', 'more', 'also', 'like', 'just', 'only', 'even', 'much', 'many', 'some', 'very', 'well', 'make', 'made', 'time', 'year', 'years', 'news', 'article']):
                important_words.append(word)

        # Count word frequency
        word_freq = {}
        for word in important_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get top words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # Create hashtags
        hashtags = []
        for word, freq in top_words:
            if len(hashtags) >= self.config.max_hashtags:
                break
            hashtag = f"#{word.capitalize()}"
            hashtags.append(hashtag)

        # Add some common news hashtags if we need more
        common_hashtags = ['#BreakingNews', '#News', '#Update', '#Latest']
        while len(hashtags) < self.config.min_hashtags and common_hashtags:
            hashtags.append(common_hashtags.pop(0))

        return hashtags[:self.config.max_hashtags]

    def _generate_short_title(self, text: str) -> str:
        """Generate a short, catchy title by intelligently selecting key words"""
        # Extract first sentence or key phrase
        sentences = sent_tokenize(text)
        first_sentence = sentences[0] if sentences else text

        # Split into words and clean
        words = first_sentence.split()

        # Remove common filler words but keep important ones
        filler_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                       'of', 'with', 'by', 'from', 'amid', 'during', 'through', 'against'}

        # Keep track of important words with scores
        word_scores = []
        for i, word in enumerate(words):
            word_lower = word.lower()
            score = 0

            # Higher score for words at the beginning (title position)
            if i < 3:
                score += 3
            elif i < 5:
                score += 2
            else:
                score += 1

            # Higher score for capitalized words (proper nouns, brands)
            if word[0].isupper() and len(word) > 1:
                score += 3

            # Higher score for numbers and percentages
            if any(char.isdigit() for char in word) or '%' in word or '$' in word:
                score += 2

            # Higher score for action/business words
            action_words = {'sees', 'shows', 'reports', 'announces', 'reveals', 'launches',
                           'gains', 'rises', 'falls', 'hits', 'reaches', 'breaks', 'surges',
                           'volatility', 'growth', 'increase', 'decrease', 'market', 'price'}
            if word_lower in action_words:
                score += 2

            # Lower score for filler words
            if word_lower in filler_words:
                score -= 2

            # Keep all words with their scores
            word_scores.append((word, score, i))

        # Sort by score (descending) but preserve some original order for readability
        word_scores.sort(key=lambda x: (-x[1], x[2]))

        # Select top words up to max_title_words
        selected_words = []
        selected_positions = []

        for word, score, pos in word_scores:
            if len(selected_words) >= self.config.max_title_words:
                break
            if score > 0:  # Only take words with positive scores
                selected_words.append(word)
                selected_positions.append(pos)

        # Sort selected words back to original order for natural reading
        word_pos_pairs = list(zip(selected_words, selected_positions))
        word_pos_pairs.sort(key=lambda x: x[1])
        final_words = [word for word, pos in word_pos_pairs]

        # Create the short title
        title = ' '.join(final_words)

        # Clean up title - keep alphanumeric, spaces, hyphens, and some punctuation
        title = re.sub(r'[^\w\s\-$%]', '', title)
        title = title.strip()

        # Ensure we have a reasonable title
        if not title or len(title.split()) < 2:
            # Fallback: take first few important words
            important_words = [word for word, score, pos in word_scores if score > 1][:self.config.max_title_words]
            title = ' '.join(important_words) if important_words else "Breaking News"

        return title if title else "Breaking News Update"

    def _generate_journalistic_paragraph(self, text: str, summary: str) -> str:
        """Generate structured paragraph: Facts → Transition → Analysis → Actionable Insights"""

        # Extract key information intelligently
        key_data = self._extract_key_data(text)
        story_type, detected_sentiment, main_subject = self._analyze_story_context(text, summary)

        # Phase 1: Extract clean factual summary (20-30% of content)
        factual_section = self._create_factual_opening(summary, key_data, main_subject)

        # Phase 2: Professional transition to analysis
        transition_phrase = self._get_professional_transition(story_type)

        # Phase 3: Substantial trading analysis (60-70% of content)
        trading_analysis = self._create_trading_analysis(text, key_data, story_type, detected_sentiment, main_subject)

        # Phase 4: Market outlook + actionable insights
        actionable_conclusion = self._create_actionable_insights(story_type, detected_sentiment, key_data, text)

        # Assemble with proper structure and flow
        paragraph = self._assemble_structured_paragraph(factual_section, transition_phrase, trading_analysis, actionable_conclusion)

        return paragraph

    def _create_factual_opening(self, summary: str, key_data: Dict, main_subject: str) -> str:
        """Create clean, concise factual opening (20-30% of content)"""

        # Clean the summary and make it concise
        factual_base = summary.strip()

        # Add key data points if they enhance the facts
        if key_data['percentages']:
            # If percentages aren't already in summary, add the most important one
            main_percentage = key_data['percentages'][0]
            if main_percentage not in factual_base:
                factual_base += f", with {main_percentage} movements observed"

        # Ensure clean sentence structure
        if not factual_base.endswith('.'):
            factual_base += '.'

        return factual_base

    def _get_professional_transition(self, story_type: str) -> str:
        """Get professional transition phrase based on story type"""

        transitions = {
            'crypto': [
                "From a trading perspective,",
                "Looking at market dynamics,",
                "From a technical standpoint,",
                "Analyzing the market reaction,"
            ],
            'stock_earnings': [
                "From an earnings analysis perspective,",
                "Looking at the financial implications,",
                "From a fundamental analysis standpoint,",
                "Examining the market response,"
            ],
            'stock_movement': [
                "From a technical analysis perspective,",
                "Looking at price action,",
                "From a momentum trading standpoint,",
                "Analyzing the volume patterns,"
            ],
            'fed_policy': [
                "From a macroeconomic perspective,",
                "Looking at policy implications,",
                "From a rates trading standpoint,",
                "Analyzing the monetary policy impact,"
            ],
            'market_general': [
                "From a market structure perspective,",
                "Looking at broader market dynamics,",
                "From an institutional flow standpoint,",
                "Analyzing the sentiment shifts,"
            ]
        }

        return random.choice(transitions.get(story_type, transitions['crypto']))

    def _create_trading_analysis(self, text: str, key_data: Dict, story_type: str, sentiment: str, main_subject: str) -> str:
        """Create substantial trading analysis (60-70% of content)"""

        analysis_parts = []
        text_lower = text.lower()

        # Get appropriate emoji for sentiment
        emoji = random.choice(GEN_Z_TRADING_VOCABULARY['emojis'][sentiment])

        # Core market analysis based on story type and sentiment
        if story_type == 'crypto':
            if sentiment == 'bearish':
                analysis_parts.append(f"this type of macro uncertainty typically triggers risk-off behavior in crypto markets {emoji}")
                if 'tariff' in text_lower or 'policy' in text_lower:
                    analysis_parts.append("Policy shifts like tariffs often create short-term selling pressure as traders de-risk positions")
            elif sentiment == 'bullish':
                analysis_parts.append(f"crypto is showing resilience against traditional market headwinds {emoji}")
            else:
                analysis_parts.append(f"we're seeing mixed signals with some assets holding stronger than others {emoji}")

        elif story_type == 'stock_earnings':
            if sentiment == 'bullish':
                analysis_parts.append(f"earnings beats like this typically trigger momentum continuation {emoji}")
                analysis_parts.append("Options traders who held through ER are likely seeing green across their screens")
            elif sentiment == 'bearish':
                analysis_parts.append(f"disappointing results often create oversold bounces for contrarian players {emoji}")

        # Add volume and momentum insights
        if any(word in text_lower for word in ['volume', 'trading', 'activity']):
            analysis_parts.append("Volume patterns are telling the real story here - institutional flows vs retail sentiment")

        # Add specific crypto insights
        if story_type == 'crypto':
            if 'bitcoin' in text_lower and 'ether' in text_lower:
                analysis_parts.append("BTC and ETH correlation remains strong, but alt performance is diverging")
            if any(alt in text_lower for alt in ['xrp', 'ada', 'sol']):
                analysis_parts.append("Alt coin resilience during macro uncertainty often signals underlying strength")

        # Market structure insights
        if any(word in text_lower for word in ['institutional', 'retail']):
            analysis_parts.append("The institutional vs retail dynamic is key to watch in this environment")

        # Technical considerations
        if key_data['percentages']:
            main_pct = key_data['percentages'][0]
            analysis_parts.append(f"The {main_pct} movement suggests we're testing key psychological levels")

        # Join analysis parts naturally
        if len(analysis_parts) >= 2:
            return f"{analysis_parts[0]}. {analysis_parts[1]}. " + ". ".join(analysis_parts[2:])
        elif len(analysis_parts) == 1:
            return f"{analysis_parts[0]}."
        else:
            return "market dynamics suggest this move has more room to develop."

    def _create_actionable_insights(self, story_type: str, sentiment: str, key_data: Dict, text: str) -> str:
        """Create market outlook + actionable trading advice"""

        insights = []
        emoji = random.choice(GEN_Z_TRADING_VOCABULARY['emojis'][sentiment])

        # Market Outlook first
        if story_type == 'crypto':
            if sentiment == 'bearish':
                insights.append("Short-term consolidation is likely as markets digest the policy implications")
            elif sentiment == 'bullish':
                insights.append("Momentum could accelerate if volume continues to expand")
            else:
                insights.append("Range-bound trading may persist until clearer directional catalysts emerge")

        # Actionable advice second
        actionable_advice = []

        if story_type == 'crypto':
            if 'whale' in text.lower() or 'institutional' in text.lower():
                actionable_advice.append("Keep an eye on whale wallet movements for early trend signals")

            if sentiment == 'bearish':
                actionable_advice.append("DCA strategies might find attractive entry points in this volatility")
            elif sentiment == 'bullish':
                actionable_advice.append("Momentum traders should watch for volume confirmation on any breakouts")
            else:
                actionable_advice.append("Range traders have solid opportunities between established support/resistance levels")

        elif story_type == 'stock_earnings':
            actionable_advice.append("Options flow and analyst revisions will be key catalysts to monitor")

        elif story_type == 'fed_policy':
            actionable_advice.append("Interest rate sensitive assets will remain in focus for position sizing decisions")

        # Default actionable advice if none specific
        if not actionable_advice:
            actionable_advice.append("Risk management remains paramount in this evolving market structure")

        # Combine outlook and advice
        full_insights = insights + actionable_advice

        if len(full_insights) >= 2:
            return f"{full_insights[0]}. {' '.join(full_insights[1:])} {emoji}"
        else:
            return f"{full_insights[0]} {emoji}"

    def _assemble_structured_paragraph(self, facts: str, transition: str, analysis: str, insights: str) -> str:
        """Assemble paragraph with proper structure and flow"""

        # Clean each section
        facts = facts.strip()
        transition = transition.strip()
        analysis = analysis.strip()
        insights = insights.strip()

        # Ensure proper punctuation
        if not facts.endswith('.'):
            facts += '.'
        if not analysis.endswith('.'):
            analysis += '.'
        if not insights.endswith('.') and not any(emoji in insights for emoji in ['🚀', '📈', '🔥', '💎', '📉', '😩', '💸', '⚡', '👀', '⏰', '📊', '🧐', '⚖️']):
            insights += '.'

        # Assemble with natural flow
        paragraph = f"{facts} {transition} {analysis} {insights}"

        # Clean up any double punctuation or spacing issues
        paragraph = re.sub(r'\.\.+', '.', paragraph)
        paragraph = re.sub(r'\s+', ' ', paragraph)
        paragraph = paragraph.strip()

        return paragraph

    def _extract_key_data(self, text: str) -> Dict[str, any]:
        """Extract key data points from the text"""
        data = {
            'percentages': [],
            'prices': [],
            'companies': [],
            'dates': [],
            'numbers': []
        }

        # Extract percentages
        percentages = re.findall(r'(\d+(?:\.\d+)?%)', text)
        data['percentages'] = percentages[:3]  # Limit to top 3

        # Extract price data (handle $ properly)
        prices = re.findall(r'\$(\d+(?:\.\d+)?(?:,\d{3})*(?:\.\d+)?)', text)
        data['prices'] = [f"${price}" for price in prices]

        # Extract company/entity names (capitalized sequences)
        companies = re.findall(r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b', text)
        # Filter out common words and keep meaningful names
        meaningful_companies = []
        for company in companies:
            if len(company) > 2 and company not in ['The', 'This', 'That', 'With', 'From', 'Over', 'Under', 'During']:
                meaningful_companies.append(company)
        data['companies'] = list(set(meaningful_companies))[:3]

        # Extract time indicators
        time_patterns = [
            r'(today|yesterday|this week|last week|this month|last month)',
            r'(in \w+ \d{4}|on \w+day)',
            r'(recent \w+|past \w+|following \w+)'
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            data['dates'].extend(matches)

        # Extract significant numbers
        numbers = re.findall(r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|thousand|trillion)', text)
        data['numbers'] = [f"{num} {unit}" for num, unit in numbers]

        return data

    def _analyze_story_context(self, text: str, summary: str) -> tuple:
        """Analyze financial story with sophisticated classification and sentiment detection"""
        combined_text = (text + " " + summary).lower()

        # Score each financial category
        category_scores = {}
        detected_sentiment = 'neutral'

        for story_type, config in FINANCIAL_STORY_TYPES.items():
            # Count keyword matches
            keyword_score = sum(1 for keyword in config['keywords'] if keyword in combined_text)
            category_scores[story_type] = keyword_score

        # Get primary category (default to stock_movement if no clear winner)
        primary_category = max(category_scores, key=category_scores.get) if any(category_scores.values()) else 'stock_movement'

        # Detect sentiment/market direction
        bullish_indicators = ['up', 'gain', 'rise', 'surge', 'increase', 'rally', 'moon', 'pump', 'green', 'beat', 'exceed', 'outperform']
        bearish_indicators = ['down', 'fall', 'drop', 'decline', 'crash', 'dump', 'red', 'miss', 'disappoint', 'underperform', 'sell-off']

        bullish_count = sum(1 for indicator in bullish_indicators if indicator in combined_text)
        bearish_count = sum(1 for indicator in bearish_indicators if indicator in combined_text)

        # Determine sentiment
        if bullish_count > bearish_count + 1:
            detected_sentiment = 'bullish'
        elif bearish_count > bullish_count + 1:
            detected_sentiment = 'bearish'
        else:
            detected_sentiment = 'neutral'

        # Extract main subject with financial context
        # Look for ticker symbols first
        ticker_pattern = r'\b[A-Z]{1,5}\b'
        tickers = re.findall(ticker_pattern, text)

        # Filter out common words that aren't tickers
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'HAS', 'BUT', 'NEW', 'CEO', 'CFO', 'USD', 'USD'}
        real_tickers = [ticker for ticker in tickers if ticker not in common_words and len(ticker) <= 5]

        if real_tickers:
            main_subject = real_tickers[0]
        else:
            # Fall back to entity extraction
            entities = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', text)
            main_subject = entities[0] if entities else "The asset"

        return primary_category, detected_sentiment, main_subject

    def _create_contextual_opening(self, story_type: str, sentiment: str, main_subject: str, key_data: Dict) -> str:
        """Create Gen Z trader-style opening based on story type and sentiment"""

        # Get appropriate emoji for sentiment
        emoji = random.choice(GEN_Z_TRADING_VOCABULARY['emojis'][sentiment])

        if story_type == 'crypto':
            if sentiment == 'bullish':
                slang = random.choice(FINANCIAL_STORY_TYPES['crypto']['positive_slang'])
                return f"{main_subject} is {slang} right now! {emoji}"
            elif sentiment == 'bearish':
                slang = random.choice(FINANCIAL_STORY_TYPES['crypto']['negative_slang'])
                return f"{main_subject} is {slang} today {emoji}"
            else:
                return f"{main_subject} is consolidating - classic crypto behavior {emoji}"

        elif story_type == 'stock_earnings':
            if sentiment == 'bullish':
                slang = random.choice(FINANCIAL_STORY_TYPES['stock_earnings']['positive_slang'])
                return f"{main_subject} just {slang}! {emoji}"
            elif sentiment == 'bearish':
                slang = random.choice(FINANCIAL_STORY_TYPES['stock_earnings']['negative_slang'])
                return f"{main_subject} {slang} on earnings {emoji}"
            else:
                return f"{main_subject} delivered earnings as expected {emoji}"

        elif story_type == 'stock_movement':
            if sentiment == 'bullish':
                slang = random.choice(FINANCIAL_STORY_TYPES['stock_movement']['positive_slang'])
                return f"{main_subject} is {slang}! {emoji}"
            elif sentiment == 'bearish':
                slang = random.choice(FINANCIAL_STORY_TYPES['stock_movement']['negative_slang'])
                return f"{main_subject} is {slang} {emoji}"
            else:
                return f"{main_subject} is chopping around in typical fashion {emoji}"

        elif story_type == 'fed_policy':
            if sentiment == 'bullish':
                return f"The Fed just made a {FINANCIAL_STORY_TYPES['fed_policy']['positive_slang'][0]} to the moon! {emoji}"
            elif sentiment == 'bearish':
                return f"Fed policy is {FINANCIAL_STORY_TYPES['fed_policy']['negative_slang'][0]} right now {emoji}"
            else:
                return f"The Fed kept things boring with no surprises {emoji}"

        elif story_type == 'market_general':
            if sentiment == 'bullish':
                return f"Markets are {FINANCIAL_STORY_TYPES['market_general']['positive_slang'][0]}! {emoji}"
            elif sentiment == 'bearish':
                return f"Markets are {FINANCIAL_STORY_TYPES['market_general']['negative_slang'][0]} {emoji}"
            else:
                return f"Markets are giving us {FINANCIAL_STORY_TYPES['market_general']['neutral_slang'][0]} {emoji}"

        else:
            # Default fallback
            if sentiment == 'bullish':
                return f"{main_subject} is absolutely crushing it right now! {emoji}"
            elif sentiment == 'bearish':
                return f"{main_subject} is having a rough day {emoji}"
            else:
                return f"{main_subject} is showing some interesting action {emoji}"

    def _build_main_content(self, summary: str, key_data: Dict, story_type: str, sentiment: str) -> str:
        """Build main content with Gen Z trader language and financial data integration"""

        # Start with the summary as base
        main_content = summary

        # Add trading-specific context based on story type
        if story_type == 'crypto' and key_data['percentages']:
            percentages = key_data['percentages'][:2]
            if sentiment == 'bullish':
                main_content += f" We're seeing some serious FOMO with {', '.join(percentages)} moves that got everyone jumping in"
            elif sentiment == 'bearish':
                main_content += f" The sell-off is brutal with {', '.join(percentages)} drops making hodlers question everything"
            else:
                main_content += f" Price action showing {', '.join(percentages)} swings - typical crypto volatility for you"

        elif story_type == 'stock_earnings' and key_data['percentages']:
            percentage = key_data['percentages'][0]
            if sentiment == 'bullish':
                main_content += f" AH trading is going absolutely brazy with {percentage} moves - options traders are probably printing"
            elif sentiment == 'bearish':
                main_content += f" The {percentage} drop in after-hours has got to hurt for anyone holding calls through earnings"
            else:
                main_content += f" Stock moved {percentage} on the earnings news - pretty much in line with expectations"

        elif story_type == 'stock_movement':
            if 'volume' in summary.lower():
                if sentiment == 'bullish':
                    main_content += " Volume is absolutely exploding - smart money is definitely making moves here"
                elif sentiment == 'bearish':
                    main_content += " Heavy volume on the way down usually means institutional selling pressure"
                else:
                    main_content += " Volume patterns suggest we might be setting up for a breakout either direction"

        # Add price context with trading slang
        if key_data['prices'] and len(key_data['prices']) > 0:
            price = key_data['prices'][0]
            if story_type in ['crypto', 'stock_movement']:
                if sentiment == 'bullish':
                    main_content += f" Currently sitting around {price} and looking like it wants to break higher"
                elif sentiment == 'bearish':
                    main_content += f" Trading near {price} but support levels are looking shaky"
                else:
                    main_content += f" Consolidating around the {price} level - range-bound for now"

        # Add transition phrase for flow
        transition = random.choice(GEN_Z_TRADING_VOCABULARY['transition_phrases'])
        if transition not in main_content:
            main_content = f"{transition} {main_content.lower()}"

        return main_content

    def _extract_supporting_details(self, text: str, key_data: Dict, story_type: str) -> str:
        """Extract trading insights and supporting details for Gen Z traders"""
        details = []
        text_lower = text.lower()

        # Crypto-specific insights
        if story_type == 'crypto':
            if any(word in text_lower for word in ['institutional', 'bank', 'corporation']):
                details.append("Institutional adoption is clearly accelerating - this isn't just retail FOMO anymore")

            if any(word in text_lower for word in ['regulation', 'sec', 'government']):
                details.append("Regulatory developments are shaping the narrative, as always in crypto")

            if 'whale' in text_lower or 'large' in text_lower:
                details.append("Big players are making moves - time to watch those whale wallets closely")

        # Stock-specific insights
        elif story_type in ['stock_earnings', 'stock_movement']:
            if any(word in text_lower for word in ['analyst', 'upgrade', 'downgrade']):
                details.append("Wall Street analysts are scrambling to update their models and price targets")

            if any(word in text_lower for word in ['option', 'call', 'put']):
                details.append("Options flow is probably going absolutely crazy right now - IV traders unite!")

            if any(word in text_lower for word in ['short', 'squeeze']):
                details.append("Short interest dynamics could make this move even more explosive")

        # Fed/Policy insights
        elif story_type == 'fed_policy':
            details.append("Bond traders are having a field day while equity futures dance around")

            if 'rate' in text_lower:
                details.append("Rate-sensitive sectors are going to feel this one hard")

        # General market insights
        if any(word in text_lower for word in ['volume', 'trading']):
            details.append("Volume tells the real story - and right now it's screaming that people are paying attention")

        if any(word in text_lower for word in ['retail', 'robinhood', 'webull', 'app']):
            details.append("Retail traders on commission-free platforms are definitely part of this action")

        # Technical analysis hints
        if any(word in text_lower for word in ['support', 'resistance', 'breakout']):
            details.append("Technical traders have been watching these levels for a while - breakouts don't lie")

        if any(word in text_lower for word in ['momentum', 'trend']):
            details.append("Momentum players are probably adding to positions here - trend is your friend until it isn't")

        # Social media/sentiment
        if any(word in text_lower for word in ['social', 'twitter', 'reddit', 'discord']):
            details.append("Social sentiment is absolutely buzzing - FinTwit is probably having a moment")

        return ". ".join(details) if details else ""

    def _create_relevant_conclusion(self, story_type: str, sentiment: str, key_data: Dict, text: str) -> str:
        """Create actionable conclusions with Gen Z trader language"""

        # Get appropriate emoji for sentiment
        emoji = random.choice(GEN_Z_TRADING_VOCABULARY['emojis'][sentiment])

        if story_type == 'crypto':
            if sentiment == 'bullish':
                conclusions = [
                    f"This could be the breakout crypto degens have been waiting for {emoji}",
                    f"HODLers are probably feeling pretty vindicated right now {emoji}",
                    f"If you've been DCAing through the bear market, today's your validation {emoji}"
                ]
            elif sentiment == 'bearish':
                conclusions = [
                    f"Paper hands are getting shaken out hard - diamond hands time {emoji}",
                    f"This dip might be the buying opportunity patient traders have been waiting for {emoji}",
                    f"Crypto winter vibes but smart money knows these are accumulation zones {emoji}"
                ]
            else:
                conclusions = [
                    f"Sideways action means range traders are eating good {emoji}",
                    f"Consolidation phases usually lead to explosive moves - patience required {emoji}"
                ]

        elif story_type == 'stock_earnings':
            if sentiment == 'bullish':
                conclusions = [
                    f"Earnings beats like this usually trigger analyst upgrades - watch for momentum {emoji}",
                    f"Options traders who held through ER are probably celebrating hard {emoji}",
                    f"This performance should give the stock some serious runway {emoji}"
                ]
            elif sentiment == 'bearish':
                conclusions = [
                    f"Earnings misses can create oversold bounces - contrarian opportunity? {emoji}",
                    f"Put holders are printing while call buyers are getting crushed {emoji}",
                    f"Sometimes bad earnings clear the air - lower expectations, higher potential {emoji}"
                ]
            else:
                conclusions = [
                    f"Meeting expectations is fine but won't move the needle much {emoji}",
                    f"Steady performance - not exciting but reliable for long-term holders {emoji}"
                ]

        elif story_type == 'fed_policy':
            if sentiment == 'bullish':
                conclusions = [
                    f"Risk-on mode activated - growth stocks about to party {emoji}",
                    f"Tech names and crypto should benefit from this dovish pivot {emoji}",
                    f"QQQ calls looking absolutely delicious right now {emoji}"
                ]
            elif sentiment == 'bearish':
                conclusions = [
                    f"Hawkish Fed means value over growth - time to rotate portfolios {emoji}",
                    f"Higher rates = bond gang wins, growth gang loses {emoji}",
                    f"Defensive sectors might be the play until Fed pivots {emoji}"
                ]
            else:
                conclusions = [
                    f"Status quo Fed policy - markets hate uncertainty but this removes some {emoji}",
                    f"No surprises is sometimes the best surprise in volatile times {emoji}"
                ]

        else:  # stock_movement, market_general, or default
            if sentiment == 'bullish':
                actionable_conclusions = [
                    f"Momentum traders should be watching for continuation patterns {emoji}",
                    f"Volume confirmation could send this way higher - technical setup looking clean {emoji}",
                    f"Breakout above resistance could trigger serious FOMO buying {emoji}"
                ]
            elif sentiment == 'bearish':
                actionable_conclusions = [
                    f"Support levels are key here - break below and things get ugly fast {emoji}",
                    f"This could be a healthy pullback before the next leg up {emoji}",
                    f"Buy-the-dip mentality will be tested if selling continues {emoji}"
                ]
            else:
                actionable_conclusions = [
                    f"Range-bound trading continues - scalpers' paradise {emoji}",
                    f"Waiting for a catalyst to break this consolidation pattern {emoji}",
                    f"Low volatility won't last forever - coiled spring energy building {emoji}"
                ]
            conclusions = actionable_conclusions

        return random.choice(conclusions)

    def _assemble_paragraph(self, parts: List[str]) -> str:
        """Assemble paragraph parts with proper transitions and punctuation"""
        if not parts:
            return "Recent developments have captured market attention."

        # Clean each part
        cleaned_parts = []
        for part in parts:
            if part and part.strip():
                # Ensure proper punctuation
                part = part.strip()
                if not part.endswith('.'):
                    part += '.'
                cleaned_parts.append(part)

        if not cleaned_parts:
            return "Recent developments have captured market attention."

        # Join with appropriate spacing
        paragraph = ' '.join(cleaned_parts)

        # Clean up any double punctuation or spacing issues
        paragraph = re.sub(r'\.\.+', '.', paragraph)
        paragraph = re.sub(r'\s+', ' ', paragraph)
        paragraph = paragraph.strip()

        return paragraph

    def summarize_article(self, title: str, article_text: str) -> Dict[str, str]:
        """
        Main method to summarize a news article with the specified format.

        Args:
            title: The title of the news article
            article_text: The full text of the news article

        Returns:
            Dictionary with title, paragraph, and hashtags
        """
        if not article_text or not article_text.strip():
            return {"error": "Empty article text provided."}

        logger.info("Starting article summarization...")

        # Clean the input text
        clean_title = self._clean_text(title)
        clean_text = self._clean_text(article_text)

        # Generate base summary
        base_summary = self._generate_base_summary(clean_text)

        if not base_summary:
            return {"error": "Could not generate summary."}

        # Generate all components
        hashtags = self._generate_hashtags(clean_text)
        short_title = self._generate_short_title(clean_title)
        journalistic_paragraph = self._generate_journalistic_paragraph(clean_text, base_summary)

        # Format the final output as dictionary
        result = {
            "title": short_title,
            "paragraph": journalistic_paragraph,
            "hashtags": " ".join(hashtags)
        }

        logger.info("Article summarization completed successfully")
        return result

# Utility functions for easy usage
def summarize_news_article(title: str, article_text: str, config: Optional[SummaryConfig] = None) -> Dict[str, str]:
    """
    Convenience function to summarize a single news article.

    Args:
        title: The title of the news article
        article_text: The full text of the news article
        config: Optional configuration object

    Returns:
        Dictionary with title, paragraph, and hashtags
    """
    summarizer = NewsArticleSummarizer(config)
    return summarizer.summarize_article(title, article_text)

def main():
    """Example usage of the news summarizer"""
    # Example article
    sample_title = "Apple Announces Revolutionary iPhone 15 Pro Max with Advanced Camera Technology"
    sample_article = """
    Tech giant Apple announced today that it will be releasing a new iPhone model with
    revolutionary camera technology. The iPhone 15 Pro Max will feature a 48-megapixel
    main camera with advanced computational photography capabilities. Apple CEO Tim Cook
    revealed during the keynote presentation that the new device will be available
    starting next month. The company expects this to be their most successful launch
    in recent years, with pre-orders beginning this Friday. Industry analysts predict
    strong sales numbers, especially given the enhanced features and competitive pricing.
    The new iPhone will also include improved battery life and faster processing speeds
    compared to previous models. Apple's stock price rose 3% following the announcement.
    """

    print("News Article Summarizer - Example Usage")
    print("=" * 50)

    # Create summarizer with default config
    summarizer = NewsArticleSummarizer()

    # Generate summary
    summary = summarizer.summarize_article(sample_title, sample_article)

    print("\nGenerated Summary:")
    print("-" * 30)
    print(f"Title: {summary['title']}")
    print(f"Paragraph: {summary['paragraph']}")
    print(f"Hashtags: {summary['hashtags']}")

if __name__ == "__main__":
    main()
