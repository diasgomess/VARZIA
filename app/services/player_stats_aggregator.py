from __future__ import annotations

from dataclasses import dataclass

from app.models.event import Event
from app.models.player_stats import PlayerStats


POSITION_WEIGHTS = {
    "GK": {"passes": 0.5, "shots": 0.2, "goals": 0.2, "tackles": 1.0, "distance": 0.3},
    "DEF": {"passes": 0.6, "shots": 0.8, "goals": 1.0, "tackles": 1.2, "distance": 0.5},
    "MID": {"passes": 1.2, "shots": 1.0, "goals": 1.0, "tackles": 0.8, "distance": 0.6},
    "FWD": {"passes": 0.6, "shots": 1.2, "goals": 2.0, "tackles": 0.4, "distance": 0.4},
    "DEFAULT": {"passes": 0.8, "shots": 0.8, "goals": 1.2, "tackles": 0.8, "distance": 0.5},
}


@dataclass
class InMemoryPlayerStatsStore:
    _storage: dict[tuple[int, int], PlayerStats]

    def __init__(self) -> None:
        self._storage = {}

    def save_many(self, stats: list[PlayerStats]) -> list[PlayerStats]:
        for stat in stats:
            self._storage[(stat.match_id, stat.player_id)] = stat
        return stats

    def get_match(self, match_id: int) -> list[PlayerStats]:
        return [stat for (m_id, _), stat in self._storage.items() if m_id == match_id]


def _calculate_rating(stat: PlayerStats, position: str | None) -> float:
    weights = POSITION_WEIGHTS.get((position or "").upper(), POSITION_WEIGHTS["DEFAULT"])
    raw_score = (
        stat.passes * weights["passes"]
        + stat.shots * weights["shots"]
        + stat.goals * weights["goals"]
        + stat.tackles * weights["tackles"]
        + stat.distance * weights["distance"]
    )
    return round(max(0.0, min(10.0, 5.0 + (raw_score / 10.0))), 2)


def aggregate_player_stats(
    events: list[Event],
    match_id: int,
    player_positions: dict[int, str] | None = None,
) -> list[PlayerStats]:
    player_positions = player_positions or {}
    grouped: dict[int, PlayerStats] = {}

    for event in events:
        if event.match_id != match_id:
            continue

        stats = grouped.setdefault(
            event.player_id,
            PlayerStats(match_id=match_id, player_id=event.player_id),
        )

        if event.event_type == "pass":
            stats.passes += 1
        elif event.event_type == "shot":
            stats.shots += 1
        elif event.event_type == "goal":
            stats.goals += 1
        elif event.event_type == "tackle":
            stats.tackles += 1
        elif event.event_type == "distance":
            stats.distance += float(event.value)

    for stats in grouped.values():
        position = player_positions.get(stats.player_id)
        stats.rating = _calculate_rating(stats, position)

    return sorted(grouped.values(), key=lambda stat: stat.player_id)


def recalculate_match_player_stats(
    events: list[Event],
    match_id: int,
    store: InMemoryPlayerStatsStore,
    player_positions: dict[int, str] | None = None,
) -> list[PlayerStats]:
    stats = aggregate_player_stats(events=events, match_id=match_id, player_positions=player_positions)
    return store.save_many(stats)
