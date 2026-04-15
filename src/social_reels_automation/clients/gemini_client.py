from __future__ import annotations

import json

import httpx

from social_reels_automation.clients.prompt_builder import build_content_prompts
from social_reels_automation.config import get_settings
from social_reels_automation.models import ContentBrief, ReelRequest, TrendSnapshot


class GeminiClient:
    api_url_template = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "{model}:generateContent?key={api_key}"
    )

    async def create_content_brief(
        self,
        reel_request: ReelRequest,
        trends: list[TrendSnapshot],
    ) -> ContentBrief:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required to generate content briefs with Gemini.")

        system_prompt, user_prompt = build_content_prompts(reel_request, trends)
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.8,
                "responseMimeType": "application/json",
            },
        }
        url = self.api_url_template.format(
            model=settings.gemini_model,
            api_key=settings.gemini_api_key,
        )

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return ContentBrief.model_validate(json.loads(text))
