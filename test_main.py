import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": "gemini-2.0-flash-001"}

@patch("firestore_service.FirestoreService.save_context", new_callable=AsyncMock)
def test_save_context(mock_save_context):
    mock_save_context.return_value = "fake_doc_id"
    response = client.post("/context", json={
        "user_id": "test_user",
        "time": "14:00",
        "mood": "happy",
        "location_type": "home"
    })
    assert response.status_code == 200
    assert response.json() == {"status": "success", "doc_id": "fake_doc_id"}

@patch("vertex_service.VertexAIService.generate_nudge", new_callable=AsyncMock)
@patch("firestore_service.FirestoreService.save_nudge", new_callable=AsyncMock)
def test_generate_nudge(mock_save_nudge, mock_generate_nudge):
    mock_generate_nudge.return_value = "This is a test nudge."
    mock_save_nudge.return_value = "nudge_id_123"
    
    response = client.post("/nudge", json={
        "user_id": "test_user",
        "context": {
            "time": "14:00",
            "mood": "happy",
            "location_type": "home"
        }
    })
    assert response.status_code == 200
    assert response.json() == {"nudge_text": "This is a test nudge."}

@patch("vertex_service.VertexAIService.analyze_food", new_callable=AsyncMock)
def test_analyze_food(mock_analyze_food):
    mock_analyze_food.return_value = {
        "energy_quality": "High",
        "mood_impact": "Positive",
        "timing_tip": "Good for morning",
        "insight": "Great test insight."
    }
    
    response = client.post("/food/analyze", json={
        "food_description": "Apple"
    })
    assert response.status_code == 200
    assert response.json() == {
        "energy_quality": "High",
        "mood_impact": "Positive",
        "timing_tip": "Good for morning",
        "insight": "Great test insight."
    }

@patch("firestore_service.FirestoreService.get_history", new_callable=AsyncMock)
def test_get_history(mock_get_history):
    mock_get_history.return_value = [{"id": "1", "nudge_text": "test"}]
    response = client.get("/history/test_user")
    assert response.status_code == 200
    assert response.json() == {"history": [{"id": "1", "nudge_text": "test"}]}

@patch("firestore_service.FirestoreService.save_preferences", new_callable=AsyncMock)
def test_save_preferences(mock_save_preferences):
    response = client.post("/preferences", json={
        "user_id": "test_user",
        "preferences": {"diet": "vegan"}
    })
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

@patch("firestore_service.FirestoreService.save_feedback", new_callable=AsyncMock)
def test_save_feedback(mock_save_feedback):
    response = client.post("/feedback", json={
        "nudge_id": "nudge_123",
        "helpful": True
    })
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
