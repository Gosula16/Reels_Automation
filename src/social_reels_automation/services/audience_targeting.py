from __future__ import annotations

import re
from dataclasses import dataclass

from social_reels_automation.config import get_settings
from social_reels_automation.models import TrendSnapshot


@dataclass
class RankedTopic:
    topic: str
    score: float
    source: str


class AudienceTargetingService:
    def rank_topics(self, trend_snapshots: list[TrendSnapshot]) -> list[RankedTopic]:
        settings = get_settings()
        audience_terms = self._keywords(
            f"{settings.brand_niche} {settings.target_audience} {' '.join(settings.parsed_topic_seeds)}"
        )
        ranked: list[RankedTopic] = []
        for snapshot in trend_snapshots:
            for topic in snapshot.topics:
                ranked.append(
                    RankedTopic(
                        topic=topic,
                        source=snapshot.source,
                        score=self._score_topic(topic, audience_terms, snapshot.source),
                    )
                )
        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked

    def _score_topic(self, topic: str, audience_terms: set[str], source: str) -> float:
        topic_terms = self._keywords(topic)
        overlap = len(topic_terms & audience_terms)
        niche_bonus = sum(1.0 for token in topic_terms if token in {"ai", "growth", "creator", "founder", "marketing", "business"})
        source_weight = 1.4 if source == "google_trends" else 1.1
        length_penalty = max(len(topic_terms) - 8, 0) * 0.08
        return (overlap * 2.2 + niche_bonus + 1.0) * source_weight - length_penalty

    def _keywords(self, text: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}
