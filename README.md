---
title: Reels Automation
emoji: "🎬"
colorFrom: orange
colorTo: red
sdk: docker
app_port: 7860
short_description: Automate daily Instagram Reels and YouTube Shorts with Claude, Higgsfield, and audience-fit trend targeting.
---

# Social Reels Automation

This service helps automate a content workflow:

1. Ask Claude to generate a short-form content angle, script, caption, hashtags, CTA, and metadata.
2. Send the visual prompt to Higgsfield to render a vertical video asset.
3. Download the generated video locally.
4. Publish the result to YouTube Shorts.
5. Publish the same asset to Instagram Reels through the Instagram Graph API.
6. Refresh trend signals daily and post two reels automatically at your configured times.
7. Provide a local website dashboard for manual runs, schedule visibility, and daily batch posting.

## Important limits

- It can help improve consistency, captions, hooks, posting hygiene, and metadata quality.
- It cannot guarantee "good reach". Platform distribution depends on content quality, watch time, audience fit, account history, and platform ranking systems.
- Instagram direct publishing requires a Business or Creator account connected through Meta.
- YouTube upload requires OAuth consent and a local `client_secrets.json`.
- There is no official Instagram or YouTube "latest hashtag" API that guarantees viral tags, so this app derives fresh daily hashtag sets from live trend/news signals and your niche.

## Setup

1. Create a virtual environment and install dependencies:

```powershell
cd D:\Scalar\social-reels-automation
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

2. Copy `.env.example` to `.env` and fill in your secrets.
3. Put your YouTube OAuth app secrets JSON at the path configured by `YOUTUBE_CLIENT_SECRETS_FILE`.
4. Set `AUTOMATION_POST_TIMES` to two local times like `10:00,18:00`.
5. For Hugging Face deployment, set `HF_REPO_ID` and optionally `HF_REPO_TYPE`.

## Run the API

```powershell
cd D:\Scalar\social-reels-automation
.\.venv\Scripts\Activate.ps1
uvicorn social_reels_automation.main:app --reload
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) to use the website dashboard.

## Deploy to Hugging Face

Your snippet is close, but for a working hosted website this project should go to a Hugging Face `space`, not a `model`.

Current Hugging Face docs show:

- `upload_folder(..., repo_type="space")` uploads a whole app folder to a Space
- Docker Spaces support custom containers like FastAPI apps

I added:

- [Dockerfile](D:/Scalar/social-reels-automation/Dockerfile) for Hugging Face Docker Spaces
- [deploy_to_huggingface.py](D:/Scalar/social-reels-automation/scripts/deploy_to_huggingface.py) to automate repo creation and upload

Run it like this:

```powershell
cd D:\Scalar\social-reels-automation
$env:HF_TOKEN="your_huggingface_token"
$env:HF_REPO_ID="Gosula16/Reels"
$env:HF_REPO_TYPE="space"
python .\scripts\deploy_to_huggingface.py
```

If you only want to store the code on the Hub and not host the site, you can set:

```powershell
$env:HF_REPO_TYPE="model"
```

That will upload the files, but it will not run the web app as a hosted site.

## Trigger a reel generation

Example request:

```powershell
$body = @{
  topic = "3 mistakes founders make when pitching investors"
  goal = "educate and build authority"
  style = "cinematic, fast-paced, confident"
  call_to_action = "Follow for more founder growth content"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/pipelines/reels/run `
  -ContentType "application/json" `
  -Body $body
```

## Daily automation

When `AUTOMATION_ENABLED=true`, the app schedules two posts per day using `AUTOMATION_POST_TIMES` in your local timezone.

- `GET /automation/status` shows the configured schedule and recent runs
- `POST /automation/run-daily` immediately creates and posts two reels using fresh trend signals

## What the pipeline returns

The API returns:

- Claude's structured content brief
- Higgsfield request and status IDs
- Downloaded file path
- YouTube video ID and URL when upload succeeds
- Instagram creation and publish IDs when publish succeeds

## Reach optimization built in

The content brief asks Claude to produce:

- a scroll-stopping hook
- a concise spoken script
- strong first-line caption text
- hashtag clusters
- daily refreshed hashtags based on trend inputs
- SEO-friendly YouTube title and description
- a CTA tuned to your audience and niche

For better outcomes, keep these variables strong:

- use a specific audience and topic, not general motivational content
- keep the first 2 seconds visually strong
- keep clips short and easy to rewatch
- publish consistently instead of chasing one viral post
- review analytics and refine prompts based on retention

## Audience targeting logic

The scheduler does not just pick a random trend. It ranks trend topics by overlap with:

- your niche
- your audience description
- your configured topic seeds

This helps the app bias toward better audience-fit ideas instead of broad but irrelevant trends.

## Safe credential handling

Do not paste secrets into source files. Keep them in `.env`, which is meant for local configuration only.
