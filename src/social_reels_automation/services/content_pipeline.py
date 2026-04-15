from __future__ import annotations

from pathlib import Path

from social_reels_automation.clients.content_strategy_client import ContentStrategyClient
from social_reels_automation.clients.higgsfield_client import HiggsfieldClient
from social_reels_automation.clients.instagram_client import InstagramClient
from social_reels_automation.clients.trend_client import TrendClient
from social_reels_automation.clients.youtube_client import YouTubeClient
from social_reels_automation.models import PipelineResponse, PublishResult, ReelRequest


class ContentPipeline:
    def __init__(self) -> None:
        self.strategy = ContentStrategyClient()
        self.higgsfield = HiggsfieldClient()
        self.instagram = InstagramClient()
        self.trends = TrendClient()
        self.youtube = YouTubeClient()

    async def run(self, reel_request: ReelRequest) -> PipelineResponse:
        trend_snapshots = await self.trends.fetch_daily_signals()
        brief = await self.strategy.create_content_brief(reel_request, trend_snapshots)
        higgsfield_result = await self.higgsfield.generate_video(brief)
        output_dir = Path.cwd() / "generated"
        local_video = await self.higgsfield.download_asset(higgsfield_result.asset_url, output_dir)

        youtube_video_id, youtube_url = self.youtube.upload_short(local_video, brief)
        instagram_creation_id, instagram_publish_id = await self.instagram.publish_reel(
            video_url=higgsfield_result.asset_url,
            caption=brief.caption,
        )

        return PipelineResponse(
            brief=brief,
            trends=trend_snapshots,
            higgsfield=higgsfield_result,
            downloaded_video_path=str(local_video),
            publish=PublishResult(
                youtube_video_id=youtube_video_id,
                youtube_url=youtube_url,
                instagram_creation_id=instagram_creation_id,
                instagram_publish_id=instagram_publish_id,
            ),
        )
