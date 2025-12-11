"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to known state before each test"""
    # Store original state - deep copy to preserve exact structure
    original = copy.deepcopy(activities)
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(copy.deepcopy(original))


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_data(self, client):
        """Test that get_activities returns activity data"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_get_activities_includes_programming_class(self, client):
        """Test that Programming Class is available"""
        response = client.get("/activities")
        data = response.json()
        assert "Programming Class" in data
    
    def test_get_activities_includes_activity_details(self, client):
        """Test that activities include required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Programming Class"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_includes_participants(self, client):
        """Test that activities include participant list"""
        response = client.get("/activities")
        data = response.json()
        
        # Programming Class should have participants
        assert len(data["Programming Class"]["participants"]) > 0
        assert isinstance(data["Programming Class"]["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student(self, client, reset_activities):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "newemail@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
    
    def test_signup_new_student_updates_participants(self, client, reset_activities):
        """Test that signup actually adds the student to participants"""
        email = "newstudent@mergington.edu"
        client.post("/activities/Gym%20Class/signup", params={"email": email})
        
        # Verify student was added
        response = client.get("/activities")
        assert email in response.json()["Gym Class"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        email = "emma@mergington.edu"  # Already in Programming Class
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test that multiple students can sign up for the same activity"""
        emails = ["test1@mergington.edu", "test2@mergington.edu", "test3@mergington.edu"]
        
        for email in emails:
            response = client.post("/activities/Gym%20Class/signup", params={"email": email})
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        participants = response.json()["Gym Class"]["participants"]
        for email in emails:
            assert email in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_student(self, client, reset_activities):
        """Test removing a student from an activity"""
        email = "emma@mergington.edu"  # Already in Programming Class
        response = client.delete(
            "/activities/Programming%20Class/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_student(self, client, reset_activities):
        """Test that unregister actually removes the student"""
        email = "john@mergington.edu"  # In Gym Class
        client.delete(
            "/activities/Gym%20Class/unregister",
            params={"email": email}
        )
        
        # Verify student was removed
        response = client.get("/activities")
        assert email not in response.json()["Gym Class"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_unregister_student_not_in_activity(self, client, reset_activities):
        """Test unregistering a student who is not in the activity"""
        response = client.delete(
            "/activities/Programming%20Class/unregister",
            params={"email": "notamember@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test the full cycle: signup then unregister"""
        email = "testuser@mergington.edu"
        activity = "Gym%20Class"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 200
        
        # Verify signup worked
        response = client.get("/activities")
        assert email in response.json()["Gym Class"]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
        assert response.status_code == 200
        
        # Verify unregister worked
        response = client.get("/activities")
        assert email not in response.json()["Gym Class"]["participants"]


class TestCapacityManagement:
    """Tests for activity capacity constraints"""
    
    def test_activity_capacity_is_not_enforced_currently(self, client, reset_activities):
        """Test current behavior: capacity is not enforced (for documentation)"""
        # This test documents current behavior where capacity is not enforced
        # If capacity enforcement is added later, this test should be updated
        activity = "Gym%20Class"
        
        # Try to add students beyond current size
        for i in range(5):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            # Currently should not fail due to capacity
            assert response.status_code == 200

