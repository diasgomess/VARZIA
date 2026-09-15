from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MatchCreate(BaseModel):
    team_id: int
    opponent: str = Field(min_length=1, max_length=100)
    date: datetime
    location: str = Field(min_length=1, max_length=200)
    formation: str = Field(min_length=1, max_length=20)
    status: str = Field(default="scheduled", min_length=1, max_length=20)
    video_url: Optional[str] = Field(default=None, max_length=500)


class MatchUpdate(BaseModel):
    team_id: Optional[int] = None
    opponent: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date: Optional[datetime] = None
    location: Optional[str] = Field(default=None, min_length=1, max_length=200)
    formation: Optional[str] = Field(default=None, min_length=1, max_length=20)
    status: Optional[str] = Field(default=None, min_length=1, max_length=20)
    video_url: Optional[str] = Field(default=None, max_length=500)


class MatchLineupUpdate(BaseModel):
    player_ids: list[int]


class MatchRead(BaseModel):
    id: int
    team_id: int
    opponent: str
    date: datetime
    location: str
    formation: str
    status: str
    video_url: Optional[str]
    starting_lineup: list[int]
