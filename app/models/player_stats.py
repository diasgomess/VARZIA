from pydantic import BaseModel


class PlayerStats(BaseModel):
    match_id: int
    player_id: int
    passes: int = 0
    shots: int = 0
    goals: int = 0
    tackles: int = 0
    distance: float = 0.0
    rating: float = 0.0
