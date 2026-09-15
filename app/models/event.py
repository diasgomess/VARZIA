from pydantic import BaseModel, Field


class Event(BaseModel):
    match_id: int
    player_id: int
    event_type: str = Field(pattern=r"^(pass|shot|goal|tackle|distance)$")
    value: float = 0.0
