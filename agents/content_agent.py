import os
import json
import asyncio
from typing import Dict, List, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import aiohttp
from dotenv import load_dotenv

load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
SERP_API_KEY = os.getenv('SERP_API_KEY')

class ContentAgent:
    def __init__(self):
        self.youtube_service = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    async def search_youtube_videos(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for educational videos on YouTube"""
        try:
            # Create a task for asynchronous execution
            loop = asyncio.get_event_loop()
            search_response = await loop.run_in_executor(
                None,
                lambda: self.youtube_service.search().list(
                    q=query + " tutorial lecture",
                    part="snippet",
                    maxResults=max_results,
                    type="video",
                    videoEmbeddable="true",
                    order="relevance",
                    videoDefinition="high"
                ).execute()
            )
            
            # Check if we have results
            if not search_response.get('items'):
                print(f"No YouTube results found for query: {query}")
                return []
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get video details
            video_response = await loop.run_in_executor(
                None,
                lambda: self.youtube_service.videos().list(
                    part="contentDetails,snippet,statistics",
                    id=",".join(video_ids)
                ).execute()
            )
            
            results = []
            for item in video_response['items']:
                # Convert duration to minutes
                duration = item['contentDetails']['duration'].replace('PT', '')
                minutes = 0
                if 'H' in duration:
                    h, duration = duration.split('H')
                    minutes += int(h) * 60
                if 'M' in duration:
                    if 'S' in duration:
                        m, s = duration.split('M')
                        minutes += int(m)
                    else:
                        minutes += int(duration.replace('M', ''))
                
                results.append({
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'link': f"https://www.youtube.com/watch?v={item['id']}",
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'duration': f"{minutes} menit",
                    'views': item['statistics'].get('viewCount', '0'),
                    'source': 'youtube',
                    'type': 'video'
                })
                
            return results
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return []
    
    async def search_articles(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for educational articles using SERP API"""
        try:
            params = {
                "q": query + " tutorial guide",
                "api_key": SERP_API_KEY,
                "num": max_results,
                "engine": "google",
                "gl": "id",
                "hl": "id",
                "google_domain": "google.co.id",
                "safe": "active",
                "location": "Indonesia"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get("https://serpapi.com/search", params=params) as response:
                    data = await response.json()
                    
                    results = []
                    if 'organic_results' in data:
                        for item in data['organic_results'][:max_results]:
                            results.append({
                                'title': item['title'],
                                'description': item.get('snippet', ''),
                                'link': item['link'],
                                'source': 'web',
                                'type': 'article',
                                'duration': '10-15 menit'  # Estimated reading time
                            })
                    
                    return results
        except Exception as e:
            print(f"SERP API error: {e}")
            return []