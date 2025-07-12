from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url: str) -> str:
    import re
    match = re.search(r"v=([\w-]+)", url)
    return match.group(1) if match else None

def get_transcript(video_id: str, language: str = 'en') -> str:
    response = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    return " ".join([entry['text'] for entry in response])