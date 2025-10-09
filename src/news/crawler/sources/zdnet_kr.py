"""
ZDNet Korea (zdnet.co.kr) 뉴스 크롤러.

ZDNet Korea는 글로벌 IT 미디어 ZDNet의 한국 버전으로,
IT, 테크, 디지털 뉴스를 제공하는 전문 매체입니다.
기업 IT, 클라우드, 보안, 모바일 등 다양한 IT 분야를 다룹니다.

RSS Feed: https://www.zdnet.co.kr/rss/allNews.xml
"""

import re
from typing import Optional

import feedparser

from src.news.crawler.base_crawler import BaseCrawler, ParseError
from src.news.models import News, NewsCategory, NewsImportance, NewsSource


class ZDNetKoreaCrawler(BaseCrawler):
    """
    ZDNet Korea 뉴스 크롤러.

    ZDNet Korea RSS 피드에서 뉴스를 가져와서 파싱합니다.
    """

    def __init__(self):
        """ZDNet Korea 크롤러 초기화."""
        super().__init__(
            source=NewsSource.ZDNET_KR,
            rss_url="https://www.zdnet.co.kr/rss/allNews.xml",
        )

    def parse_article(self, entry: feedparser.FeedParserDict) -> Optional[News]:
        """
        ZDNet Korea RSS entry를 파싱하여 News 객체로 변환합니다.

        Args:
            entry: RSS feed entry

        Returns:
            파싱된 News 객체, 실패 시 None

        Raises:
            ParseError: 필수 필드가 없을 경우
        """
        try:
            # 기본 필드 추출
            title = entry.get("title", "").strip()
            url = entry.get("link", "").strip()

            if not title or not url:
                raise ParseError("제목 또는 URL이 없습니다")

            # 요약 추출
            summary = entry.get("summary", "")
            if summary:
                summary = self._extract_text(summary, max_length=500)

            # 본문 추출 (가능한 경우)
            content = None
            if "content" in entry and entry.content:
                content = self._extract_text(entry.content[0].value, max_length=2000)

            # 저자 추출
            author = entry.get("author", None)
            if not author and "authors" in entry and entry.authors:
                author = entry.authors[0].get("name")

            # 이미지 추출
            image_url = None
            thumbnail_url = None

            # media:content 시도
            if "media_content" in entry and entry.media_content:
                image_url = entry.media_content[0].get("url")

            # media:thumbnail 시도
            if "media_thumbnail" in entry and entry.media_thumbnail:
                thumbnail_url = entry.media_thumbnail[0].get("url")

            # 발행일 파싱
            published_at = self._parse_publish_date(entry)

            # 카테고리 결정
            category = self._get_category(entry, title, summary)

            # 중요도 결정
            importance = self._get_importance(entry, title)

            # 단어 수 계산
            text_for_count = content or summary or ""
            word_count = len(text_for_count)  # 한글은 글자 수로 계산
            reading_time = self._estimate_reading_time(word_count)

            # News 객체 생성
            news = News(
                title=title,
                url=url,
                source=self.source,
                summary=summary,
                content=content,
                category=category,
                importance=importance,
                published_at=published_at,
                author=author,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                word_count=word_count,
                reading_time=reading_time,
            )

            self.logger.debug(
                f"파싱 완료: {title[:30]}...",
                extra={
                    "category": category.value,
                    "importance": importance.value,
                },
            )

            return news

        except ParseError:
            raise

        except Exception as e:
            raise ParseError(f"ZDNet Korea entry 파싱 실패: {e}") from e

    def _get_category(
        self,
        entry: feedparser.FeedParserDict,
        title: str,
        summary: str,
    ) -> NewsCategory:
        """
        ZDNet Korea 특화 로직으로 기사 카테고리를 결정합니다.

        Args:
            entry: RSS feed entry
            title: 기사 제목
            summary: 기사 요약

        Returns:
            기사 카테고리
        """
        # 제목과 요약을 합쳐서 분석
        text = f"{title} {summary}".lower()

        # RSS 카테고리/태그 확인
        if "tags" in entry:
            tags = [tag.get("term", "").lower() for tag in entry.tags]

            # AI/ML
            if any(tag in ["ai", "인공지능", "머신러닝", "딥러닝"] for tag in tags):
                return NewsCategory.AI_ML

            # 보안
            if any(tag in ["보안", "사이버보안", "정보보호", "security"] for tag in tags):
                return NewsCategory.SECURITY

            # 클라우드/소프트웨어
            if any(tag in ["클라우드", "소프트웨어", "sw", "cloud", "saas"] for tag in tags):
                return NewsCategory.SOFTWARE_CLOUD

        # 키워드 기반 탐지
        # AI/ML 키워드
        ai_keywords = [
            "인공지능",
            "ai",
            "머신러닝",
            "딥러닝",
            "챗gpt",
            "chatgpt",
            "생성형 ai",
            "llm",
            "대규모 언어모델",
            "claude",
            "gemini",
        ]
        if any(keyword in text for keyword in ai_keywords):
            return NewsCategory.AI_ML

        # 스타트업/투자 키워드
        startup_keywords = [
            "투자",
            "시리즈",
            "스타트업",
            "유니콘",
            "벤처",
            "vc",
            "펀딩",
            "자금 조달",
        ]
        if any(keyword in text for keyword in startup_keywords):
            return NewsCategory.STARTUP_FUNDING

        # 보안 키워드
        security_keywords = [
            "보안",
            "해킹",
            "사이버",
            "정보보호",
            "암호화",
            "취약점",
            "랜섬웨어",
            "피싱",
            "데이터 유출",
        ]
        if any(keyword in text for keyword in security_keywords):
            return NewsCategory.SECURITY

        # 클라우드/소프트웨어 키워드
        cloud_keywords = [
            "클라우드",
            "aws",
            "애저",
            "azure",
            "구글 클라우드",
            "gcp",
            "saas",
            "플랫폼",
            "api",
            "소프트웨어",
            "erp",
        ]
        if any(keyword in text for keyword in cloud_keywords):
            return NewsCategory.SOFTWARE_CLOUD

        # 모바일 키워드
        mobile_keywords = [
            "아이폰",
            "갤럭시",
            "안드로이드",
            "ios",
            "모바일",
            "스마트폰",
            "태블릿",
            "앱",
        ]
        if any(keyword in text for keyword in mobile_keywords):
            return NewsCategory.MOBILE

        # 하드웨어 키워드
        hardware_keywords = [
            "반도체",
            "칩",
            "프로세서",
            "cpu",
            "gpu",
            "디스플레이",
            "배터리",
            "센서",
        ]
        if any(keyword in text for keyword in hardware_keywords):
            return NewsCategory.HARDWARE

        # 기본값: 일반 기술
        return NewsCategory.TECH_GENERAL

    def _get_importance(
        self,
        entry: feedparser.FeedParserDict,
        title: str,
    ) -> NewsImportance:
        """
        ZDNet Korea 기사의 중요도를 결정합니다.

        Args:
            entry: RSS feed entry
            title: 기사 제목

        Returns:
            기사 중요도
        """
        title_lower = title.lower()

        # 속보 지표
        breaking_keywords = [
            "속보",
            "긴급",
            "단독",
            "특종",
            "breaking",
        ]
        if any(keyword in title_lower for keyword in breaking_keywords):
            return NewsImportance.BREAKING

        # 주요 뉴스 지표 (대기업, 주요 IT 기업)
        major_keywords = [
            "삼성",
            "sk",
            "lg",
            "네이버",
            "카카오",
            "구글",
            "google",
            "애플",
            "apple",
            "마이크로소프트",
            "microsoft",
            "아마존",
            "amazon",
            "메타",
            "meta",
            "openai",
            "발표",
            "출시",
            "인수",
            "합병",
        ]
        if any(keyword in title_lower for keyword in major_keywords):
            return NewsImportance.MAJOR

        # 대규모 투자 금액 확인
        funding_pattern = r"(\d+)억|(\d+)조"
        match = re.search(funding_pattern, title_lower)
        if match:
            if match.group(2):  # 조 단위
                return NewsImportance.MAJOR
            elif match.group(1):  # 억 단위
                amount = int(match.group(1))
                if amount >= 100:  # 100억 이상
                    return NewsImportance.MAJOR

        return NewsImportance.NORMAL


# 편의 함수
def create_zdnet_kr_crawler() -> ZDNetKoreaCrawler:
    """
    ZDNet Korea 크롤러 인스턴스를 생성합니다.

    Returns:
        ZDNet Korea 크롤러

    Example:
        >>> crawler = create_zdnet_kr_crawler()
        >>> news = crawler.fetch_news(limit=10)
        >>> print(f"가져온 기사: {news.total}개")
    """
    return ZDNetKoreaCrawler()
