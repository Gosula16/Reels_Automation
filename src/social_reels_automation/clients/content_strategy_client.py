from __future__ import annotations

from social_reels_automation.clients.anthropic_client import AnthropicClient
from social_reels_automation.clients.gemini_client import GeminiClient
from social_reels_automation.config import get_settings
from social_reels_automation.models import ContentBrief, ReelRequest, TrendSnapshot


class ContentStrategyClient:
    def __init__(self) -> None:
        self.gemini = GeminiClient()
        self.anthropic = AnthropicClient()

    async def create_content_brief(
        self,
        reel_request: ReelRequest,
        trends: list[TrendSnapshot],
    ) -> ContentBrief:
        settings = get_settings()
        errors: list[str] = []

        if settings.gemini_api_key:
            try:
                return await self.gemini.create_content_brief(reel_request, trends)
            except Exception as exc:
                errors.append(f"Gemini failed: {exc}")

        if settings.anthropic_api_key:
            try:
                return await self.anthropic.create_content_brief(reel_request, trends)
            except Exception as exc:
                errors.append(f"Claude failed: {exc}")

        if errors:
            raise RuntimeError(" | ".join(errors))
        raise RuntimeError("No content model configured. Set GEMINI_API_KEY or ANTHROPIC_API_KEY.")
