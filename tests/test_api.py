"""
API endpoint tests for Mergington High School Activities API.
Uses the Arrange-Act-Assert (AAA) pattern for clear test structure:
  - Arrange: Set up test data and preconditions
  - Act: Execute the action being tested
  - Assert: Verify the results and side effects
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """
        Verify that GET / redirects to /static/index.html
        
        Arrange: Client is ready (via fixture)
        Act: Make GET request to /
        Assert: Response is redirect (307) to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "location" in response.headers
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all(self, client, sample_activities):
        """
        Verify that GET /activities returns all activities
        
        Arrange: Sample activities loaded via fixture
        Act: Make GET request to /activities
        Assert: Response contains all activities with correct structure
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == len(sample_activities)
        for activity_name in sample_activities:
            assert activity_name in data
    
    def test_get_activities_includes_participant_details(self, client):
        """
        Verify that each activity includes required fields including participants
        
        Arrange: Client ready with sample activities
        Act: Make GET request to /activities
        Assert: Each activity has description, schedule, max_participants, participants
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_with_no_participants(self, client, monkeypatch):
        """
        Verify that activity with empty participant list is handled correctly
        
        Arrange: Create activity with empty participants list
        Act: Make GET request to /activities
        Assert: Empty activity returns successfully
        """
        # Arrange
        from src import app
        test_activities = {
            "Empty Activity": {
                "description": "Test activity",
                "schedule": "Test time",
                "max_participants": 10,
                "participants": []
            }
        }
        monkeypatch.setattr("src.app.activities", test_activities)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert data["Empty Activity"]["participants"] == []


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """
        Verify successful student signup for an activity
        
        Arrange: Activity exists with known current participants
        Act: POST request to signup with valid activity and email
        Assert: Status 200, participant added to list, count incremented
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Check response
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in response.json()["message"]
        
        # Assert - Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_email_fails(self, client):
        """
        Verify that duplicate signup returns error
        
        Arrange: Student already registered for activity
        Act: POST request to signup same student again
        Assert: Status 400 with descriptive error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_invalid_activity_fails(self, client):
        """
        Verify that signup for non-existent activity returns error
        
        Arrange: Activity name doesn't exist
        Act: POST request to signup for invalid activity
        Assert: Status 404 with descriptive error message
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_increments_participant_count(self, client):
        """
        Verify that participant count increases after signup
        
        Arrange: Track initial participant count
        Act: Add new participant
        Assert: Count incremented by exactly 1
        """
        # Arrange
        activity_name = "Programming Class"
        email = "newprogrammer@mergington.edu"
        
        # Get initial count
        initial_data = client.get("/activities").json()
        initial_count = len(initial_data[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        updated_data = client.get("/activities").json()
        updated_count = len(updated_data[activity_name]["participants"])
        assert updated_count == initial_count + 1


class TestRemoveEndpoint:
    """Tests for POST /activities/{activity_name}/remove endpoint"""
    
    def test_remove_success(self, client):
        """
        Verify successful removal of participant from activity
        
        Arrange: Activity exists with participant to remove
        Act: POST request to remove with valid activity and email
        Assert: Status 200, participant removed, count decremented
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Known participant
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert - Check response
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in response.json()["message"]
        
        # Assert - Verify participant was removed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]
    
    def test_remove_nonexistent_participant_fails(self, client):
        """
        Verify that removing non-existent participant returns error
        
        Arrange: Email not registered for activity
        Act: POST request to remove participant not in list
        Assert: Status 404 with descriptive error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notaparticipant@mergington.edu"  # Not in participants
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_invalid_activity_fails(self, client):
        """
        Verify that remove from non-existent activity returns error
        
        Arrange: Activity name doesn't exist
        Act: POST request to remove from invalid activity
        Assert: Status 404 with descriptive error message
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_decrements_participant_count(self, client):
        """
        Verify that participant count decreases after removal
        
        Arrange: Track initial participant count
        Act: Remove a participant
        Assert: Count decremented by exactly 1
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Known participant
        
        # Get initial count
        initial_data = client.get("/activities").json()
        initial_count = len(initial_data[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        updated_data = client.get("/activities").json()
        updated_count = len(updated_data[activity_name]["participants"])
        assert updated_count == initial_count - 1
