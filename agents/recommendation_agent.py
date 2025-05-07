import os
from typing import Dict, List, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class RecommendationAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def filter_and_rank(
        self, 
        content: List[Dict[str, Any]], 
        preferences: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter and rank content based on user preferences and deliberative analysis"""
        if not content or not preferences:
            return []
        
        # First, basic filtering based on time constraints
        filtered_content = []
        study_hours = float(preferences.get('hours', 1)) * 60  # Convert to minutes
        
        for item in content:
            # Extract duration in minutes
            duration_str = item.get('duration', '0 menit')
            try:
                if 'menit' in duration_str:
                    duration = int(duration_str.split()[0])
                else:
                    duration = 10  # Default time for articles
                
                # Only include items that fit within the user's study time
                # For videos, include if they're less than 80% of available time
                if item['type'] == 'video' and duration <= (study_hours * 0.8):
                    filtered_content.append(item)
                # For articles, always include as they can be consumed in parts
                elif item['type'] == 'article':
                    filtered_content.append(item)
            except (ValueError, IndexError):
                filtered_content.append(item)  # Include if we can't parse duration
        
        if not filtered_content:
            return []
        
        # Use Gemini AI for deliberative ranking based on user preferences
        content_descriptions = "\n\n".join([
            f"Content {idx + 1}:\n- Title: {item['title']}\n- Description: {item['description'][:200]}...\n- Type: {item['type']}\n- Duration: {item['duration']}"
            for idx, item in enumerate(filtered_content[:10])  # Limit to 10 items for prompt size
        ])
        
        prompt = f"""
        As a learning content recommendation system, evaluate these content items for a student with these preferences:
        
        Student Profile:
        - Field of study: {preferences.get('field')}
        - Topic of interest: {preferences.get('topic')}
        - Available study time: {preferences.get('hours')} hours per day
        - Subtopics of interest: {', '.join(analysis.get('subtopics', []))}
        - Preferred complexity: {analysis.get('complexity', 'beginner')}
        
        Content to evaluate:
        {content_descriptions}
        
        Rank these content items from 1-5 (5 being most relevant) based on:
        1. Relevance to the student's topic and field
        2. Appropriateness of complexity level
        3. Efficiency given their time constraints
        4. Educational value
        
        Return ONLY a JSON array with objects containing content index (1-based) and score (1-5).
        Example: [{{"index": 1, "score": 4}}, {{"index": 2, "score": 5}}]
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            
            # Extract JSON from response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                scores = eval(json_str)  # Parse the JSON safely
                
                # Sort content based on scores
                scored_content = []
                for score_item in scores:
                    idx = score_item.get('index', 0) - 1  # Convert to 0-based
                    if 0 <= idx < len(filtered_content):
                        content_item = filtered_content[idx].copy()
                        content_item['score'] = score_item.get('score', 0)
                        scored_content.append(content_item)
                
                # Sort by score (highest first)
                sorted_content = sorted(scored_content, key=lambda x: x.get('score', 0), reverse=True)
                return sorted_content
            else:
                return filtered_content[:5]  # Return top 5 if parsing fails
        except Exception as e:
            print(f"Error ranking content: {e}")
            return filtered_content[:5]  # Return top 5 if analysis fails