from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="team", cascade="all, delete-orphan")


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)

    team = relationship("Team", back_populates="players")
    lineup_entries = relationship("MatchLineup", back_populates="player", cascade="all, delete-orphan")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    opponent = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)
    location = Column(String(200), nullable=False)
    formation = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="scheduled")
    video_url = Column(String(500), nullable=True)

    team = relationship("Team", back_populates="matches")
    lineup_entries = relationship("MatchLineup", back_populates="match", cascade="all, delete-orphan")


class MatchLineup(Base):
    __tablename__ = "match_lineups"

    match_id = Column(Integer, ForeignKey("matches.id"), primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), primary_key=True)
    is_starting = Column(Boolean, nullable=False, default=True)

    match = relationship("Match", back_populates="lineup_entries")
    player = relationship("Player", back_populates="lineup_entries")
