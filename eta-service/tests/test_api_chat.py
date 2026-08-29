import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_eta_inquiry():
    """Test /api/v1/chat endpoint for ETA inquiry."""
    payload = {
        "device_id": "test_pilgrim_chat_01",
        "message": "When will I reach the temple?",
        "current_location": {"lat": 19.9975, "lng": 73.7898},
        "destination": {"lat": 19.9956, "lng": 73.7810},
        "crowd_density_index": 0.5,
        "is_festival": True,
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["intent"] == "eta_inquiry"
    assert "arrival time" in data["reply"].lower()
    assert data["eta_summary"] is not None


def test_chat_queue_inquiry():
    """Test /api/v1/chat endpoint for temple queue inquiry."""
    payload = {
        "device_id": "test_pilgrim_chat_02",
        "message": "How long is the darshan queue wait time?",
        "crowd_density_index": 0.8,
        "is_festival": True,
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["intent"] == "queue_inquiry"
    assert "queue waiting time" in data["reply"].lower()


def test_chat_departure_advice():
    """Test /api/v1/chat endpoint for departure advice."""
    payload = {
        "device_id": "test_pilgrim_chat_03",
        "message": "What is the best time to leave to avoid traffic?",
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["intent"] == "departure_advice"
    assert "recommendations" in data
