from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .recommendation_engine import AIInsight, MetricSample, SimpleRecommendationEngine
from .websocket import AlertPublisher


@dataclass
class InMemoryAIInsightsStore:
    insights: list[AIInsight] = field(default_factory=list)

    def add(self, insight: AIInsight) -> None:
        self.insights.append(insight)

    def list_by_match(self, match_id: str) -> list[AIInsight]:
        return [insight for insight in self.insights if insight.match_id == match_id]


class InsightGenerationService:
    def __init__(
        self,
        engine: SimpleRecommendationEngine | None = None,
        store: InMemoryAIInsightsStore | None = None,
        alert_publisher: AlertPublisher | None = None,
    ) -> None:
        self.engine = engine or SimpleRecommendationEngine()
        self.store = store or InMemoryAIInsightsStore()
        self.alert_publisher = alert_publisher

    def generate_ai_insights(
        self,
        match_id: str,
        samples: list[MetricSample],
        now: datetime | None = None,
    ) -> list[AIInsight]:
        insights = self.engine.analyze(match_id=match_id, samples=samples, now=now)
        for insight in insights:
            self.store.add(insight)
            if self.alert_publisher:
                self.alert_publisher.publish(
                    channel=f"match:{match_id}:alerts",
                    payload=insight.to_dict(),
                )
        return insights


def generate_ai_insights_job(
    match_id: str,
    samples: list[MetricSample],
    service: InsightGenerationService | None = None,
    now: datetime | None = None,
) -> list[AIInsight]:
    execution_service = service or InsightGenerationService()
    return execution_service.generate_ai_insights(match_id=match_id, samples=samples, now=now)
