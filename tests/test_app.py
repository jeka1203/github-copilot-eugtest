import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data

def test_signup_for_activity():
    email = "testuser@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    # Teilnehmer sollte jetzt in der Liste sein
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]

def test_unregister_participant():
    email = "testuser@mergington.edu"
    # Erst anmelden, falls nicht vorhanden
    client.post(f"/activities/Chess Club/signup?email={email}")
    # Dann entfernen
    response = client.post(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["success"] is True
    # Teilnehmer sollte jetzt entfernt sein
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]
