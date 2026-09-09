"""
Pytest configuration and shared fixtures for API tests.
Provides isolated test data and FastAPI TestClient.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def sample_activities():
    """
    Fixture: Returns a fresh copy of sample activities data for each test.
    This ensures test isolation and prevents cross-test contamination.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }


@pytest.fixture
def client(monkeypatch, sample_activities):
    """
    Fixture: Provides a TestClient with isolated test data.
    Uses monkeypatch to replace the app's activities dict with fresh test data
    for each test, ensuring no state carries over between tests.
    """
    # Replace the app's activities with isolated test data
    monkeypatch.setattr("src.app.activities", sample_activities)
    
    # Return TestClient for making requests
    return TestClient(app)
