import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    original_activities = copy.deepcopy(activities)
    yield
    # Restore original activities after test
    activities.clear()
    activities.update(original_activities)