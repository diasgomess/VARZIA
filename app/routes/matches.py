from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Match, MatchLineup, Player, Team
from app.schemas import MatchCreate, MatchLineupUpdate, MatchRead, MatchUpdate


router = APIRouter(prefix="/matches", tags=["matches"])


def _serialize_match(match: Match) -> MatchRead:
    return MatchRead(
        id=match.id,
        team_id=match.team_id,
        opponent=match.opponent,
        date=match.date,
        location=match.location,
        formation=match.formation,
        status=match.status,
        video_url=match.video_url,
        starting_lineup=[entry.player_id for entry in match.lineup_entries if entry.is_starting],
    )


@router.post("/", response_model=MatchRead)
def create_match(payload: MatchCreate, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == payload.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    match = Match(**payload.model_dump())
    db.add(match)
    db.commit()
    db.refresh(match)
    return _serialize_match(match)


@router.put("/{match_id}", response_model=MatchRead)
def update_match(match_id: int, payload: MatchUpdate, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    data = payload.model_dump(exclude_unset=True)
    if "team_id" in data:
        team = db.query(Team).filter(Team.id == data["team_id"]).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

    for field, value in data.items():
        setattr(match, field, value)

    db.commit()
    db.refresh(match)
    return _serialize_match(match)


@router.get("/", response_model=list[MatchRead])
def list_matches(team_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Match)
    if team_id is not None:
        query = query.filter(Match.team_id == team_id)
    matches = query.order_by(Match.date.desc()).all()
    return [_serialize_match(match) for match in matches]


@router.put("/{match_id}/lineup", response_model=MatchRead)
def set_starting_lineup(match_id: int, payload: MatchLineupUpdate, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if len(payload.player_ids) != len(set(payload.player_ids)):
        raise HTTPException(status_code=400, detail="Duplicate players in lineup")

    players = (
        db.query(Player)
        .filter(Player.id.in_(payload.player_ids), Player.team_id == match.team_id)
        .all()
    )
    if len(players) != len(payload.player_ids):
        raise HTTPException(status_code=400, detail="Invalid player list for team")

    db.query(MatchLineup).filter(MatchLineup.match_id == match.id).delete()
    for player_id in payload.player_ids:
        db.add(MatchLineup(match_id=match.id, player_id=player_id, is_starting=True))

    db.commit()
    db.refresh(match)
    return _serialize_match(match)
