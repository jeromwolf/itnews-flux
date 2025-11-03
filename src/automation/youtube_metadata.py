"""
YouTube metadata generator for Tech News Digest.

Generates optimized metadata for YouTube uploads:
- SEO-friendly titles
- Comprehensive descriptions
- Relevant tags
"""

from datetime import datetime
from typing import Optional

from src.video.models import VideoProject


def generate_youtube_metadata(project: VideoProject) -> dict[str, any]:
    """
    Generate YouTube metadata for a video project.

    Args:
        project: Video project

    Returns:
        Dictionary with title, description, tags
    """
    # Extract topics from segments
    topics = [segment.title for segment in project.segments]

    # Generate title
    title = generate_title(topics, project.created_at)

    # Generate description
    description = generate_description(topics, project)

    # Generate tags
    tags = generate_tags(topics)

    return {
        "title": title,
        "description": description,
        "tags": tags,
        "category_id": "28",  # Science & Technology
        "privacy_status": "public",
    }


def generate_title(topics: list[str], date: datetime) -> str:
    """
    Generate SEO-friendly YouTube title with high CTR potential.

    Strategy:
    - Start with curiosity/urgency keywords
    - Include brand name at the end
    - Use power words and numbers
    - Keep under 60 characters for mobile display

    Args:
        topics: List of news topics
        date: Video date

    Returns:
        YouTube title (max 100 characters, optimized for ~60)
    """
    date_str = date.strftime("%m/%d")

    # Power words for CTR
    power_starters = ["🔥", "⚡️", "🚨", "💥", "🎯", "📢"]

    # Use first topic as main title with power word
    if topics:
        main_topic = topics[0]

        # Extract key phrase (first 2-3 words or up to 30 chars)
        words = main_topic.split()
        if len(words) > 3:
            key_phrase = " ".join(words[:3])
        else:
            key_phrase = main_topic

        # Shorten if too long
        if len(key_phrase) > 35:
            key_phrase = key_phrase[:32] + "..."

        # Create compelling title with power word
        import random
        power_word = random.choice(power_starters)

        # Format: [Power] Main Topic + More | Brand | Date
        if len(topics) > 1:
            title = f"{power_word} {key_phrase} 외 {len(topics)-1}건 | AI ON 톡톡 {date_str}"
        else:
            title = f"{power_word} {key_phrase} | AI ON 톡톡 {date_str}"
    else:
        title = f"🔥 오늘의 AI 뉴스 | AI ON 톡톡 {date_str}"

    # Ensure max 100 characters (YouTube limit)
    if len(title) > 100:
        title = title[:97] + "..."

    return title


def generate_description(topics: list[str], project: VideoProject) -> str:
    """
    Generate comprehensive YouTube description with SEO optimization.

    Strategy:
    - Start with hook (first 2-3 lines appear in search)
    - Include timestamps (YouTube loves them)
    - Add clear CTAs (subscribe, like, comment)
    - Use relevant keywords naturally
    - Add hashtags at the end

    Args:
        topics: List of news topics
        project: Video project

    Returns:
        YouTube description
    """
    date_str = project.created_at.strftime("%Y년 %m월 %d일")
    date_short = project.created_at.strftime("%m월 %d일")

    # Build topics list with emojis
    topic_emojis = ["🔥", "⚡️", "💡", "🚀", "🎯"]
    topics_text = ""
    for i, topic in enumerate(topics, 1):
        emoji = topic_emojis[i % len(topic_emojis)]
        topics_text += f"{emoji} {topic}\n"

    # Calculate approximate timestamps (assuming ~60s per segment + 20s intro/outro)
    timestamps = "\n⏱️ 타임스탬프 (Timestamps):\n"
    timestamps += "00:00 인트로\n"
    current_time = 20
    for i, topic in enumerate(topics, 1):
        minutes = current_time // 60
        seconds = current_time % 60
        timestamps += f"{minutes:02d}:{seconds:02d} 뉴스 {i} - {topic[:40]}{'...' if len(topic) > 40 else ''}\n"
        current_time += 60

    description = f"""오늘의 핫한 AI·테크 뉴스를 3분 안에! | {date_short} AI ON 톡톡 📡

{date_str}의 꼭 알아야 할 IT 뉴스를 빠르게 정리했습니다.
매일 아침 가장 중요한 AI와 기술 소식을 전해드립니다!

━━━━━━━━━━━━━━━━━━━━

📰 오늘의 주요 뉴스:
{topics_text}
━━━━━━━━━━━━━━━━━━━━
{timestamps}
━━━━━━━━━━━━━━━━━━━━

💼 이런 분들께 추천합니다:
✅ 바쁜 직장인 (출퇴근길 3분 브리핑)
✅ IT 업계 종사자 (최신 트렌드 파악)
✅ 스타트업 창업자 (시장 동향 체크)
✅ 개발자·기획자 (기술 뉴스 습득)
✅ 투자자 (테크 산업 인사이트)

━━━━━━━━━━━━━━━━━━━━

🎙️ AI ON, 톡톡이란?
매일 아침 7시, AI가 전 세계 IT 뉴스를 선별하고 요약해 전달합니다.
복잡한 기술 뉴스를 쉽고 빠르게! 출근길 3분이면 충분합니다.

━━━━━━━━━━━━━━━━━━━━

🔔 구독하고 알림 설정하면:
• 매일 아침 7시 새로운 뉴스 업데이트
• AI, 클라우드, 보안, 스타트업 등 다양한 분야
• 전문가처럼 대화할 수 있는 IT 지식
• 커리어에 도움되는 테크 인사이트

👍 좋아요와 댓글로 더 알고 싶은 뉴스를 알려주세요!
💬 어떤 주제가 궁금하신가요? 댓글로 의견 남겨주세요.

━━━━━━━━━━━━━━━━━━━━

📺 AI ON 채널:
🎬 YouTube: @aion-vibecoding
📧 문의: aion-vibecoding@youtube.com

━━━━━━━━━━━━━━━━━━━━

#AI뉴스 #기술뉴스 #IT뉴스 #인공지능 #ChatGPT #테크트렌드 #스타트업뉴스 #개발자뉴스 #클라우드 #사이버보안 #빅테크 #실리콘밸리 #한국IT #글로벌테크 #AION #톡톡 #TechNews #AINews #TechBrief
"""

    return description


