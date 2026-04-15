from __future__ import annotations

import json

import httpx

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
        system_prompt = (
            "You are a senior short-form social media strategist. "
            "Return valid JSON only. Create high-retention Instagram Reel and YouTube Short content "
            "for the provided topic. Optimize for a strong first two seconds, clear payoff, concise speech, "
            "and platform-safe captions. Keep it practical and audience-specific."
        )
        user_prompt = {
            "brand_name": settings.brand_name,
            "brand_niche": settings.brand_niche,
            "target_audience": settings.target_audience,
            "language": settings.default_language,
            "topic": reel_request.topic,
            "goal": reel_request.goal,
            "style": reel_request.style,
            "call_to_action": reel_request.call_to_action,
            "duration_seconds": reel_request.duration_seconds,
            "trend_signals": [trend.model_dump() for trend in trends],
            "instructions": [
                "Use the trend signals only when relevant to the niche and audience.",
                "Generate daily-fresh hashtags that combine niche, topic, and current trend language.",
                "Keep hashtags useful for both Instagram and YouTube Shorts.",
                "Avoid spammy, banned, or misleading hashtags.",
            ],
            "output_schema": {
                "hook": "string",
                "spoken_script": "string",
                "caption": "string",
                "hashtags": ["string"],
                "youtube_title": "string",
                "youtube_description": "string",
                "higgsfield_prompt": "string",
                "shot_plan": ["string"],
                "reach_rationale": ["string"],
            },
        }

        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": settings.anthropic_model,
            "max_tokens": 1400,
            "system": system_prompt,
            "messages": [{"role": "user", "content": json.dumps(user_prompt)}],
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()

        data = response.json()
        text = "".join(block["text"] for block in data["content"] if block["type"] == "text")
        parsed = json.loads(text)
        return ContentBrief.model_validate(parsed)
