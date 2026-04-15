from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import uuid4

import httpx

from social_reels_automation.config import get_settings
from social_reels_automation.models import ContentBrief, HiggsfieldGenerationResult


class HiggsfieldClient:
    def __init__(self) -> None:
        self._auth_header: str | None = None

    async def generate_video(self, brief: ContentBrief) -> HiggsfieldGenerationResult:
        settings = get_settings()
        if not settings.higgsfield_api_key or not settings.higgsfield_api_secret:
            raise RuntimeError("HIGGSFIELD_API_KEY and HIGGSFIELD_API_SECRET are required.")
        self._auth_header = f"Key {settings.higgsfield_api_key}:{settings.higgsfield_api_secret}"
        url = f"{settings.higgsfield_base_url.rstrip('/')}{settings.higgsfield_video_path}"
        payload = {
            "prompt": brief.higgsfield_prompt,
            "aspect_ratio": "9:16",
            "resolution": "720p",
        }
        headers = {
            "Authorization": self._auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            accepted = response.json()

            status_url = accepted["status_url"]
            request_id = accepted["request_id"]
            final = await self._wait_for_completion(client, status_url)

        return HiggsfieldGenerationResult(
            request_id=request_id,
            status_url=status_url,
            asset_url=final["video"]["url"],
        )

    async def _wait_for_completion(self, client: httpx.AsyncClient, status_url: str) -> dict:
        if not self._auth_header:
            raise RuntimeError("Higgsfield authorization is not initialized.")
        for _ in range(60):
            status_response = await client.get(
                status_url,
                headers={"Authorization": self._auth_header, "Accept": "application/json"},
            )
            status_response.raise_for_status()
            data = status_response.json()
            status = data.get("status")
            if status == "completed":
                return data
            if status in {"failed", "nsfw"}:
                raise RuntimeError(f"Higgsfield generation finished with status '{status}'.")
            await asyncio.sleep(2)
        raise TimeoutError("Timed out waiting for Higgsfield video generation.")

    async def download_asset(self, asset_url: str, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"reel-{uuid4().hex}.mp4"
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.get(asset_url, follow_redirects=True)
            response.raise_for_status()
            output_path.write_bytes(response.content)
        return output_path