def generate_tags(topics: list[str]) -> list[str]:
    """
    Generate relevant YouTube tags with SEO optimization.

    Strategy:
    - Mix broad and specific tags
    - Include trending keywords
    - Add long-tail keywords (3-4 words)
    - Balance Korean and English tags
    - Keep under 500 characters total

    Args:
        topics: List of news topics

    Returns:
        List of tags (optimized for discovery)
    """
    # High-priority brand and category tags
    priority_tags = [
        "AI ON",
        "톡톡",
        "AI ON 톡톡",
    ]

    # Broad category tags (high search volume)
    broad_tags = [
        "AI뉴스",
        "기술뉴스",
        "IT뉴스",
        "테크뉴스",
        "인공지능뉴스",
        "tech news",
        "AI news",
        "technology news",
        "IT news Korea",
    ]

    # Medium-specific tags (moderate competition)
    medium_tags = [
        "ChatGPT",
        "OpenAI",
        "구글AI",
        "테크브리핑",
        "기술트렌드",
        "스타트업뉴스",
        "빅테크",
        "실리콘밸리",
        "개발자뉴스",
        "프로그래머",
        "tech brief",
        "daily tech news",
        "tech trends",
        "AI trends",
        "startup news",
    ]

    # Long-tail keywords (low competition, high intent)
    longtail_tags = [
        "출퇴근길 뉴스",
        "3분 IT뉴스",
        "매일 아침 뉴스",
        "직장인 뉴스",
        "아침 기술뉴스",
        "IT업계 뉴스",
        "한국 IT뉴스",
        "morning tech news",
        "quick tech update",
        "daily AI update",
        "tech news for developers",
        "Korean tech news",
    ]

    # Extract keywords from topics
    topic_keywords = []
    stop_words = {"with", "from", "that", "this", "will", "have", "been", "were", "their"}

    for topic in topics:
        # Clean and split
        words = topic.lower().replace(",", "").replace(".", "").split()
        # Get significant words (length > 3, not stop words)
        keywords = [
            w for w in words
            if len(w) > 3 and w not in stop_words and not w.isdigit()
        ]
        # Add top 2 keywords per topic
        topic_keywords.extend(keywords[:2])

    # Combine all tags (priority first)
    all_tags = priority_tags + broad_tags + medium_tags + longtail_tags + topic_keywords

    # Deduplicate while preserving order
    unique_tags = []
    seen = set()
    total_chars = 0

    for tag in all_tags:
        tag_lower = tag.lower()
        # Check character limit (YouTube: 500 chars total)
        if tag_lower not in seen and total_chars + len(tag) + 1 < 480:  # Leave buffer
            unique_tags.append(tag)
            seen.add(tag_lower)
            total_chars += len(tag) + 1  # +1 for comma separator

    # YouTube recommends 5-15 tags, but allows up to 500 chars
    # We'll use ~30-40 tags for maximum coverage
    return unique_tags[:40]


def format_metadata_for_display(metadata: dict[str, any]) -> str:
    """
    Format metadata for display in UI.

    Args:
        metadata: YouTube metadata dictionary

    Returns:
        Formatted string for display
    """
    tags_str = ", ".join(metadata["tags"][:20])  # First 20 tags
    if len(metadata["tags"]) > 20:
        tags_str += f" ... (+{len(metadata['tags']) - 20} more)"

    formatted = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 YOUTUBE METADATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 TITLE:
{metadata['title']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 DESCRIPTION:
{metadata['description']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏷️  TAGS ({len(metadata['tags'])}):
{tags_str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️  SETTINGS:
Category: Science & Technology (28)
Privacy: {metadata['privacy_status'].upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    return formatted
