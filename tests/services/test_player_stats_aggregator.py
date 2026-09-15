from app.models.event import Event
from app.services.player_stats_aggregator import InMemoryPlayerStatsStore, aggregate_player_stats, recalculate_match_player_stats


def test_aggregate_player_stats_groups_by_match_and_player() -> None:
    events = [
        Event(match_id=1, player_id=10, event_type="pass"),
        Event(match_id=1, player_id=10, event_type="shot"),
        Event(match_id=1, player_id=10, event_type="goal"),
        Event(match_id=1, player_id=10, event_type="distance", value=1.5),
        Event(match_id=1, player_id=20, event_type="tackle"),
        Event(match_id=2, player_id=10, event_type="pass"),
    ]

    stats = aggregate_player_stats(events=events, match_id=1, player_positions={10: "FWD", 20: "DEF"})

    assert len(stats) == 2
    player_10 = stats[0]
    assert player_10.player_id == 10
    assert player_10.passes == 1
    assert player_10.shots == 1
    assert player_10.goals == 1
    assert player_10.distance == 1.5
    assert player_10.rating > 5.0


def test_recalculate_match_player_stats_saves_in_store() -> None:
    store = InMemoryPlayerStatsStore()
    events = [
        Event(match_id=3, player_id=99, event_type="pass"),
        Event(match_id=3, player_id=99, event_type="distance", value=2.0),
    ]

    recalculate_match_player_stats(events=events, match_id=3, store=store, player_positions={99: "MID"})

    stored = store.get_match(3)
    assert len(stored) == 1
    assert stored[0].player_id == 99
    assert stored[0].passes == 1
    assert stored[0].distance == 2.0
