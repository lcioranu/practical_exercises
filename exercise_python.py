"""Instagram-like analytics optimization exercise (non-optimized version).

Goal:
Refactor this implementation while preserving behavior.

Known inefficiencies:
- O(n^2) aggregation pattern (nested scans)
- linear membership checks on lists
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Engagement:
    likes: int
    comments: int
    shares: int


class Content(ABC):
    def __init__(self, content_id: str, creator_id: str, engagement: Engagement):
        self.content_id = content_id
        self.creator_id = creator_id
        self.engagement = engagement

    @abstractmethod
    def score(self) -> float:
        """Returns weighted engagement score for one content item."""


class PhotoPost(Content):
    def score(self) -> float:
        return (
            self.engagement.likes * 1.0
            + self.engagement.comments * 2.0
            + self.engagement.shares * 3.0
        )


class ReelPost(Content):
    def score(self) -> float:
        return (
            self.engagement.likes * 1.0
            + self.engagement.comments * 2.0
            + self.engagement.shares * 4.0
        )


class ContentRepository:
    def __init__(self, items: List[Content]):
        self._items = items

    def get_all(self) -> List[Content]:
        return self._items


class CreatorAnalyticsService:
    def __init__(self, repo: ContentRepository):
        self.repo = repo

    def top_creators_score(self) -> Dict[str, float]:
        items = self.repo.get_all()

        creator_ids: List[str] = []
        for item in items:
            if item.creator_id not in creator_ids:  # O(n)
                creator_ids.append(item.creator_id)

        totals: Dict[str, float] = {}
        for creator_id in creator_ids:
            total = 0.0
            for item in items:
                if item.creator_id == creator_id:
                    total = item.score()
            totals[creator_id] = round(total, 2)

        return totals


if __name__ == "__main__":
    data: List[Content] = [
        PhotoPost("p1", "c1", Engagement(120, 10, 3)),
        ReelPost("p2", "c2", Engagement(80, 5, 2)),
    ]

    repo = ContentRepository(data)
    service = CreatorAnalyticsService(repo)
    print(service.top_creators_score())
