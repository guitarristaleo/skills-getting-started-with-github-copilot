import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def backup_activities():
    original = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(original)


def test_get_activities_returns_structure(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant(client):
    activity = "Chess Club"
    email = "tester@example.com"

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity]["participants"]


def test_signup_duplicate_returns_400(client):
    activity = "Chess Club"
    email = "dup@example.com"

    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200

    # Second sign-up should fail with 400
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400


def test_remove_participant_removes(client):
    activity = "Chess Club"
    email = "remove_me@example.com"

    # Ensure participant exists
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200

    # Remove participant
    r2 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r2.status_code == 200

    # Verify removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]


def test_remove_nonexistent_returns_404(client):
    activity = "Chess Club"
    email = "nope@example.com"

    r = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r.status_code == 404
