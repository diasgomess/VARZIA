from fastapi import FastAPI

from app.db import Base, engine
from app.routes.matches import router as matches_router


app = FastAPI(title="VARZIA API")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(matches_router)
from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

DATABASE_URL = "sqlite:///./varzia.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)

    players: Mapped[list["Player"]] = relationship(back_populates="team", cascade="all, delete-orphan")


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    number: Mapped[int] = mapped_column(index=True)
    position: Mapped[str] = mapped_column(String(50))
    dominant_foot: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20))

    team: Mapped[Team] = relationship(back_populates="players")


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class PlayerBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    number: int = Field(ge=1, le=99)
    position: str = Field(min_length=1, max_length=50)
    dominant_foot: str = Field(pattern="^(left|right|both)$")
    status: str = Field(pattern="^(active|inactive|injured|suspended)$")


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(PlayerBase):
    team_id: int | None = Field(default=None, ge=1)


class PlayerResponse(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int


app = FastAPI(title="VARZIA API")
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_team_or_404(db: Session, team_id: int) -> Team:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team


def ensure_unique_number(db: Session, team_id: int, number: int, player_id: int | None = None) -> None:
    query = select(Player).where(Player.team_id == team_id, Player.number == number)
    existing = db.execute(query).scalar_one_or_none()
    if existing and existing.id != player_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player number already exists for this team",
        )


@app.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(payload: TeamCreate, db: Session = Depends(get_db)):
    team = Team(name=payload.name)
    db.add(team)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team already exists")
    db.refresh(team)
    return team


@app.post("/teams/{team_id}/players", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_player(team_id: int, payload: PlayerCreate, db: Session = Depends(get_db)):
    get_team_or_404(db, team_id)
    ensure_unique_number(db, team_id, payload.number)

    player = Player(team_id=team_id, **payload.model_dump())
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@app.get("/teams/{team_id}/players", response_model=list[PlayerResponse])
def list_players(team_id: int, db: Session = Depends(get_db)):
    get_team_or_404(db, team_id)
    return db.execute(select(Player).where(Player.team_id == team_id)).scalars().all()


@app.get("/players/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return player


@app.put("/players/{player_id}", response_model=PlayerResponse)
def update_player(player_id: int, payload: PlayerUpdate, db: Session = Depends(get_db)):
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    new_team_id = payload.team_id or player.team_id
    get_team_or_404(db, new_team_id)
    ensure_unique_number(db, new_team_id, payload.number, player_id=player.id)

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(player, field, value)

    if payload.team_id is not None:
        player.team_id = payload.team_id

    db.commit()
    db.refresh(player)
    return player


@app.delete("/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    db.delete(player)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
from fastapi import FastAPI

from app.api.routes.player_stats import router as player_stats_router

app = FastAPI(title="VARZIA API")
app.include_router(player_stats_router)
