"""
YouTube video information and transcript extraction tools.

This module provides functionality to:
- Extract video information (title, description, etc.)
- Get video transcripts/captions
- Parse YouTube URLs
"""

import logging
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL.

    Supports various YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID

    Args:
        url: YouTube URL

    Returns:
        Video ID or None if not found
    """
    patterns = [
        r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',  # Shorts
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def is_youtube_url(url: str) -> bool:
    """
    Check if a URL is a YouTube video URL.

    Args:
        url: URL to check

    Returns:
        True if it's a YouTube URL, False otherwise
    """
    return extract_video_id(url) is not None


def get_video_info(url: str) -> Dict[str, Any]:
    """
    Get YouTube video information and transcript.

    Args:
        url: YouTube video URL

    Returns:
        Dictionary with keys:
        - success: bool
        - video_id: str
        - title: str
        - description: str
        - transcript: str (if available)
        - duration: int (seconds)
        - error: str (if failed)
    """
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return {
                "success": False,
                "error": "Could not extract video ID from URL"
            }

        # Try to get video info using yt-dlp
        try:
            return _get_info_yt_dlp(video_id, url)
        except ImportError:
            logger.warning("yt-dlp not available, trying youtube-transcript-api only")
            return _get_info_transcript_api(video_id, url)

    except Exception as e:
        logger.error(f"Error getting YouTube video info: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _get_info_yt_dlp(video_id: str, url: str) -> Dict[str, Any]:
    """Get video info using yt-dlp (more comprehensive)."""
    try:
        import yt_dlp
    except ImportError:
        raise ImportError("Please install yt-dlp: pip install yt-dlp")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        result = {
            "success": True,
            "video_id": video_id,
            "title": info.get('title', 'Unknown'),
            "description": info.get('description', ''),
            "duration": info.get('duration', 0),
            "channel": info.get('channel', 'Unknown'),
            "upload_date": info.get('upload_date', ''),
        }

        # Try to get transcript
        try:
            transcript = _get_transcript(video_id)
            if transcript:
                result["transcript"] = transcript
        except Exception as e:
            logger.warning(f"Could not get transcript: {e}")
            result["transcript"] = None

        return result


def _get_info_transcript_api(video_id: str, url: str) -> Dict[str, Any]:
    """Get video info using youtube-transcript-api (transcript only)."""
    result = {
        "success": True,
        "video_id": video_id,
        "title": f"YouTube Video {video_id}",
        "description": "Video info not available (install yt-dlp for full details)",
    }

    try:
        transcript = _get_transcript(video_id)
        result["transcript"] = transcript
    except Exception as e:
        logger.error(f"Could not get transcript: {e}")
        result["transcript"] = None
        result["error"] = f"Could not retrieve transcript: {str(e)}"

    return result


def _get_transcript(video_id: str) -> Optional[str]:
    """
    Get video transcript using youtube-transcript-api.

    Args:
        video_id: YouTube video ID

    Returns:
        Transcript text or None if not available
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        raise ImportError(
            "Please install youtube-transcript-api: pip install youtube-transcript-api"
        )

    try:
        # Get transcript (tries to get English by default, falls back to auto-generated)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine all transcript entries
        full_transcript = ' '.join([entry['text'] for entry in transcript_list])

        return full_transcript

    except Exception as e:
        logger.warning(f"Could not get transcript for {video_id}: {e}")
        return None


def format_video_info(info: Dict[str, Any]) -> str:
    """
    Format video information into a readable string.

    Args:
        info: Video information dictionary

    Returns:
        Formatted string
    """
    if not info.get("success"):
        return f"Error: {info.get('error', 'Unknown error')}"

    lines = [
        f"**YouTube Video: {info['title']}**",
        f"Video ID: {info['video_id']}",
    ]

    if info.get('channel'):
        lines.append(f"Channel: {info['channel']}")

    if info.get('duration'):
        minutes = info['duration'] // 60
        seconds = info['duration'] % 60
        lines.append(f"Duration: {minutes}m {seconds}s")

    if info.get('description'):
        desc = info['description']
        if len(desc) > 300:
            desc = desc[:300] + "..."
        lines.append(f"\nDescription:\n{desc}")

    if info.get('transcript'):
        transcript = info['transcript']
        if len(transcript) > 2000:
            transcript = transcript[:2000] + "\n\n[Transcript truncated...]"
        lines.append(f"\nTranscript:\n{transcript}")
    else:
        lines.append("\nTranscript: Not available")

    return '\n'.join(lines)
