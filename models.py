from pydantic import BaseModel
from typing import Dict, Any

class ContextInput(BaseModel):
    user_id: str
    time: str
    mood: str
    location_type: str

class NudgeRequest(BaseModel):
    user_id: str
    context: Dict[str, Any]

class NudgeResponse(BaseModel):
    nudge_text: str

class FoodAnalyzeRequest(BaseModel):
    food_description: str

class FoodAnalyzeResponse(BaseModel):
    energy_quality: str
    mood_impact: str
    timing_tip: str
    insight: str

class PreferencesInput(BaseModel):
    user_id: str
    preferences: Dict[str, Any]

class FeedbackInput(BaseModel):
    nudge_id: str
    helpful: bool
