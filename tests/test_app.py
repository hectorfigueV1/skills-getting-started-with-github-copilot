import pytest
from fastapi.testclient import TestClient

def test_root_redirect(client: TestClient):
    """Test that the root endpoint redirects to the static index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client: TestClient):
    """Test retrieving all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success(client: TestClient):
    """Test successful signup for an activity."""
    response = client.post("/activities/Chess Club/signup", params={"email": "newstudent@mergington.edu"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up newstudent@mergington.edu for Chess Club" == data["message"]

    # Verify the student was added
    response = client.get("/activities")
    activities = response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_activity_not_found(client: TestClient):
    """Test signup for non-existent activity."""
    response = client.post("/activities/NonExistent Activity/signup", params={"email": "student@mergington.edu"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]

def test_signup_already_signed_up(client: TestClient):
    """Test signup when student is already signed up."""
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "existing@mergington.edu"})
    # Try again
    response = client.post("/activities/Chess Club/signup", params={"email": "existing@mergington.edu"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up" == data["detail"]

def test_unregister_success(client: TestClient):
    """Test successful unregistration from an activity."""
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "student@mergington.edu"})
    # Then unregister
    response = client.delete("/activities/Chess Club/unregister", params={"email": "student@mergington.edu"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered student@mergington.edu from Chess Club" == data["message"]

    # Verify the student was removed
    response = client.get("/activities")
    activities = response.json()
    assert "student@mergington.edu" not in activities["Chess Club"]["participants"]

def test_unregister_activity_not_found(client: TestClient):
    """Test unregistration from non-existent activity."""
    response = client.delete("/activities/NonExistent Activity/unregister", params={"email": "student@mergington.edu"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]

def test_unregister_not_signed_up(client: TestClient):
    """Test unregistration when student is not signed up."""
    response = client.delete("/activities/Chess Club/unregister", params={"email": "notsignedup@mergington.edu"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student not signed up for this activity" == data["detail"]

def test_multiple_operations_isolation(client: TestClient):
    """Test that multiple operations work correctly and are isolated."""
    # Signup multiple students
    client.post("/activities/Programming Class/signup", params={"email": "student1@mergington.edu"})
    client.post("/activities/Programming Class/signup", params={"email": "student2@mergington.edu"})

    # Check they are both signed up
    response = client.get("/activities")
    data = response.json()
    assert "student1@mergington.edu" in data["Programming Class"]["participants"]
    assert "student2@mergington.edu" in data["Programming Class"]["participants"]

    # Unregister one
    client.delete("/activities/Programming Class/unregister", params={"email": "student1@mergington.edu"})

    # Check only one remains
    response = client.get("/activities")
    data = response.json()
    assert "student1@mergington.edu" not in data["Programming Class"]["participants"]
    assert "student2@mergington.edu" in data["Programming Class"]["participants"]