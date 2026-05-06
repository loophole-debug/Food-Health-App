import os
import json
import asyncio
from vertexai.generative_models import GenerativeModel
import vertexai

class VertexAIService:
    def __init__(self):
        project_id = os.getenv("GCP_PROJECT_ID")
        vertexai.init(project=project_id, location="us-central1")
        self.model = GenerativeModel("gemini-2.0-flash-001")

    async def _generate_with_retry(self, prompt: str, system_instruction: str, max_attempts: int = 3) -> str:
        try:
            tokens_info = self.model.count_tokens(prompt)
            if tokens_info.total_tokens > 500:
                prompt = prompt[:2000]
        except Exception:
            pass

        model = GenerativeModel(
            "gemini-2.0-flash-001",
            system_instruction=[system_instruction]
        )
        
        attempt = 0
        while attempt < max_attempts:
            try:
                response = await model.generate_content_async(prompt)
                return response.text
            except Exception as e:
                attempt += 1
                if attempt == max_attempts:
                    raise e
                await asyncio.sleep(2 ** attempt)
        return ""

    async def generate_nudge(self, context: dict) -> str:
        prompt = f"User Context: {json.dumps(context)}"
        system_prompt = "You are a behavioral nutrition coach. Generate ONE micro-intervention (max 2 sentences, warm tone, no calorie mention, actionable within 2 minutes) based on the user context provided. Context includes time of day, mood, and behavioral patterns."
        return await self._generate_with_retry(prompt, system_prompt)

    async def analyze_food(self, description: str) -> dict:
        prompt = f"Food Description: {description}"
        system_prompt = "Analyze this food for: energy quality (not calories), mood impact, timing recommendation, and one surprising nutritional insight. Return JSON with keys: energy_quality, mood_impact, timing_tip, insight."
        
        try:
            text = await self._generate_with_retry(prompt, system_prompt)
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            return json.loads(text.strip())
        except Exception:
            return {
                "energy_quality": "Unknown energy quality.",
                "mood_impact": "Unknown mood impact.",
                "timing_tip": "Anytime.",
                "insight": "Listen to your body."
            }

    async def detect_pattern(self, events: list) -> str:
        prompt = f"Events: {json.dumps(events)}"
        system_prompt = "Given these behavioral events, identify ONE recurring pattern that predicts poor food choices. Be specific and empathetic. Max 2 sentences."
        return await self._generate_with_retry(prompt, system_prompt)

vertex_service = VertexAIService()
