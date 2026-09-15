from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable


@dataclass(frozen=True)
class MetricSample:
    timestamp: datetime
    attacks_left: int
    attacks_right: int


@dataclass(frozen=True)
class AIInsight:
    match_id: str
    rule_id: str
    severity: str
    recommendation: str
    details: str
    created_at: datetime

    def to_dict(self) -> dict[str, str]:
        return {
            "match_id": self.match_id,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "recommendation": self.recommendation,
            "details": self.details,
            "created_at": self.created_at.isoformat(),
        }


class SimpleRecommendationEngine:
    """Rule-based engine for tactical insights from temporal metrics."""

    def __init__(self, window_minutes: int = 5, left_attack_threshold: float = 0.65) -> None:
        self.window_minutes = window_minutes
        self.left_attack_threshold = left_attack_threshold

    def analyze(self, match_id: str, samples: Iterable[MetricSample], now: datetime | None = None) -> list[AIInsight]:
        now = now or datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=self.window_minutes)

        recent_samples = [sample for sample in samples if sample.timestamp >= window_start]
        if not recent_samples:
            return []

        total_left = sum(sample.attacks_left for sample in recent_samples)
        total_right = sum(sample.attacks_right for sample in recent_samples)
        total_attacks = total_left + total_right

        if total_attacks == 0:
            return []

        left_ratio = total_left / total_attacks
        if left_ratio <= self.left_attack_threshold:
            return []

        recommendation = (
            "Ataques concentrados no lado esquerdo acima de 65% nos últimos 5 minutos. "
            "Recomenda-se ajustar cobertura e pressionar a saída pelo lado esquerdo."
        )
        insight = AIInsight(
            match_id=match_id,
            rule_id="left_attack_overload",
            severity="medium",
            recommendation=recommendation,
            details=f"left_ratio={left_ratio:.2%}; left={total_left}; right={total_right}",
            created_at=now,
        )
        return [insight]
