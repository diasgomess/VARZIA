from fastapi import APIRouter
from pydantic import BaseModel

from app.models.event import Event
from app.models.player_stats import PlayerStats
from app.services.player_stats_aggregator import InMemoryPlayerStatsStore, recalculate_match_player_stats

router = APIRouter(prefix="/matches", tags=["player-stats"])
store = InMemoryPlayerStatsStore()


class RecalculateStatsRequest(BaseModel):
    events: list[Event]
    player_positions: dict[int, str] = {}


class RecalculateStatsResponse(BaseModel):
    stats: list[PlayerStats]


@router.post("/{match_id}/player-stats/recalculate", response_model=RecalculateStatsResponse)
def recalculate_player_stats(match_id: int, payload: RecalculateStatsRequest) -> RecalculateStatsResponse:
    stats = recalculate_match_player_stats(
        events=payload.events,
        match_id=match_id,
        store=store,
        player_positions=payload.player_positions,
    )
    return RecalculateStatsResponse(stats=stats)
