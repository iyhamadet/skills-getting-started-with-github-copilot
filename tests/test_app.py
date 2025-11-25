import os
import sys

# Make sure src is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_user@example.com"

    # Ensure clean state
    r = client.get("/activities")
    participants = r.json()[activity]["participants"]
    if email in participants:
        client.post(f"/activities/{activity}/unregister?email={email}")

    # Sign up
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Verify present
    r = client.get("/activities")
    assert email in r.json()[activity]["participants"]

    # Unregister
    r = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r.status_code == 200
    assert "Unregistered" in r.json().get("message", "")

    # Verify removed
    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]


def test_signup_duplicate_returns_400():
    activity = "Chess Club"
    email = "dup_user@example.com"

    # Cleanup if present
    try:
        client.post(f"/activities/{activity}/unregister?email={email}")
    except Exception:
        pass

    # First signup
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    # Duplicate signup should fail
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # Cleanup
    client.post(f"/activities/{activity}/unregister?email={email}")
