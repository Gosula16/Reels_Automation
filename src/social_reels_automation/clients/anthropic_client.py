from __future__ import annotations

import json

import httpx

from social_reels_automation.clients.prompt_builder import build_content_prompts
from social_reels_automation.config import get_settings
from social_reels_automation.models import ContentBrief, ReelRequest, TrendSnapshot


class AnthropicClient:
    api_url = "https://api.anthropic.com/v1/messages"

    async def create_content_brief(
        self,
        reel_request: ReelRequest,
        trends: list[TrendSnapshot],
    ) -> ContentBrief:
        settings = get_settings()
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required to generate content briefs.")
        system_prompt, user_prompt = build_content_prompts(reel_request, trends)

        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": settings.anthropic_model,
            "max_tokens": 1400,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()

        data = response.json()
        text = "".join(block["text"] for block in data["content"] if block["type"] == "text")
        parsed = json.loads(text)
        return ContentBrief.model_validate(parsed)
