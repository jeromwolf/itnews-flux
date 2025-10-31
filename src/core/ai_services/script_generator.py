"""
GPT-4o Script Generator for Tech News Digest.

Generates professional news anchor scripts with:
- English news content
- Korean translation
- Key vocabulary extraction
- Natural conversational flow
"""

import json
from typing import Optional

from src.core.ai_services.base import BaseAIService, GenerationError
from src.core.ai_services.models import GeneratedScript, ScriptStyle
from src.core.logging import get_logger, log_execution_time
from src.news.models import News

logger = get_logger(__name__)


class ScriptGenerator(BaseAIService):
    """
    GPT-4o script generator for news content.

    Generates professional anchor-style scripts optimized for:
    - English learning (clear vocabulary)
    - News delivery (professional tone)
    - YouTube format (3-5 minutes)
    """

    def __init__(self, **kwargs):
        """Initialize script generator."""
        super().__init__(**kwargs)
        self.model = self.settings.openai.gpt_model

        # Pricing (GPT-4o as of 2025)
        self.price_input = 2.50 / 1_000_000  # $2.50 per 1M input tokens
        self.price_output = 10.00 / 1_000_000  # $10.00 per 1M output tokens

    @log_execution_time(logger)
    def generate(
        self,
        news: News,
        style: ScriptStyle | str = ScriptStyle.PROFESSIONAL,
        target_duration: int = 60,  # 60 seconds per news
        include_vocabulary: bool = True,
        is_first_segment: bool = False,  # 첫 번째 세그먼트 여부
        is_last_segment: bool = False,  # 마지막 세그먼트 여부
    ) -> GeneratedScript:
        """
        Generate news script from article.

        Args:
            news: News article
            style: Script style (enum or string)
            target_duration: Target duration in seconds
            include_vocabulary: Extract key vocabulary
            is_first_segment: Whether this is the first segment (includes greeting)
            is_last_segment: Whether this is the last segment (includes closing)

        Returns:
            Generated script

        Raises:
            GenerationError: If generation fails
        """
        # Convert string to enum if needed
        if isinstance(style, str):
            style = ScriptStyle(style)

        self.logger.info(
            f"Generating script for: {news.title[:50]}... "
            f"(style={style.value}, duration={target_duration}s)"
        )

        # Check cache
        cache_key = f"{news.url}_{style.value}_{target_duration}"
        cached = self._load_from_cache(cache_key)
        if cached:
            return GeneratedScript(**cached)

        # Build prompt
        prompt = self._build_prompt(news, style, target_duration, include_vocabulary, is_first_segment, is_last_segment)

        # Generate script
        try:
            response = self._call_api_with_retry(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(style),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )

            # Parse response
            content = response.choices[0].message.content
            data = json.loads(content)

            # Calculate cost
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            cost = (
                prompt_tokens * self.price_input
                + completion_tokens * self.price_output
            )
            self.total_cost += cost

            # Create script object
            script = GeneratedScript(
                english_script=data.get("english_script", ""),
                korean_translation=data.get("korean_translation", ""),
                key_vocabulary=data.get("key_vocabulary", []),
                word_count=len(data.get("english_script", "").split()),
                estimated_duration=float(data.get("estimated_duration", target_duration)),
                style=style,
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_cost=cost,
            )

            # Save to cache
            self._save_to_cache(cache_key, script.model_dump())

            self.logger.info(
                f"Script generated: {script.word_count} words, "
                f"~{script.estimated_duration:.0f}s, "
                f"${cost:.4f}"
            )

            return script

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse GPT response: {e}")
            raise GenerationError(f"Invalid JSON response: {e}") from e

        except Exception as e:
            self.logger.error(f"Script generation failed: {e}", exc_info=True)
            raise GenerationError(f"Script generation failed: {e}") from e

    def _get_system_prompt(self, style: ScriptStyle) -> str:
        """
        Get system prompt based on style.

        Args:
            style: Script style

        Returns:
            System prompt
        """
        base_prompt = """You are a professional news anchor for a YouTube tech news channel called "Tech News Digest".
Your audience consists of IT professionals, developers, and tech enthusiasts who want to learn English while staying updated on tech trends.

Your task is to transform news articles into engaging, clear, and educational scripts."""

        style_prompts = {
            ScriptStyle.PROFESSIONAL: """
Style Guidelines:
- Professional but approachable tone
- Clear, precise language
- Avoid jargon unless explaining it
- Use active voice
- Include context for technical terms
""",
            ScriptStyle.CASUAL: """
Style Guidelines:
- Conversational and friendly tone
- Use simple everyday language
- Include relatable examples
- Feel free to express opinions
- Keep it engaging and fun
""",
            ScriptStyle.EDUCATIONAL: """
Style Guidelines:
- Focus on teaching and explaining
- Break down complex concepts
- Provide analogies and examples
- Highlight learning opportunities
- Emphasize key vocabulary
""",
        }

        return base_prompt + style_prompts.get(style, "")

    def _build_prompt(
        self,
        news: News,
        style: ScriptStyle,
        target_duration: int,
        include_vocabulary: bool,
        is_first_segment: bool = False,
        is_last_segment: bool = False,
    ) -> str:
        """
        Build prompt for script generation.

        Args:
            news: News article
            style: Script style
            target_duration: Target duration
            include_vocabulary: Include vocabulary
            is_first_segment: Whether this is the first segment
            is_last_segment: Whether this is the last segment

        Returns:
            Prompt string
        """
        vocab_instruction = ""
        if include_vocabulary:
            vocab_instruction = """
5. key_vocabulary: Array of 3-5 important words/phrases with:
   - word: The term
   - meaning: Korean translation
   - example: Example sentence using the word
"""

        # 세그먼트별 금지 사항을 먼저 명확히 설정
        segment_restriction = ""
        if is_first_segment:
            segment_restriction = """
⚠️ CRITICAL: This is the FIRST segment of a multi-segment video.
- You MUST include the opening greeting: "안녕하세요! AI ON, 톡톡입니다."
- Brand name "AI ON, 톡톡" is MANDATORY and cannot be omitted
"""
        elif is_last_segment:
            segment_restriction = """
⚠️ CRITICAL: This is the LAST segment of a multi-segment video.
- You MUST include the closing: "좋은 하루 보내세요! AI ON, 톡톡이었습니다."
- Brand name "AI ON, 톡톡" is MANDATORY and cannot be omitted
"""
        else:
            segment_restriction = """
🚫 CRITICAL: This is a MIDDLE segment of a multi-segment video.
- DO NOT include ANY greeting like "안녕하세요"
- DO NOT repeat "AI ON, 톡톡입니다" (only first segment has this)
- DO NOT include closing remarks (only last segment has this)
- ONLY use transition phrases like "다음 소식입니다" + news content
"""

        prompt = f"""{segment_restriction}

Transform this tech news article into a {target_duration}-second news script.

Article Information:
- Title: {news.title}
- Category: {news.category.value}
- Summary: {news.summary}
- URL: {news.url}

Requirements:
- Target duration: {target_duration} seconds (~{target_duration * 2.5:.0f} words)
- Style: {style.value}
- Language: Clear, educational English suitable for non-native speakers
- Include context and explain technical terms
- Make it engaging and informative

Return a JSON object with:
1. english_script: The complete news script in English
2. korean_translation: Korean translation of the script
3. estimated_duration: Estimated reading time in seconds
4. word_count: Number of words in the script
{vocab_instruction}

Example structure for the script:
"""

        # 세그먼트별 멘트 구조
        if is_first_segment:
            prompt += """
첫 번째 세그먼트 (오프닝 멘트 - 전체 영상에서 단 한 번만 사용):

반드시 이 형식으로 시작:
"안녕하세요! AI ON, 톡톡입니다.
오늘도 흥미로운 인공지능 소식들을 준비했습니다.
바로 시작해볼까요?

첫 번째 소식입니다. [뉴스 내용]"

CRITICAL RULES - 절대 지켜야 함:
1. 반드시 "안녕하세요! AI ON, 톡톡입니다."로 시작
2. "AI ON, 톡톡" 브랜드명을 정확히 그대로 사용 (절대 생략 금지)
3. 이 인사는 첫 번째 세그먼트에서만 단 한 번 사용
4. 순수 한글 스크립트 (기술 용어만 영어 가능)
"""
        elif is_last_segment:
            prompt += """
마지막 세그먼트 (클로징 멘트 - 전체 영상에서 단 한 번만 사용):

반드시 이 형식으로 끝:
"[뉴스 내용]

오늘 준비한 AI 소식은 여기까지입니다.
내일도 새로운 인공지능 뉴스로 찾아뵙겠습니다.
좋은 하루 보내세요! AI ON, 톡톡이었습니다."

CRITICAL RULES - 절대 지켜야 함:
1. 반드시 "AI ON, 톡톡이었습니다."로 끝내기 (절대 생략 금지)
2. "AI ON, 톡톡" 브랜드명을 정확히 그대로 사용
3. 이 클로징은 마지막 세그먼트에서만 단 한 번 사용
4. 순수 한글 스크립트 (기술 용어만 영어 가능)
"""
        else:
            prompt += """
중간 세그먼트 (전환 멘트만 사용 - 인사 없음):

다음 4가지 전환 멘트 중 하나를 자연스럽게 선택:
1. "다음 소식입니다. [뉴스 내용]"
2. "이어서 다음 뉴스 전해드리겠습니다. [뉴스 내용]"
3. "계속해서, 이런 소식도 있습니다. [뉴스 내용]"
4. "또 다른 AI 뉴스입니다. [뉴스 내용]"

CRITICAL RULES - 절대 지켜야 함:
1. 절대 "안녕하세요" 같은 인사말 사용 금지 (첫 번째 세그먼트에서만 사용)
2. 절대 "AI ON, 톡톡입니다" 반복 금지 (첫 번째 세그먼트에서만 사용)
3. 절대 클로징 멘트 사용 금지 (마지막 세그먼트에서만 사용)
4. 오직 전환 멘트 + 뉴스 내용만 포함
5. 순수 한글 스크립트 (기술 용어만 영어 가능)
"""

        return prompt

    def generate_batch(
        self,
        news_list: list[News],
        style: ScriptStyle = ScriptStyle.PROFESSIONAL,
        target_duration: int = 60,
    ) -> list[GeneratedScript]:
        """
        Generate scripts for multiple news articles.

        Args:
            news_list: List of news articles
            style: Script style
            target_duration: Target duration per script

        Returns:
            List of generated scripts
        """
        self.logger.info(f"Generating {len(news_list)} scripts in batch")

        scripts = []
        for i, news in enumerate(news_list, 1):
            try:
                self.logger.info(f"Processing {i}/{len(news_list)}: {news.title[:50]}...")
                script = self.generate(news, style, target_duration)
                scripts.append(script)

            except GenerationError as e:
                self.logger.error(f"Failed to generate script for news {i}: {e}")
                # Continue with next article
                continue

        self.logger.info(
            f"Batch generation complete: {len(scripts)}/{len(news_list)} successful, "
            f"total cost: ${self.total_cost:.4f}"
        )

        return scripts


def create_script_generator(**kwargs) -> ScriptGenerator:
    """
    Create script generator instance.

    Returns:
        ScriptGenerator instance

    Example:
        >>> generator = create_script_generator()
        >>> script = generator.generate(news_article)
        >>> print(script.english_script)
    """
    return ScriptGenerator(**kwargs)
