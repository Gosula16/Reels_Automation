from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from social_reels_automation.config import get_settings
from social_reels_automation.models import AutomationRunRecord, AutomationStatus, ReelRequest
from social_reels_automation.services.audience_targeting import AudienceTargetingService
from social_reels_automation.services.content_pipeline import ContentPipeline


class AutomationService:
    def __init__(self, pipeline: ContentPipeline) -> None:
        self.pipeline = pipeline
        self.targeting = AudienceTargetingService()
        self.scheduler: AsyncIOScheduler | None = None
        self.recent_runs: deque[AutomationRunRecord] = deque(maxlen=20)
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        settings = get_settings()
        if not settings.automation_enabled:
            return
        if self.scheduler and self.scheduler.running:
            return

        timezone = self._resolve_timezone(settings.default_timezone)
        self.scheduler = AsyncIOScheduler(timezone=timezone)
        for post_time in settings.parsed_post_times[:2]:
            hour_str, minute_str = post_time.split(":", maxsplit=1)
            self.scheduler.add_job(
                self.run_single_scheduled_post,
                "cron",
                hour=int(hour_str),
                minute=int(minute_str),
                args=[post_time],
                id=f"daily-post-{post_time}",
                replace_existing=True,
            )
        self.scheduler.start()

    async def shutdown(self) -> None:
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    async def run_daily_batch(self) -> list[str]:
        settings = get_settings()
        results: list[str] = []
        for post_time in settings.parsed_post_times[:2]:
            results.append(await self.run_single_scheduled_post(post_time))
        return results

    async def run_single_scheduled_post(self, scheduled_for: str) -> str:
        async with self._lock:
            settings = get_settings()
            topic = await self._build_topic()
            reel_request = ReelRequest(
                topic=topic,
                goal="increase qualified reach and engagement",
                style="vertical cinematic short-form, modern, energetic",
                call_to_action="Follow for daily insights and watch the next reel",
                duration_seconds=20,
            )
            try:
                await self.pipeline.run(reel_request)
                detail = f"Posted successfully for topic: {topic}"
                status = "success"
            except Exception as exc:
                detail = str(exc)
                status = "failed"

            now = datetime.now(self._resolve_timezone(settings.default_timezone)).isoformat()
            self.recent_runs.appendleft(
                AutomationRunRecord(
                    scheduled_for=f"{now} [{scheduled_for}]",
                    topic=topic,
                    status=status,
                    detail=detail,
                )
            )
            return detail

    async def status(self) -> AutomationStatus:
        settings = get_settings()
        return AutomationStatus(
            enabled=settings.automation_enabled,
            timezone=settings.default_timezone,
            post_times=settings.parsed_post_times[:2],
            topic_seeds=settings.parsed_topic_seeds,
            recent_runs=list(self.recent_runs),
        )

    async def _build_topic(self) -> str:
        settings = get_settings()
        trend_snapshots = await self.pipeline.trends.fetch_daily_signals()
        seeds = settings.parsed_topic_seeds or [settings.brand_niche]
        seed = seeds[len(self.recent_runs) % len(seeds)]
        ranked_topics = self.targeting.rank_topics(trend_snapshots)
        if ranked_topics:
            return f"{seed} inspired by current trend: {ranked_topics[0].topic}"
        return seed

    def _resolve_timezone(self, timezone_name: str) -> ZoneInfo:
        aliases = {
            "Asia/Calcutta": "Asia/Kolkata",
        }
        normalized = aliases.get(timezone_name, timezone_name)
        try:
            return ZoneInfo(normalized)
        except ZoneInfoNotFoundError:
            return ZoneInfo("UTC")
