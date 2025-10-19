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
    Generate SEO-friendly YouTube title.

    Args:
        topics: List of news topics
        date: Video date

    Returns:
        YouTube title (max 100 characters)
    """
    date_str = date.strftime("%Y.%m.%d")

    # Use first topic as main title
    if topics:
        main_topic = topics[0]
        # Shorten if too long
        if len(main_topic) > 50:
            main_topic = main_topic[:47] + "..."

        title = f"AI ON - {main_topic} | Tech News {date_str}"
    else:
        title = f"AI ON - Daily Tech News Digest | {date_str}"

    # Ensure max 100 characters
    if len(title) > 100:
        title = title[:97] + "..."

    return title


def generate_description(topics: list[str], project: VideoProject) -> str:
    """
    Generate comprehensive YouTube description.

    Args:
        topics: List of news topics
        project: Video project

    Returns:
        YouTube description
    """
    date_str = project.created_at.strftime("%Y년 %m월 %d일")

    # Build topics list
    topics_text = ""
    for i, topic in enumerate(topics, 1):
        topics_text += f"{i}. {topic}\n"

    description = f"""🤖 AI ON - Your Daily Tech Intelligence

📅 {date_str} Tech News Digest

오늘의 주요 IT 뉴스를 영어와 한국어로 전합니다!
Today's top IT news in English and Korean!

📰 Today's Topics:
{topics_text}

━━━━━━━━━━━━━━━━━━━━

🎯 Perfect for:
✅ IT professionals learning English
✅ Tech enthusiasts staying updated
✅ Korean speakers interested in global tech trends
✅ English learners in the tech industry

━━━━━━━━━━━━━━━━━━━━

💡 About AI ON:
AI ON delivers daily tech news in a bilingual format, helping you stay informed while improving your English skills. Our content is automatically generated using cutting-edge AI technology, ensuring fresh news every day.

━━━━━━━━━━━━━━━━━━━━

📺 Subscribe for:
• Daily tech news updates
• AI and technology trends
• Bilingual content (English + Korean)
• Clear explanations of complex tech topics

━━━━━━━━━━━━━━━━━━━━

🔗 Follow AI ON:
YouTube: @aion-vibecoding

━━━━━━━━━━━━━━━━━━━━

#TechNews #AI #Technology #IT #EnglishLearning #한국어 #기술뉴스 #인공지능 #AION #DailyNews #TechDigest #Innovation #Startups #SoftwareDevelopment
"""

    return description


def generate_tags(topics: list[str]) -> list[str]:
    """
    Generate relevant YouTube tags.

    Args:
        topics: List of news topics

    Returns:
        List of tags
    """
    # Base tags
    base_tags = [
        "AI ON",
        "tech news",
        "technology",
        "IT news",
        "daily tech",
        "AI",
        "artificial intelligence",
        "english learning",
        "한국어",
        "기술 뉴스",
        "tech digest",
        "innovation",
        "startups",
        "software",
        "hardware",
        "cloud computing",
        "cybersecurity",
    ]

    # Extract keywords from topics
    topic_keywords = []
    for topic in topics:
        # Simple keyword extraction (split and filter)
        words = topic.lower().split()
        # Get significant words (length > 3)
        keywords = [w for w in words if len(w) > 3 and w not in ["with", "from", "that", "this", "will", "have"]]
        topic_keywords.extend(keywords[:3])  # Top 3 keywords per topic

    # Combine and deduplicate
    all_tags = base_tags + topic_keywords
    unique_tags = []
    seen = set()
    for tag in all_tags:
        tag_lower = tag.lower()
        if tag_lower not in seen:
            unique_tags.append(tag)
            seen.add(tag_lower)

    # YouTube allows max 500 characters for tags, ~30-50 tags
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
