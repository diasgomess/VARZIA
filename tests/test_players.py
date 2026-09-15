from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import Base, app, get_db


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_team(name: str):
    response = client.post("/teams", json={"name": name})
    assert response.status_code == 201
    return response.json()["id"]


def create_player(team_id: int, number: int, name: str = "Jogador"):
    payload = {
        "name": name,
        "number": number,
        "position": "midfielder",
        "dominant_foot": "right",
        "status": "active",
    }
    return client.post(f"/teams/{team_id}/players", json=payload)


def test_create_player_and_list_players():
    reset_database()
    team_id = create_team("Time Azul")

    create_response = create_player(team_id, 10, name="Carlos")
    assert create_response.status_code == 201
    assert create_response.json()["team_id"] == team_id

    list_response = client.get(f"/teams/{team_id}/players")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["name"] == "Carlos"


def test_reject_duplicate_number_in_same_team():
    reset_database()
    team_id = create_team("Time Verde")

    first = create_player(team_id, 7, name="Leo")
    assert first.status_code == 201

    duplicate = create_player(team_id, 7, name="Pedro")
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Player number already exists for this team"


def test_allow_same_number_in_different_teams():
    reset_database()
    team_a = create_team("Time A")
    team_b = create_team("Time B")

    assert create_player(team_a, 9, name="Rafa").status_code == 201
    assert create_player(team_b, 9, name="Neto").status_code == 201


def test_get_update_and_delete_player():
    reset_database()
    team_a = create_team("Time Ouro")
    team_b = create_team("Time Prata")

    created = create_player(team_a, 8, name="Marcos")
    player_id = created.json()["id"]

    get_response = client.get(f"/players/{player_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Marcos"

    update_payload = {
        "name": "Marcos Silva",
        "number": 6,
        "position": "defender",
        "dominant_foot": "left",
        "status": "active",
        "team_id": team_b,
    }
    update_response = client.put(f"/players/{player_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["team_id"] == team_b
    assert update_response.json()["number"] == 6

    delete_response = client.delete(f"/players/{player_id}")
    assert delete_response.status_code == 204

    not_found_response = client.get(f"/players/{player_id}")
    assert not_found_response.status_code == 404
