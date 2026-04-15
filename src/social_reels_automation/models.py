from __future__ import annotations

from pydantic import BaseModel, Field


class ReelRequest(BaseModel):
    topic: str = Field(..., min_length=5)
    goal: str = Field(default="grow reach")
    style: str = Field(default="cinematic, modern, attention-grabbing")
    call_to_action: str = Field(default="Follow for more")
    duration_seconds: int = Field(default=20, ge=8, le=60)


class ContentBrief(BaseModel):
    hook: str
    spoken_script: str
    caption: str
    hashtags: list[str]
    youtube_title: str
    youtube_description: str
    higgsfield_prompt: str
    shot_plan: list[str]
    reach_rationale: list[str]


class TrendSnapshot(BaseModel):
    source: str
    query: str
    topics: list[str]


class HiggsfieldGenerationResult(BaseModel):
    request_id: str
    status_url: str
    asset_url: str


class PublishResult(BaseModel):
    youtube_video_id: str | None = None
    youtube_url: str | None = None
    instagram_creation_id: str | None = None
    instagram_publish_id: str | None = None


class PipelineResponse(BaseModel):
    brief: ContentBrief
    trends: list[TrendSnapshot]
    higgsfield: HiggsfieldGenerationResult
    downloaded_video_path: str
    publish: PublishResult


class AutomationRunRecord(BaseModel):
    scheduled_for: str
    topic: str
    status: str
    detail: str


class AutomationStatus(BaseModel):
    enabled: bool
    timezone: str
    post_times: list[str]
    topic_seeds: list[str]
    recent_runs: list[AutomationRunRecord]
