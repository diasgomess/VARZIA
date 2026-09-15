from datetime import datetime, timedelta, timezone
import unittest

from varzia.recommendation_engine import MetricSample, SimpleRecommendationEngine
from varzia.service import InMemoryAIInsightsStore, InsightGenerationService
from varzia.websocket import CollectingAlertPublisher


class RecommendationEngineTests(unittest.TestCase):
    def test_generates_insight_when_left_attacks_above_threshold(self) -> None:
        now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
        samples = [
            MetricSample(timestamp=now - timedelta(minutes=4), attacks_left=7, attacks_right=2),
            MetricSample(timestamp=now - timedelta(minutes=2), attacks_left=6, attacks_right=3),
            MetricSample(timestamp=now - timedelta(minutes=8), attacks_left=10, attacks_right=0),
        ]

        engine = SimpleRecommendationEngine()
        insights = engine.analyze(match_id="match-1", samples=samples, now=now)

        self.assertEqual(len(insights), 1)
        self.assertEqual(insights[0].severity, "medium")
        self.assertEqual(insights[0].rule_id, "left_attack_overload")

    def test_does_not_generate_insight_when_threshold_not_met(self) -> None:
        now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
        samples = [
            MetricSample(timestamp=now - timedelta(minutes=4), attacks_left=5, attacks_right=5),
            MetricSample(timestamp=now - timedelta(minutes=2), attacks_left=2, attacks_right=4),
        ]

        engine = SimpleRecommendationEngine()
        insights = engine.analyze(match_id="match-1", samples=samples, now=now)

        self.assertEqual(insights, [])

    def test_service_stores_and_publishes_alert(self) -> None:
        now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
        samples = [
            MetricSample(timestamp=now - timedelta(minutes=3), attacks_left=8, attacks_right=2),
        ]
        store = InMemoryAIInsightsStore()
        publisher = CollectingAlertPublisher()
        service = InsightGenerationService(store=store, alert_publisher=publisher)

        insights = service.generate_ai_insights(match_id="match-99", samples=samples, now=now)

        self.assertEqual(len(insights), 1)
        self.assertEqual(len(store.list_by_match("match-99")), 1)
        self.assertEqual(len(publisher.messages), 1)
        channel, payload = publisher.messages[0]
        self.assertEqual(channel, "match:match-99:alerts")
        self.assertEqual(payload["severity"], "medium")
        self.assertIn("Recomenda-se", payload["recommendation"])


if __name__ == "__main__":
    unittest.main()
