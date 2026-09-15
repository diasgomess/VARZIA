import os
from datetime import datetime

from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_varzia.db"

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Player, Team  # noqa: E402


client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _seed_team_and_players():
    db = SessionLocal()
    team = Team(name="VARZIA FC")
    db.add(team)
    db.commit()
    db.refresh(team)

    p1 = Player(name="Jogador 1", team_id=team.id)
    p2 = Player(name="Jogador 2", team_id=team.id)
    db.add_all([p1, p2])
    db.commit()
    db.refresh(p1)
    db.refresh(p2)
    team_id, p1_id, p2_id = team.id, p1.id, p2.id
    db.close()
    return team_id, p1_id, p2_id


def test_create_update_and_list_matches():
    team_id, _, _ = _seed_team_and_players()
    payload = {
        "team_id": team_id,
        "opponent": "Adversario FC",
        "date": datetime(2026, 9, 15, 10, 0, 0).isoformat(),
        "location": "Campo Central",
        "formation": "4-4-2",
        "status": "scheduled",
        "video_url": "https://example.com/match.mp4",
    }

    create_response = client.post("/matches/", json=payload)
    assert create_response.status_code == 200
    body = create_response.json()
    assert body["team_id"] == team_id
    assert body["video_url"] == payload["video_url"]
    match_id = body["id"]

    update_response = client.put(
        f"/matches/{match_id}",
        json={"formation": "4-3-3", "status": "finished", "video_url": "https://example.com/final.mp4"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["formation"] == "4-3-3"
    assert update_response.json()["status"] == "finished"

    list_response = client.get("/matches/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_set_starting_lineup_validates_team_players():
    team_id, p1_id, p2_id = _seed_team_and_players()
    create_response = client.post(
        "/matches/",
        json={
            "team_id": team_id,
            "opponent": "Adversario FC",
            "date": datetime(2026, 9, 15, 10, 0, 0).isoformat(),
            "location": "Campo Central",
            "formation": "4-4-2",
            "status": "scheduled",
        },
    )
    match_id = create_response.json()["id"]

    lineup_response = client.put(f"/matches/{match_id}/lineup", json={"player_ids": [p1_id, p2_id]})
    assert lineup_response.status_code == 200
    assert set(lineup_response.json()["starting_lineup"]) == {p1_id, p2_id}

    db = SessionLocal()
    other_team = Team(name="Visitante")
    db.add(other_team)
    db.commit()
    db.refresh(other_team)
    outsider = Player(name="Outro", team_id=other_team.id)
    db.add(outsider)
    db.commit()
    db.refresh(outsider)
    outsider_id = outsider.id
    db.close()

    invalid_lineup_response = client.put(
        f"/matches/{match_id}/lineup", json={"player_ids": [p1_id, outsider_id]}
    )
    assert invalid_lineup_response.status_code == 400
