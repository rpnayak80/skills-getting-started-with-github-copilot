import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield


def test_get_activities_returns_known_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert "description" in data[expected_activity]


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "newstudent@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(participant_email)}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {participant_email} for {activity_name}"}
    assert participant_email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(participant_email)}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/participants?email={quote(participant_email)}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {participant_email} from {activity_name}"}
    assert participant_email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "missing@mergington.edu"
    url = f"/activities/{quote(activity_name)}/participants?email={quote(participant_email)}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_invalid_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    participant_email = "student@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(participant_email)}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
