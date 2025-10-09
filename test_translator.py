#!/usr/bin/env python3
"""AI 번역 서비스 테스트 스크립트."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.ai_services import create_translation_service


def test_translation():
    """AI 번역 서비스 테스트."""
    print("=" * 70)
    print("🌐 AI 번역 서비스 테스트")
    print("=" * 70)

    # 번역 서비스 생성
    print("\n📝 번역 서비스 초기화 중...")
    translator = create_translation_service(model="gpt-4o-mini", enable_cache=True)
    print(f"✅ 번역 서비스 생성 완료: {translator.model}\n")

    # 테스트 뉴스 데이터
    test_news = [
        {
            "title": "OpenAI Releases GPT-5 with Advanced Reasoning Capabilities",
            "summary": "OpenAI has announced the release of GPT-5, featuring significantly improved reasoning and problem-solving abilities. The new model shows remarkable performance in complex mathematical tasks and scientific research.",
        },
        {
            "title": "Google Unveils New AI-Powered Search Features",
            "summary": "Google introduced AI-enhanced search capabilities that provide more contextual and personalized results. The update leverages advanced language models to better understand user intent.",
        },
        {
            "title": "Apple Launches New MacBook Pro with M4 Chip",
            "summary": "Apple's latest MacBook Pro features the powerful M4 chip, offering 40% better performance and improved battery life. The new model includes enhanced display technology and faster memory.",
        },
    ]

    # 각 뉴스 번역
    for i, news in enumerate(test_news, 1):
        print(f"{'='*70}")
        print(f"📰 테스트 {i}/{len(test_news)}")
        print(f"{'='*70}\n")

        print(f"원문 제목: {news['title']}")
        print(f"원문 요약: {news['summary']}\n")

        try:
            # 번역 실행
            print("🔄 번역 중...")
            result = translator.translate_news(
                title=news["title"], summary=news["summary"], preserve_technical_terms=True
            )

            print(f"\n✅ 번역 완료!")
            print(f"번역된 제목: {result['title']}")
            print(f"번역된 요약: {result['summary']}\n")

            # 통계 출력
            stats = translator.get_stats()
            print(f"💰 누적 비용: ${stats['total_cost']:.4f}")
            print(f"📊 누적 요청: {stats['request_count']}회\n")

        except Exception as e:
            print(f"❌ 번역 실패: {e}\n")
            import traceback

            traceback.print_exc()

    # 최종 통계
    print("\n" + "=" * 70)
    print("📊 최종 통계")
    print("=" * 70)
    stats = translator.get_stats()
    print(f"총 비용: ${stats['total_cost']:.4f}")
    print(f"총 요청: {stats['request_count']}회")
    print(f"캐시 활성화: {stats['cache_enabled']}")
    print(f"캐시 디렉토리: {stats['cache_dir']}")

    print("\n" + "=" * 70)
    print("✅ 테스트 완료!")
    print("=" * 70)


if __name__ == "__main__":
    test_translation()
