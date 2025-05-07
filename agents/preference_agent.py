import os
import json
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class PreferenceAgent:
    def __init__(self):
        self.user_preferences = {}
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'user_data.json')
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Load existing user data if available
        self._load_user_data()
    
    def _load_user_data(self):
        """Load user preferences from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert user_id keys from strings back to integers
                    self.user_preferences = {int(k): v for k, v in data.items()}
            except Exception as e:
                print(f"Error loading user data: {e}")
                self.user_preferences = {}
    
    def _save_user_data(self):
        """Save user preferences to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    async def store_preferences(self, user_id: int, preferences: Dict[str, Any]) -> None:
        """Store user preferences and save to file"""
        self.user_preferences[user_id] = preferences
        self._save_user_data()
    
    async def get_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences"""
        return self.user_preferences.get(user_id, {})
    
    async def has_preferences(self, user_id: int) -> bool:
        """Check if user has preferences"""
        return user_id in self.user_preferences
    
    async def analyze_preferences(self, user_id: int) -> Dict[str, Any]:
        """Analyze user preferences using Gemini AI to extract more detailed interests"""
        preferences = await self.get_preferences(user_id)
        if not preferences:
            return {}
        
        prompt = f"""
        As a learning content recommendation system, analyze these user preferences:
        - Field of study: {preferences.get('field')}
        - Topic of interest: {preferences.get('topic')}
        - Available study time: {preferences.get('hours')} hours per day
        
        Based on this information, provide:
        1. Three specific subtopics they might be interested in
        2. Suitable content formats based on their available time
        3. The estimated complexity level (beginner, intermediate, advanced)
        
        Return the results in JSON format with keys: subtopics, formats, complexity
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            response_text = response.text
            
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                return analysis
            else:
                return {
                    "subtopics": [],
                    "formats": ["video", "article"],
                    "complexity": "beginner"
                }
        except Exception as e:
            print(f"Error analyzing preferences: {e}")
            return {
                "subtopics": [],
                "formats": ["video", "article"],
                "complexity": "beginner"
            }