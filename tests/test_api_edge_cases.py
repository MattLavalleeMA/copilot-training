from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities_state():
    original_state = deepcopy(activities)

    yield

    activities.clear()
    activities.update(original_state)


def test_signup_unknown_activity_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_unknown_activity_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_non_member_returns_not_found(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not-registered@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student not registered for this activity"}


def test_signup_full_activity_returns_error(client):
    # Arrange
    activity_name = "Full Test Activity"
    activities[activity_name] = {
        "description": "Temporary activity for full-capacity test",
        "schedule": "Mondays, 1:00 PM - 2:00 PM",
        "max_participants": 1,
        "participants": ["filled@mergington.edu"],
    }
    email = "newcomer@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    assert email not in activities[activity_name]["participants"]
