from __future__ import annotations

from urllib.parse import quote_plus
from xml.etree import ElementTree

import httpx

from social_reels_automation.config import get_settings
from social_reels_automation.models import TrendSnapshot


class TrendClient:
    async def fetch_daily_signals(self) -> list[TrendSnapshot]:
        settings = get_settings()
        trend_snapshots = [
            await self._fetch_google_trends(settings.trend_region),
            await self._fetch_google_news(settings.brand_niche),
        ]
        return [snapshot for snapshot in trend_snapshots if snapshot.topics]

    async def _fetch_google_trends(self, region: str) -> TrendSnapshot:
        url = f"https://trends.google.com/trending/rss?geo={region}"
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
        root = ElementTree.fromstring(response.text)
        titles = [item.findtext("title", default="").strip() for item in root.findall("./channel/item")]
        topics = [title for title in titles if title][:10]
        return TrendSnapshot(source="google_trends", query=region, topics=topics)

    async def _fetch_google_news(self, query: str) -> TrendSnapshot:
        encoded_query = quote_plus(query)
        url = (
            "https://news.google.com/rss/search?"
            f"q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        )
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
        root = ElementTree.fromstring(response.text)
        titles = [item.findtext("title", default="").strip() for item in root.findall("./channel/item")]
        topics = [title for title in titles if title][:10]
        return TrendSnapshot(source="google_news", query=query, topics=topics)
