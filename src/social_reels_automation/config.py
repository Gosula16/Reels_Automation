from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-6", alias="ANTHROPIC_MODEL")

    higgsfield_api_key: str | None = Field(default=None, alias="HIGGSFIELD_API_KEY")
    higgsfield_api_secret: str | None = Field(default=None, alias="HIGGSFIELD_API_SECRET")
    higgsfield_base_url: str = Field(default="https://platform.higgsfield.ai", alias="HIGGSFIELD_BASE_URL")
    higgsfield_video_path: str = Field(default="/higgsfield-ai/soul/standard", alias="HIGGSFIELD_VIDEO_PATH")

    instagram_access_token: str | None = Field(default=None, alias="INSTAGRAM_ACCESS_TOKEN")
    instagram_ig_user_id: str | None = Field(default=None, alias="INSTAGRAM_IG_USER_ID")
    instagram_graph_version: str = Field(default="v22.0", alias="INSTAGRAM_GRAPH_VERSION")
    instagram_share_to_feed: bool = Field(default=True, alias="INSTAGRAM_SHARE_TO_FEED")

    youtube_client_secrets_file: Path = Field(default=Path("./client_secrets.json"), alias="YOUTUBE_CLIENT_SECRETS_FILE")
    youtube_token_file: Path = Field(default=Path("./youtube_token.json"), alias="YOUTUBE_TOKEN_FILE")
    youtube_category_id: str = Field(default="22", alias="YOUTUBE_CATEGORY_ID")
    publish_privacy_status: str = Field(default="public", alias="PUBLISH_PRIVACY_STATUS")

    brand_name: str = Field(default="Your Brand", alias="BRAND_NAME")
    brand_niche: str = Field(default="personal branding", alias="BRAND_NICHE")
    target_audience: str = Field(default="founders and creators", alias="TARGET_AUDIENCE")
    default_language: str = Field(default="en", alias="DEFAULT_LANGUAGE")
    default_timezone: str = Field(default="Asia/Calcutta", alias="DEFAULT_TIMEZONE")
    trend_region: str = Field(default="IN", alias="TREND_REGION")
    automation_enabled: bool = Field(default=True, alias="AUTOMATION_ENABLED")
    automation_post_times: str = Field(default="10:00,18:00", alias="AUTOMATION_POST_TIMES")
    automation_topic_seeds: str = Field(
        default="founder tips,creator growth,instagram growth,youtube shorts ideas,ai marketing",
        alias="AUTOMATION_TOPIC_SEEDS",
    )

    @property
    def parsed_post_times(self) -> list[str]:
        return [value.strip() for value in self.automation_post_times.split(",") if value.strip()]

    @property
    def parsed_topic_seeds(self) -> list[str]:
        return [value.strip() for value in self.automation_topic_seeds.split(",") if value.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
