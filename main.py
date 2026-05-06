import os
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import logging as cloud_logging

from models import (
    ContextInput, NudgeRequest, NudgeResponse, FoodAnalyzeRequest,
    FoodAnalyzeResponse, PreferencesInput, FeedbackInput
)
from firestore_service import firestore_service
from vertex_service import vertex_service

try:
    client = cloud_logging.Client(project=os.getenv("GCP_PROJECT_ID"))
    client.setup_logging()
except Exception:
    pass
import logging
logger = logging.getLogger("nutrisense")

app = FastAPI(title="NutriSense Context Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return Response(content='{"detail": "Internal server error"}', status_code=500, media_type="application/json")

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/health")
async def health():
    return {"status": "ok", "model": "gemini-2.0-flash-001"}

@app.post("/context")
async def save_context(data: ContextInput):
    try:
        doc_id = await firestore_service.save_context(data.user_id, data.model_dump())
        return {"status": "success", "doc_id": doc_id}
    except Exception as e:
        logger.error(f"Error saving context: {e}")
        raise HTTPException(status_code=500, detail="Error saving context")

@app.post("/nudge", response_model=NudgeResponse)
async def generate_nudge(req: NudgeRequest):
    try:
        nudge_text = await vertex_service.generate_nudge(req.context)
    except Exception as e:
        logger.error(f"Vertex AI error: {e}")
        nudge_text = "Take a moment to breathe and listen to what your body really needs right now."
        
    try:
        await firestore_service.save_nudge(req.user_id, nudge_text, req.context)
    except Exception as e:
        logger.error(f"Firestore error: {e}")
        
    return NudgeResponse(nudge_text=nudge_text)

@app.post("/food/analyze", response_model=FoodAnalyzeResponse)
async def analyze_food(req: FoodAnalyzeRequest):
    try:
        insight_data = await vertex_service.analyze_food(req.food_description)
        return FoodAnalyzeResponse(**insight_data)
    except Exception as e:
        logger.error(f"Food analyze error: {e}")
        return FoodAnalyzeResponse(
            energy_quality="Unknown",
            mood_impact="Unknown",
            timing_tip="Unknown",
            insight="We could not analyze this food right now."
        )

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    try:
        history = await firestore_service.get_history(user_id, limit=10)
        return {"history": history}
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving history")

@app.post("/preferences")
async def save_preferences(req: PreferencesInput):
    try:
        await firestore_service.save_preferences(req.user_id, req.preferences)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Preferences error: {e}")
        raise HTTPException(status_code=500, detail="Error saving preferences")

@app.post("/feedback")
async def save_feedback(req: FeedbackInput):
    try:
        await firestore_service.save_feedback(req.nudge_id, req.helpful)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail="Error saving feedback")
