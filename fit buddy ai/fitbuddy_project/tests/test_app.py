from fastapi.testclient import TestClient
from app.main import app


def test_home_and_docs():
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/docs").status_code == 200


def test_generate_plan_api_and_persistence():
    with TestClient(app) as client:
        payload = {"user_id": 101, "username": "Test User", "age": 25, "weight": 70, "goal": "build strength", "intensity": "medium"}
        response = client.post("/generate-plan", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert "workout_plan" in body and "nutrition_tip" in body
        assert "Day 1" in body["workout_plan"]
        assert client.get("/view-all-users").status_code == 200


def test_feedback_update():
    with TestClient(app) as client:
        payload = {"user_id": 102, "username": "Feedback User", "age": 30, "weight": 68, "goal": "general fitness", "intensity": "low"}
        client.post("/generate-plan", json=payload)
        response = client.post("/update-plan/102", json={"feedback": "add more cardio"})
        assert response.status_code == 200
        assert "updated_plan" in response.json()


def test_validation():
    with TestClient(app) as client:
        response = client.post("/generate-plan", json={"user_id": 0, "username": "", "age": 5, "weight": 10, "goal": "x", "intensity": "extreme"})
        assert response.status_code == 422
