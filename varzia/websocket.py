from __future__ import annotations

from typing import Protocol


class AlertPublisher(Protocol):
    def publish(self, channel: str, payload: dict[str, str]) -> None: ...


class CollectingAlertPublisher:
    """Simple publisher used for integration and tests."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, dict[str, str]]] = []

    def publish(self, channel: str, payload: dict[str, str]) -> None:
        self.messages.append((channel, payload))
