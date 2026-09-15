from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_recalculate_player_stats_endpoint() -> None:
    response = client.post(
        "/matches/11/player-stats/recalculate",
        json={
            "events": [
                {"match_id": 11, "player_id": 1, "event_type": "pass"},
                {"match_id": 11, "player_id": 1, "event_type": "goal"},
                {"match_id": 11, "player_id": 2, "event_type": "tackle"},
            ],
            "player_positions": {"1": "FWD", "2": "DEF"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["stats"]) == 2
    assert body["stats"][0]["player_id"] == 1
    assert body["stats"][0]["goals"] == 1
