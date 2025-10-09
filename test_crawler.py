"""
Quick test script for TechCrunch crawler.

This script tests the crawler without requiring full environment setup.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.news.crawler.sources.techcrunch import create_techcrunch_crawler


def main():
    """Test TechCrunch crawler."""
    print("=" * 70)
    print("TechCrunch Crawler Test")
    print("=" * 70)
    print()

    try:
        # Create crawler
        print("Creating TechCrunch crawler...")
        crawler = create_techcrunch_crawler()
        print(f"✓ Crawler created: {crawler}")
        print()

        # Fetch news
        print("Fetching news (limit: 5)...")
        news_collection = crawler.fetch_news(limit=5, max_age_hours=48)
        print(f"✓ Fetched {news_collection.total} articles")
        print()

        # Display articles
        print("=" * 70)
        print("ARTICLES")
        print("=" * 70)
        print()

        for i, article in enumerate(news_collection.articles, 1):
            print(f"[{i}] {article.title}")
            print(f"    URL: {article.url}")
            print(f"    Category: {article.category.value} (weight: {article.category.weight})")
            print(f"    Importance: {article.importance.value}")
            print(f"    Published: {article.published_at.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"    Author: {article.author or 'Unknown'}")
            print(f"    Words: {article.word_count} ({article.reading_time} min read)")
            print(f"    Score: {article.score:.2f}")

            if article.summary:
                summary = article.summary[:150] + "..." if len(article.summary) > 150 else article.summary
                print(f"    Summary: {summary}")

            print()

        # Statistics
        print("=" * 70)
        print("STATISTICS")
        print("=" * 70)
        print()

        categories = {}
        importances = {}
        total_score = 0.0

        for article in news_collection.articles:
            # Count categories
            cat = article.category.value
            categories[cat] = categories.get(cat, 0) + 1

            # Count importances
            imp = article.importance.value
            importances[imp] = importances.get(imp, 0) + 1

            # Sum scores
            total_score += article.score

        print(f"Total articles: {news_collection.total}")
        print(f"Average score: {total_score / news_collection.total:.2f}")
        print()

        print("Categories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        print()

        print("Importance:")
        for imp, count in sorted(importances.items(), key=lambda x: x[1], reverse=True):
            print(f"  {imp}: {count}")
        print()

        # Top articles
        print("=" * 70)
        print("TOP 3 ARTICLES (by score)")
        print("=" * 70)
        print()

        top_articles = news_collection.get_top(3)
        for i, article in enumerate(top_articles, 1):
            print(f"{i}. [{article.score:.2f}] {article.title}")
            print(f"   {article.category.value} | {article.importance.value}")
            print()

        print("=" * 70)
        print("✓ TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)

        return 0

    except Exception as e:
        print()
        print("=" * 70)
        print("✗ TEST FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
