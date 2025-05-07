from typing import Dict, List, Any
from agents.preference_agent import PreferenceAgent
from agents.content_agent import ContentAgent
from agents.recommendation_agent import RecommendationAgent

class AgentCoordinator:
    def __init__(
        self, 
        preference_agent: PreferenceAgent,
        content_agent: ContentAgent,
        recommendation_agent: RecommendationAgent
    ):
        self.preference_agent = preference_agent
        self.content_agent = content_agent
        self.recommendation_agent = recommendation_agent
        self.content_cache = {}  # Cache content search results
    
    async def set_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> None:
        """Set user preferences and invalidate any cached content"""
        await self.preference_agent.store_preferences(user_id, preferences)
        # Invalidate cache for this user
        if user_id in self.content_cache:
            del self.content_cache[user_id]
    
    async def has_preferences(self, user_id: int) -> bool:
        """Check if user has set preferences"""
        return await self.preference_agent.has_preferences(user_id)
    
    async def get_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Coordinate agents to get personalized recommendations"""
        # Step 1: Get user preferences
        preferences = await self.preference_agent.get_preferences(user_id)
        if not preferences:
            return []
        
        # Step 2: Analyze preferences using Gemini AI
        preference_analysis = await self.preference_agent.analyze_preferences(user_id)
        
        # Step 3: Check cache or search for content
        if user_id not in self.content_cache:
            # Build search query combining field and topic
            query = f"{preferences['topic']} {preferences['field']}"
            
            # Search for content from different sources
            videos = await self.content_agent.search_youtube_videos(query)
            articles = await self.content_agent.search_articles(query)
            
            # Combine results
            all_content = videos + articles
            self.content_cache[user_id] = all_content
        else:
            all_content = self.content_cache[user_id]
        
        # Step 4: Filter and rank content
        recommendations = await self.recommendation_agent.filter_and_rank(
            all_content, preferences, preference_analysis
        )
        
        # Return top recommendations (max 5)
        return recommendations[:5]