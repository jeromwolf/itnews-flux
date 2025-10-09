"""
AI Translation Service for Tech News Digest.

Provides translation of English tech news to Korean using OpenAI GPT models.
Features:
- English to Korean translation
- Technical term preservation
- Natural Korean style
- Cost tracking and caching
"""

from pathlib import Path
from typing import Optional

from src.core.ai_services.base import BaseAIService, GenerationError


class TranslationService(BaseAIService):
    """
    AI Translation Service using OpenAI GPT.

    Translates English tech news content to natural Korean.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        cache_dir: Optional[Path] = None,
        enable_cache: bool = True,
    ):
        """
        Initialize translation service.

        Args:
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            cache_dir: Directory for caching translations
            enable_cache: Enable translation caching
        """
        super().__init__(cache_dir=cache_dir, enable_cache=enable_cache)
        self.model = model

        # Cost per 1M tokens (approximate for gpt-4o-mini)
        self.cost_per_input_token = 0.15 / 1_000_000  # $0.15 / 1M input tokens
        self.cost_per_output_token = 0.60 / 1_000_000  # $0.60 / 1M output tokens

        self.logger.info(f"Translation service initialized with model: {model}")

    def generate(
        self,
        text: str,
        source_lang: str = "English",
        target_lang: str = "Korean",
        context: Optional[str] = None,
    ) -> str:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source_lang: Source language (default: English)
            target_lang: Target language (default: Korean)
            context: Additional context for translation (e.g., "tech news")

        Returns:
            Translated text

        Raises:
            GenerationError: If translation fails
        """
        if not text or not text.strip():
            return ""

        # Check cache
        cache_key = f"{source_lang}_{target_lang}_{context or 'general'}_{text}"
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached.get("translation", text)

        # Prepare system prompt
        system_prompt = self._build_system_prompt(source_lang, target_lang, context)

        # Prepare user prompt
        user_prompt = text

        try:
            # Call OpenAI API
            self.logger.debug(
                f"Translating {len(text)} chars from {source_lang} to {target_lang}"
            )

            response = self._call_api_with_retry(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent translations
                max_tokens=2000,
            )

            # Extract translation
            translation = response.choices[0].message.content.strip()

            # Track costs
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = (
                input_tokens * self.cost_per_input_token
                + output_tokens * self.cost_per_output_token
            )
            self.total_cost += cost

            self.logger.info(
                f"Translation completed: {len(text)} chars → {len(translation)} chars "
                f"(cost: ${cost:.4f}, tokens: {input_tokens}+{output_tokens})"
            )

            # Save to cache
            self._save_to_cache(
                cache_key,
                {
                    "original": text,
                    "translation": translation,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "model": self.model,
                    "cost": cost,
                },
            )

            return translation

        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            raise GenerationError(f"Translation failed: {e}") from e

    def translate_news(
        self,
        title: str,
        summary: Optional[str] = None,
        preserve_technical_terms: bool = True,
    ) -> dict[str, str]:
        """
        Translate news title and summary to Korean.

        Args:
            title: News title to translate
            summary: News summary to translate (optional)
            preserve_technical_terms: Preserve technical terms in English

        Returns:
            Dictionary with translated title and summary
        """
        context = "IT/Tech news article"
        if preserve_technical_terms:
            context += " (preserve technical terms in English)"

        result = {"title": "", "summary": ""}

        # Translate title
        if title:
            result["title"] = self.generate(
                text=title,
                source_lang="English",
                target_lang="Korean",
                context=context,
            )

        # Translate summary
        if summary:
            result["summary"] = self.generate(
                text=summary,
                source_lang="English",
                target_lang="Korean",
                context=context,
            )

        return result

    def _build_system_prompt(
        self,
        source_lang: str,
        target_lang: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Build system prompt for translation.

        Args:
            source_lang: Source language
            target_lang: Target language
            context: Additional context

        Returns:
            System prompt
        """
        base_prompt = (
            f"You are a professional translator specializing in {source_lang} to {target_lang} translation. "
            f"Your task is to translate the given text naturally and accurately."
        )

        # Add context-specific instructions
        if context:
            if "tech" in context.lower() or "it" in context.lower():
                base_prompt += (
                    "\n\nGuidelines for tech/IT translation:\n"
                    "1. Preserve technical terms in English when appropriate (e.g., API, SDK, AI, ML)\n"
                    "2. Use natural Korean expressions for common tech concepts\n"
                    "3. Maintain professional and clear language\n"
                    "4. Keep the original meaning and tone\n"
                    "5. For product names and company names, keep them in English"
                )

            if "news" in context.lower():
                base_prompt += (
                    "\n\nGuidelines for news translation:\n"
                    "1. Use concise and clear language suitable for news headlines and articles\n"
                    "2. Maintain journalistic tone and objectivity\n"
                    "3. Preserve key facts and information accurately\n"
                    "4. Use Korean news writing conventions"
                )

        base_prompt += (
            "\n\nIMPORTANT: Provide ONLY the translation without any additional explanations, "
            "comments, or notes. Do not add 'Here is the translation:' or similar phrases."
        )

        return base_prompt


def create_translation_service(
    model: str = "gpt-4o-mini",
    cache_dir: Optional[Path] = None,
    enable_cache: bool = True,
) -> TranslationService:
    """
    Create translation service instance.

    Args:
        model: OpenAI model to use
        cache_dir: Cache directory
        enable_cache: Enable caching

    Returns:
        Translation service instance

    Example:
        >>> translator = create_translation_service()
        >>> result = translator.translate_news(
        ...     title="OpenAI Releases GPT-5",
        ...     summary="OpenAI has announced the release of GPT-5..."
        ... )
        >>> print(result["title"])
        OpenAI, GPT-5 출시
    """
    return TranslationService(
        model=model,
        cache_dir=cache_dir,
        enable_cache=enable_cache,
    )
