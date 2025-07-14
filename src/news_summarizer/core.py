"""
Core summarization module.

Contains the main NewsArticleSummarizer class and core business logic.
"""

import logging
import random
from typing import List, Dict, Optional
import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline, AutoTokenizer
import torch

from .config import SummaryConfig, FINANCIAL_STORY_TYPES, GEN_Z_TRADING_VOCABULARY
from .utils import clean_text, extract_key_data, generate_hashtags, generate_short_title

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Configure logging
logger = logging.getLogger(__name__)


class NewsArticleSummarizer:
    """
    Main class for news article summarization targeting Gen Z/Millennial audiences.
    """

    def __init__(self, config: Optional[SummaryConfig] = None):
        """
        Initialize the summarizer with configuration and load the models.

        Args:
            config: Configuration object for summarization parameters
        """
        self.config = config or SummaryConfig()
        self.device = 0 if torch.cuda.is_available() else -1
        # Check if we're using fast mode for performance optimizations
        from .config import FastSummaryConfig
        self.fast_mode = isinstance(config, FastSummaryConfig)

        logger.info(f"Loading summarization model: {self.config.model_name}")
        self.summarizer = pipeline(
            "summarization",
            model=self.config.model_name,
            device=self.device,
            return_tensors=False
        )

        logger.info(f"Loading sentiment analysis model: {self.config.sentiment_model_name}")
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=self.config.sentiment_model_name,
            device=self.device
        )

        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        logger.info("Models loaded successfully")

        # Warm up models with small input for faster first inference
        self._warm_up_models()

    def _warm_up_models(self):
        """Warm up models with small inputs to reduce first inference latency."""
        try:
            # Warm up summarizer
            dummy_text = "This is a sample text for warming up the model."
            self.summarizer(dummy_text, max_length=20, num_beams=1, do_sample=False)

            # Warm up sentiment analyzer
            self.sentiment_analyzer(dummy_text)

            logger.info("Models warmed up successfully")
        except Exception as e:
            logger.warning(f"Model warm-up failed: {e}")

    def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment using the financial sentiment analysis model.

        Args:
            text: Text to analyze

        Returns:
            Sentiment label ('positive', 'negative', or 'neutral')
        """
        try:
            result = self.sentiment_analyzer(text)
            if isinstance(result, list) and len(result) > 0:
                sentiment_label = result[0]['label'].lower()
                # Map model output to our expected format
                if 'positive' in sentiment_label:
                    return 'positive'
                elif 'negative' in sentiment_label:
                    return 'negative'
                else:
                    return 'neutral'
            return 'neutral'
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return 'neutral'

    def _analyze_story_context(self, text: str, summary: str) -> tuple:
        """
        Analyze story context to determine type and sentiment using AI models.

        Args:
            text: Article text
            summary: Article summary

        Returns:
            Tuple of (story_type, sentiment, main_subject)
        """
        combined_text = f"{text} {summary}".lower()

        # Determine story type (keeping existing logic for story type detection)
        story_type = 'market_general'  # Default
        max_matches = 0

        for story_key, story_data in FINANCIAL_STORY_TYPES.items():
            matches = sum(1 for keyword in story_data['keywords'] if keyword in combined_text)
            if matches > max_matches:
                max_matches = matches
                story_type = story_key

        # Use AI model for sentiment analysis
        sentiment = self._analyze_sentiment(text)

        # Extract main subject (keeping existing logic)
        main_subject = self._extract_main_subject(text)

        return story_type, sentiment, main_subject

    def _extract_main_subject(self, text: str) -> str:
        """
        Extract the main subject from text.

        Args:
            text: Article text

        Returns:
            Main subject string
        """
        import re

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

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks that fit within token limits.
        Optimized for performance by reducing tokenization overhead.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        # First, check if entire text fits in one chunk
        total_tokens = len(self.tokenizer.encode(text))
        if total_tokens <= self.config.max_chunk_tokens:
            return [text]

        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        current_tokens = 0

        for sentence in sentences:
            # Estimate tokens for performance (more accurate than encoding every time)
            sentence_tokens = len(sentence.split()) * 1.3  # rough estimation

            if current_tokens + sentence_tokens <= self.config.max_chunk_tokens:
                current_chunk = current_chunk + " " + sentence if current_chunk else sentence
                current_tokens += sentence_tokens
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
                current_tokens = sentence_tokens

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _generate_base_summary(self, text: str) -> str:
        """Generate a base summary from the input text using financial summarization model."""
        chunks = self._chunk_text(text)

        if not chunks:
            return ""

        # If single chunk, summarize directly
        if len(chunks) == 1:
            try:
                result = self.summarizer(
                    chunks[0],
                    max_length=60,
                    num_beams=2,
                    do_sample=False,  # Greedy search for speed
                    early_stopping=True
                )
                return self._extract_summary_text(result)
            except Exception as e:
                logger.error(f"Error summarizing single chunk: {e}")
                return chunks[0][:500]  # Fallback to truncation

        # For multiple chunks, use smarter combination strategy
        # If we have many small chunks, combine them first before summarizing
        if len(chunks) > 3:
            # Combine chunks into larger groups to reduce model calls
            combined_chunks = []
            current_group = ""
            current_tokens = 0

            for chunk in chunks:
                chunk_tokens = len(chunk.split()) * 1.3
                if current_tokens + chunk_tokens <= self.config.max_chunk_tokens * 0.8:  # Use 80% of limit for safety
                    current_group = current_group + " " + chunk if current_group else chunk
                    current_tokens += chunk_tokens
                else:
                    if current_group:
                        combined_chunks.append(current_group)
                    current_group = chunk
                    current_tokens = chunk_tokens

            if current_group:
                combined_chunks.append(current_group)

            chunks = combined_chunks

        # Summarize chunks with optimized parameters
        chunk_summaries = []
        for chunk in chunks:
            try:
                result = self.summarizer(
                    chunk,
                    max_length=40,  # Shorter for speed
                    min_length=20,
                    num_beams=2,
                    do_sample=False,
                    early_stopping=True
                )
                chunk_summaries.append(self._extract_summary_text(result))
            except Exception as e:
                logger.error(f"Error summarizing chunk: {e}")
                chunk_summaries.append(chunk[:150])  # Shorter fallback

        # If we have multiple summaries, combine them
        if len(chunk_summaries) > 1:
            combined = " ".join(chunk_summaries)
            # Only re-summarize if the combined text is still large
            if len(combined.split()) > 100:
                try:
                    result = self.summarizer(
                        combined,
                        max_length=60,
                        min_length=30,
                        num_beams=2,
                        do_sample=False,
                        early_stopping=True
                    )
                    return self._extract_summary_text(result)
                except Exception as e:
                    logger.error(f"Error summarizing combined chunks: {e}")
                    return combined[:500]
            else:
                return combined
        else:
            return chunk_summaries[0] if chunk_summaries else ""

    def _extract_summary_text(self, result) -> str:
        """Extract summary text from model result."""
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], dict) and 'summary_text' in result[0]:
                return result[0]['summary_text']
            elif isinstance(result[0], str):
                return result[0]
        return str(result)

    def _generate_bullet_points(self, text: str, summary: str) -> List[str]:
        """Generate bullet points from summary."""
        sentences = sent_tokenize(summary)
        bullet_points = []

        for sentence in sentences:
            if len(sentence.strip()) > 20:  # Skip very short sentences
                # Create bullet point with bold title
                words = sentence.split()
                if len(words) > 8:
                    title = " ".join(words[:4])
                    content = " ".join(words[4:])
                    bullet_point = f"• **{title}** || {content}"
                else:
                    bullet_point = f"• **{sentence[:30]}** || {sentence}"
                bullet_points.append(bullet_point)

        # Ensure we have the right number of bullet points
        while len(bullet_points) < self.config.min_bullet_points:
            bullet_points.append(f"• **Key point about the story** || Additional relevant information from the article.")

        return bullet_points[:self.config.max_bullet_points]

    def _generate_journalistic_paragraph(self, text: str, summary: str) -> tuple[str, str]:
        """Generate a journalistic paragraph with Gen Z flair targeting experienced traders."""
        # Fast mode: simplified processing
        if self.fast_mode:
            # Quick sentiment analysis
            sentiment = self._analyze_sentiment(summary)

            # Simplified paragraph generation
            factual_opening = self._create_factual_opening(text, summary, {})
            transition = "Looking at the charts, we're observing"  # Use fixed transition for speed

            # Simplified trading analysis
            if 'tesla' in text.lower() or 'musk' in text.lower():
                story_type = 'stocks'
            elif any(word in text.lower() for word in ['bitcoin', 'crypto', 'ethereum']):
                story_type = 'crypto'
            else:
                story_type = 'stocks'

            trading_analysis = self._create_simplified_analysis(sentiment, story_type)

            components = [factual_opening, transition, trading_analysis]
            return ' '.join(filter(None, components)), sentiment

        # Standard mode: full processing
        key_data = extract_key_data(text)
        story_type, sentiment, main_subject = self._analyze_story_context(text, summary)

        # Create factual opening (20-30% content)
        factual_opening = self._create_factual_opening(text, summary, key_data)

        # Professional transition
        transition = self._get_professional_transition(story_type, sentiment)

        # Trading analysis (60-70% content)
        trading_analysis = self._create_trading_analysis(summary, key_data, story_type, sentiment)

        # Actionable insights
        actionable_insights = self._create_actionable_insights(story_type, sentiment, key_data, text)

        # Combine all parts ensuring proper flow
        components = [factual_opening, transition, trading_analysis, actionable_insights]
        return ' '.join(filter(None, components)), sentiment

    def _create_simplified_analysis(self, sentiment: str, story_type: str) -> str:
        """Create a simplified trading analysis for fast mode."""
        # Basic analysis templates for speed
        templates = {
            'positive': {
                'stocks': "bullish momentum building 📈. Smart money accumulating on dips. Institutional flows looking strong fr. Risk-on sentiment driving the rally.",
                'crypto': "absolutely sending it 🚀. Bulls woke up and chose violence. Diamond hands paying off. DeFi yields still attractive for those hunting alpha."
            },
            'negative': {
                'stocks': "bearish divergence forming across major timeframes 📉. Smart money is likely de-risking while retail still holds bags. Risk management is key.",
                'crypto': "getting absolutely rekt. Major support levels breaking down. Hodlers crying in the club rn. Wait for oversold bounce before re-entry."
            },
            'neutral': {
                'stocks': "trading sideways in a tight range. Volume declining, waiting for catalysts. Scalp opportunities emerging but keep positions small.",
                'crypto': "crabbing hard in this range. DeFi farming still viable. Layer 2 tokens showing relative strength vs majors."
            }
        }

        return templates.get(sentiment, {}).get(story_type,
                                               "Mixed signals in the market. Playing defensive until clearer direction emerges.")

    def _create_factual_opening(self, text: str, summary: str, key_data: Dict) -> str:
        """Create a factual opening from the news content."""
        # Extract key sentences from the original text
        sentences = sent_tokenize(text)

        # Get the most important sentences (typically first 2-3 sentences)
        key_sentences = []
        for sentence in sentences[:3]:
            if len(sentence.split()) > 5:  # Avoid very short sentences
                key_sentences.append(sentence.strip())

        # Create concise factual summary
        if key_sentences:
            # Take first 2 sentences for factual opening
            opening_text = ' '.join(key_sentences[:2])
            # Remove any excessive length while preserving meaning
            if len(opening_text.split()) > 40:
                words = opening_text.split()
                opening_text = ' '.join(words[:40])
            return opening_text
        else:
            return summary.split('.')[0] + '.'

    def _get_professional_transition(self, story_type: str, sentiment: str) -> str:
        """Get professional transition phrase for credibility."""
        transitions = [
            "From a technical standpoint, we're seeing",
            "From a trading perspective, this signals",
            "Looking at the charts, we're observing",
            "From a market structure standpoint, we're seeing",
            "Technically speaking, this indicates"
        ]
        return random.choice(transitions)

    def _create_trading_analysis(self, summary: str, key_data: Dict, story_type: str, sentiment: str) -> str:
        """Create substantial trading analysis with Gen Z trading vocabulary."""
        # Trading insights based on story type and sentiment
        analysis_components = []

        # Get relevant slang and vocabulary
        slang_phrases = FINANCIAL_STORY_TYPES.get(story_type, {}).get(f"{sentiment}_slang", [])

        if story_type == 'crypto':
            if sentiment == 'positive':
                analysis_components.append("mixed signals with some assets holding stronger than others 📊")
                analysis_components.append("Volume patterns are telling the real story here - institutional flows vs retail sentiment")
            elif sentiment == 'negative':
                analysis_components.append("bearish divergence forming across major timeframes 📉")
                analysis_components.append("Smart money is likely de-risking while retail still holds bags")
            else:
                analysis_components.append("mixed signals with some assets holding stronger than others 📊")
                analysis_components.append("Volume patterns are telling the real story here - institutional flows vs retail sentiment")

        elif story_type == 'stock_earnings':
            if sentiment == 'positive':
                analysis_components.append("earnings momentum typically drives multi-quarter outperformance")
                analysis_components.append("Options flow is showing heavy call activity from institutional players")
            else:
                analysis_components.append("earnings disappointment often creates oversold bounce opportunities")
                analysis_components.append("Put/call ratios are elevated, suggesting capitulation might be near")

        else:
            analysis_components.append("mixed signals with some assets holding stronger than others 📊")
            analysis_components.append("Volume patterns are telling the real story here - institutional flows vs retail sentiment")

        # Add correlation insights
        if story_type == 'crypto':
            analysis_components.append("BTC and ETH correlation remains strong, but alt performance is diverging")
            analysis_components.append("Alt coin resilience during macro uncertainty often signals underlying strength")
        else:
            analysis_components.append("Sector rotation patterns are giving us clues about where smart money is positioning")

        return '. '.join(analysis_components) + '.'

    def _create_actionable_insights(self, story_type: str, sentiment: str, key_data: Dict, text: str) -> str:
        """Create actionable trading insights for experienced traders."""
        insights = []

        if story_type == 'crypto':
            if sentiment == 'positive':
                insights.append("Momentum plays are setting up nicely for continuation")
                insights.append("DeFi tokens might catch a bid if this keeps up ⚡")
            elif sentiment == 'negative':
                insights.append("Bounce plays might emerge from oversold levels")
                insights.append("Risk management is key - size down until volatility subsides")
            else:
                insights.append("Range-bound trading may persist until clearer directional catalysts emerge")
                insights.append("Range traders have solid opportunities between established support/resistance levels ⏰")

        elif story_type == 'stock_earnings':
            if sentiment == 'positive':
                insights.append("Earnings momentum trades typically have 2-3 week windows")
                insights.append("Look for sector peers to follow suit with similar beats")
            else:
                insights.append("Oversold bounces often happen 2-3 sessions after earnings dumps")
                insights.append("Wait for capitulation volume before considering entries")

        else:
            insights.append("Range-bound trading may persist until clearer directional catalysts emerge")
            insights.append("Range traders have solid opportunities between established support/resistance levels ⏰")

        return '. '.join(insights) + '.'

    def summarize_article(self, title: str, article_text: str) -> Dict[str, str]:
        """
        Summarize a news article with Gen Z/Millennial formatting.

        Args:
            title: Article title
            article_text: Article content

        Returns:
            Dictionary with structured summary [[memory:3128909]]
        """
        # Clean input text
        cleaned_text = clean_text(article_text)

        # Generate base summary
        base_summary = self._generate_base_summary(cleaned_text)

        # Generate bullet points
        bullet_points = self._generate_bullet_points(cleaned_text, base_summary)

        # Generate hashtags
        hashtags = generate_hashtags(cleaned_text, self.config.min_hashtags, self.config.max_hashtags)

        # Generate short title
        short_title = generate_short_title(base_summary, self.config.max_title_words)

        # Generate journalistic paragraph
        paragraph, sentiment = self._generate_journalistic_paragraph(cleaned_text, base_summary)

        # Format output according to user preference [[memory:3128909]]
        return {
            'title': short_title,
            'sentiment': sentiment,
            'paragraph': paragraph,
            'hashtags': ' '.join(hashtags)
        }
