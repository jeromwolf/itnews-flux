"""
News selection algorithm for Tech News Digest.

Selects optimal news articles based on:
- Importance score
- Category weight (IT/Tech prioritized)
- Diversity (avoid category duplication)
- Recency
- Learning suitability (length, readability)
"""

from collections import Counter
from typing import Optional

from src.core.config import get_settings
from src.core.logging import get_logger, log_execution_time
from src.news.models import News, NewsCategory, NewsCollection

settings = get_settings()
logger = get_logger(__name__)


class NewsSelector:
    """
    News selection algorithm.

    Selects top N news articles based on multiple criteria while
    maintaining diversity and IT/Tech focus.
    """

    def __init__(
        self,
        it_tech_ratio: float = 0.75,  # 75% IT/Tech news
        max_category_duplicate: int = 2,  # Max 2 articles from same category
    ):
        """
        Initialize news selector.

        Args:
            it_tech_ratio: Ratio of IT/Tech news (0.6-0.8)
            max_category_duplicate: Maximum articles from same category
        """
        self.it_tech_ratio = it_tech_ratio
        self.max_category_duplicate = max_category_duplicate
        self.logger = get_logger(__name__)

    @log_execution_time(logger)
    def select_top_news(
        self,
        news_collection: NewsCollection,
        count: int = 5,
    ) -> list[News]:
        """
        Select top N news articles.

        Args:
            news_collection: Collection of news articles
            count: Number of articles to select

        Returns:
            List of selected news articles

        Algorithm:
        1. Calculate scores for all articles
        2. Separate IT/Tech and Business news
        3. Select based on ratio (IT 3-4, Business 1-2)
        4. Ensure diversity (avoid category duplication)
        5. Sort by score and return top N
        """
        self.logger.info(
            f"Starting news selection: {news_collection.total} articles → {count} selected"
        )

        if news_collection.total == 0:
            self.logger.warning("No articles to select from")
            return []

        # Calculate scores for all articles
        for article in news_collection.articles:
            article.calculate_score()

        # Separate IT/Tech and Business articles
        it_tech_articles = [
            a for a in news_collection.articles if a.category.is_it_tech
        ]
        business_articles = [
            a for a in news_collection.articles if a.category.is_business
        ]
        other_articles = [
            a
            for a in news_collection.articles
            if not a.category.is_it_tech and not a.category.is_business
        ]

        self.logger.debug(
            f"Article breakdown: IT/Tech={len(it_tech_articles)}, "
            f"Business={len(business_articles)}, Other={len(other_articles)}"
        )

        # Calculate target counts
        it_tech_count = int(count * self.it_tech_ratio)
        business_count = count - it_tech_count

        # Adjust if not enough articles in each category
        if len(it_tech_articles) < it_tech_count:
            it_tech_count = len(it_tech_articles)
            business_count = count - it_tech_count

        if len(business_articles) < business_count:
            business_count = len(business_articles)
            it_tech_count = min(count - business_count, len(it_tech_articles))

        self.logger.debug(
            f"Target selection: IT/Tech={it_tech_count}, Business={business_count}"
        )

        # Select articles with diversity
        selected_it_tech = self._select_diverse_articles(
            it_tech_articles,
            it_tech_count,
        )
        selected_business = self._select_diverse_articles(
            business_articles,
            business_count,
        )

        # Combine and fill remaining slots if needed
        selected = selected_it_tech + selected_business

        # Fill remaining slots from other articles if needed
        remaining_count = count - len(selected)
        if remaining_count > 0 and other_articles:
            selected_other = self._select_diverse_articles(
                other_articles,
                remaining_count,
            )
            selected.extend(selected_other)

        # Sort by score (highest first)
        selected.sort(key=lambda x: x.score, reverse=True)

        # Take top N
        final_selection = selected[:count]

        # Log selection results
        self._log_selection_results(final_selection)

        return final_selection

    def _select_diverse_articles(
        self,
        articles: list[News],
        count: int,
    ) -> list[News]:
        """
        Select articles ensuring category diversity.

        Args:
            articles: List of articles to select from
            count: Number to select

        Returns:
            Selected articles with diversity
        """
        if not articles:
            return []

        # Sort by score
        sorted_articles = sorted(articles, key=lambda x: x.score, reverse=True)

        selected = []
        category_counts: Counter = Counter()

        for article in sorted_articles:
            if len(selected) >= count:
                break

            category = article.category

            # Check if we can add this category
            if category_counts[category] < self.max_category_duplicate:
                selected.append(article)
                category_counts[category] += 1

        # If we still need more articles, relax the diversity constraint
        if len(selected) < count:
            remaining = [a for a in sorted_articles if a not in selected]
            needed = count - len(selected)
            selected.extend(remaining[:needed])

        return selected

    def _log_selection_results(self, selected: list[News]) -> None:
        """
        Log selection results for debugging.

        Args:
            selected: Selected articles
        """
        self.logger.info(f"Selected {len(selected)} articles")

        # Category breakdown
        category_counts: Counter = Counter()
        for article in selected:
            category_counts[article.category.value] += 1

        self.logger.info(
            "Category breakdown: "
            + ", ".join(f"{cat}={count}" for cat, count in category_counts.most_common())
        )

        # Importance breakdown
        importance_counts: Counter = Counter()
        for article in selected:
            importance_counts[article.importance.value] += 1

        self.logger.debug(
            "Importance breakdown: "
            + ", ".join(
                f"{imp}={count}" for imp, count in importance_counts.most_common()
            )
        )

        # Average score
        avg_score = sum(a.score for a in selected) / len(selected) if selected else 0
        self.logger.debug(f"Average selection score: {avg_score:.2f}")

        # List selected articles
        for i, article in enumerate(selected, 1):
            self.logger.debug(
                f"  [{i}] [{article.score:.2f}] {article.category.value} | "
                f"{article.importance.value} | {article.title[:60]}..."
            )

    def validate_selection(self, selected: list[News]) -> dict:
        """
        Validate selection meets requirements.

        Args:
            selected: Selected articles

        Returns:
            Validation results
        """
        if not selected:
            return {
                "valid": False,
                "errors": ["No articles selected"],
            }

        errors = []
        warnings = []

        # Check count
        if len(selected) < 3:
            warnings.append(f"Only {len(selected)} articles selected (expected 5)")

        # Check IT/Tech ratio
        it_tech_count = sum(1 for a in selected if a.category.is_it_tech)
        it_tech_actual_ratio = it_tech_count / len(selected) if selected else 0

        if it_tech_actual_ratio < 0.6:
            warnings.append(
                f"IT/Tech ratio too low: {it_tech_actual_ratio:.1%} (target: 60-80%)"
            )

        # Check diversity
        category_counts = Counter(a.category for a in selected)
        max_duplicate = max(category_counts.values()) if category_counts else 0

        if max_duplicate > self.max_category_duplicate:
            warnings.append(
                f"Too many articles from same category: {max_duplicate} "
                f"(max: {self.max_category_duplicate})"
            )

        # Check for duplicates (same URL)
        urls = [str(a.url) for a in selected]
        if len(urls) != len(set(urls)):
            errors.append("Duplicate articles detected")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "it_tech_ratio": it_tech_actual_ratio,
            "category_diversity": len(category_counts),
        }


# Convenience function
def select_news(
    news_collection: NewsCollection,
    count: int = 5,
    it_tech_ratio: float = 0.75,
) -> list[News]:
    """
    Select top news articles from collection.

    Args:
        news_collection: Collection of news articles
        count: Number of articles to select (default: 5)
        it_tech_ratio: Ratio of IT/Tech news (default: 0.75)

    Returns:
        List of selected news articles

    Example:
        >>> from src.news.selector import select_news
        >>> selected = select_news(news_collection, count=5)
        >>> print(f"Selected {len(selected)} articles")
    """
    selector = NewsSelector(it_tech_ratio=it_tech_ratio)
    return selector.select_top_news(news_collection, count=count)
