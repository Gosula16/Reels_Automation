from __future__ import annotations

import os
from pathlib import Path

from huggingface_hub import HfApi, login, upload_folder


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    token = os.getenv("HF_TOKEN")
    repo_id = os.getenv("HF_REPO_ID", "Gosula16/Reels")
    repo_type = os.getenv("HF_REPO_TYPE", "space")
    space_sdk = os.getenv("HF_SPACE_SDK", "docker")

    api = HfApi(token=token)
    if token:
        login(token=token)
    else:
        # Reuse cached local auth if available; avoid interactive prompts for CI or scripted deploys.
        api.whoami()

    create_kwargs: dict[str, object] = {"repo_id": repo_id, "repo_type": repo_type, "exist_ok": True}
    if repo_type == "space":
        create_kwargs["space_sdk"] = space_sdk
    api.create_repo(**create_kwargs)

    api.upload_folder(
        folder_path=str(ROOT),
        repo_id=repo_id,
        repo_type=repo_type,
        ignore_patterns=[
            ".git/*",
            ".venv/*",
            "__pycache__/*",
            "*.pyc",
            "generated/*",
            "youtube_token.json",
            "client_secrets.json",
            ".env",
        ],
    )

    print(f"Uploaded {ROOT} to https://huggingface.co/{'spaces/' if repo_type == 'space' else ''}{repo_id}")


if __name__ == "__main__":
    main()
