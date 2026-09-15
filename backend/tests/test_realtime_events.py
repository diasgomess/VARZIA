from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.main import app


client = TestClient(app)


def test_create_event_returns_created_when_no_connections() -> None:
    payload = {
        "type": "TACTICAL_ALERT",
        "severity": "HIGH",
        "timestamp": "00:34:21",
        "title": "Exploração do corredor esquerdo",
        "description": "...",
    }

    response = client.post("/events", json=payload)

    assert response.status_code == 201
    assert response.json()["event"] == payload


def test_create_event_broadcasts_to_connected_websocket() -> None:
    payload = {
        "type": "TACTICAL_ALERT",
        "severity": "HIGH",
        "timestamp": "00:34:21",
        "title": "Exploração do corredor esquerdo",
        "description": "...",
    }

    with client.websocket_connect("/ws/events") as websocket:
        response = client.post("/events", json=payload)

        assert response.status_code == 201
        assert websocket.receive_json() == payload
