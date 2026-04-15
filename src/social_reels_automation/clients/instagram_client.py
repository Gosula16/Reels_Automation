from __future__ import annotations

import asyncio

import httpx

from social_reels_automation.config import get_settings


class InstagramClient:
    @property
    def _base_url(self) -> str:
        settings = get_settings()
        if not settings.instagram_ig_user_id:
            raise RuntimeError("INSTAGRAM_IG_USER_ID is required for Instagram publishing.")
        return (
            f"https://graph.facebook.com/{settings.instagram_graph_version}/"
            f"{settings.instagram_ig_user_id}"
        )

    async def publish_reel(self, *, video_url: str, caption: str) -> tuple[str, str]:
        settings = get_settings()
        if not settings.instagram_access_token:
            raise RuntimeError("INSTAGRAM_ACCESS_TOKEN is required for Instagram publishing.")
        async with httpx.AsyncClient(timeout=60) as client:
            create_response = await client.post(
                f"{self._base_url}/media",
                data={
                    "media_type": "REELS",
                    "video_url": video_url,
                    "caption": caption,
                    "share_to_feed": str(settings.instagram_share_to_feed).lower(),
                    "access_token": settings.instagram_access_token,
                },
            )
            create_response.raise_for_status()
            creation_id = create_response.json()["id"]

            await self._wait_until_ready(client, creation_id)

            publish_response = await client.post(
                f"{self._base_url}/media_publish",
                data={
                    "creation_id": creation_id,
                    "access_token": settings.instagram_access_token,
                },
            )
            publish_response.raise_for_status()
            publish_id = publish_response.json()["id"]

        return creation_id, publish_id

    async def _wait_until_ready(self, client: httpx.AsyncClient, creation_id: str) -> None:
        settings = get_settings()
        status_url = (
            f"https://graph.facebook.com/{settings.instagram_graph_version}/{creation_id}"
        )
        for _ in range(40):
            response = await client.get(
                status_url,
                params={
                    "fields": "status_code",
                    "access_token": settings.instagram_access_token,
                },
            )
            response.raise_for_status()
            status = response.json().get("status_code")
            if status == "FINISHED":
                return
            if status in {"ERROR", "EXPIRED"}:
                raise RuntimeError(f"Instagram container status is '{status}'.")
            await asyncio.sleep(5)
        raise TimeoutError("Instagram media container was not ready in time.")
