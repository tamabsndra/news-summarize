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
from .utils import clean_text, extract_key_data, analyze_story_context, generate_hashtags, generate_short_title

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
        """Generate a base summary from the input text."""
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
                return self._extract_summary_text(result)
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
                chunk_summaries.append(self._extract_summary_text(result))
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
                return self._extract_summary_text(result)
            except Exception as e:
                logger.error(f"Error summarizing combined chunks: {e}")
                return combined[:500]

        return combined[:500]

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

    def _generate_journalistic_paragraph(self, text: str, summary: str) -> str:
        """Generate a journalistic paragraph with Gen Z flair."""
        key_data = extract_key_data(text)
        story_type, sentiment, main_subject = analyze_story_context(text, summary)

        # Create opening
        opening = self._create_contextual_opening(story_type, sentiment, main_subject, key_data)

        # Main content
        main_content = self._build_main_content(summary, key_data, story_type, sentiment)

        # Conclusion
        conclusion = self._create_relevant_conclusion(story_type, sentiment, key_data, text)

        return f"{opening} {main_content} {conclusion}"

    def _create_contextual_opening(self, story_type: str, sentiment: str, main_subject: str, key_data: Dict) -> str:
        """Create contextual opening based on story type and sentiment."""
        if story_type == 'crypto':
            if sentiment == 'positive':
                return f"{main_subject} is absolutely sending it today 🚀"
            elif sentiment == 'negative':
                return f"{main_subject} is getting absolutely rekt right now 📉"
            else:
                return f"{main_subject} is trading sideways but there's definitely something brewing 👀"
        elif story_type == 'stock_earnings':
            if sentiment == 'positive':
                return f"{main_subject} absolutely smashed earnings expectations"
            elif sentiment == 'negative':
                return f"{main_subject} completely whiffed on earnings and disappointed the street"
            else:
                return f"{main_subject} came in pretty much as expected with earnings"
        else:
            return f"The market is showing some serious {sentiment} energy around {main_subject}"

    def _build_main_content(self, summary: str, key_data: Dict, story_type: str, sentiment: str) -> str:
        """Build the main content of the paragraph."""
        # Get relevant slang based on story type and sentiment
        slang_phrases = FINANCIAL_STORY_TYPES.get(story_type, {}).get(f"{sentiment}_slang", [])

        if slang_phrases:
            slang = random.choice(slang_phrases)
            return f"The numbers are {slang}, and smart money is probably taking notice. {summary[:100]}..."
        else:
            return f"The situation is developing with {sentiment} momentum. {summary[:100]}..."

    def _create_relevant_conclusion(self, story_type: str, sentiment: str, key_data: Dict, text: str) -> str:
        """Create a relevant conclusion."""
        conclusions = GEN_Z_TRADING_VOCABULARY.get('actionable_conclusions', [])

        if conclusions:
            conclusion = random.choice(conclusions)
            if '{}' in conclusion:
                main_subject = extract_key_data(text).get('companies', ['this'])
                subject = main_subject[0] if main_subject else 'this'
                return conclusion.format(subject)
            return conclusion
        else:
            return "This might be the setup traders have been waiting for."

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
        paragraph = self._generate_journalistic_paragraph(cleaned_text, base_summary)

        # Format output according to user preference [[memory:3128909]]
        return {
            'title': short_title,
            'paragraph': paragraph,
            'hashtags': ' '.join(hashtags)
        }
