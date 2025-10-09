#!/usr/bin/env python3
"""한국 뉴스 크롤러 테스트 스크립트."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.news.crawler import create_news_crawler


def test_korean_crawlers():
    """한국 IT 뉴스 크롤러 테스트."""
    print("=" * 70)
    print("한국 IT 뉴스 크롤러 테스트")
    print("=" * 70)

    sources = ["etnews", "zdnet_kr"]

    for source in sources:
        print(f"\n{'='*70}")
        print(f"📰 {source.upper()} 크롤러 테스트")
        print(f"{'='*70}\n")

        try:
            # 크롤러 생성
            crawler = create_news_crawler(source)
            print(f"✅ 크롤러 생성 성공: {crawler.source.display_name}")
            print(f"   RSS URL: {crawler.rss_url}\n")

            # 뉴스 가져오기
            print("📥 뉴스 가져오는 중...")
            news_collection = crawler.fetch_news(limit=5, max_age_hours=48)

            print(f"✅ 뉴스 {news_collection.total}개 가져옴\n")

            # 뉴스 출력
            for i, news in enumerate(news_collection.articles, 1):
                print(f"{i}. {news.title}")
                print(f"   📅 {news.published_at.strftime('%Y-%m-%d %H:%M')}")
                print(f"   🔗 {news.url}")
                print(f"   📊 카테고리: {news.category.value}")
                print(f"   ⭐ 중요도: {news.importance.value}")
                print(f"   📈 점수: {news.calculate_score():.2f}")
                if news.summary:
                    summary = news.summary[:100] + "..." if len(news.summary) > 100 else news.summary
                    print(f"   📝 요약: {summary}")
                print()

        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 70)
    print("테스트 완료!")
    print("=" * 70)


if __name__ == "__main__":
    test_korean_crawlers()
