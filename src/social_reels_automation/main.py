from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from social_reels_automation.config import get_settings
from social_reels_automation.models import AutomationStatus, PipelineResponse, ReelRequest
from social_reels_automation.services.automation_service import AutomationService
from social_reels_automation.services.content_pipeline import ContentPipeline

pipeline = ContentPipeline()
automation = AutomationService(pipeline)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    await automation.start()
    try:
        yield
    finally:
        await automation.shutdown()


app = FastAPI(title="Social Reels Automation", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request) -> HTMLResponse:
    settings = get_settings()
    checks = [
        ("Gemini API", bool(settings.gemini_api_key)),
        ("Claude API", bool(settings.anthropic_api_key)),
        ("Higgsfield key", bool(settings.higgsfield_api_key)),
        ("Higgsfield secret", bool(settings.higgsfield_api_secret)),
        ("Instagram access token", bool(settings.instagram_access_token)),
        ("Instagram numeric user id", bool(settings.instagram_ig_user_id and settings.instagram_ig_user_id.isdigit())),
        ("YouTube OAuth file", settings.youtube_client_secrets_file.exists()),
        ("Google Sheets id", bool(settings.google_sheets_spreadsheet_id)),
        ("Gmail sender email", bool(settings.gmail_sender_email)),
        ("Stripe secret key", bool(settings.stripe_secret_key)),
    ]
    return templates.TemplateResponse(
        "setup.html",
        {"request": request, "checks": checks},
    )


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/pipelines/reels/run", response_model=PipelineResponse)
async def run_reel_pipeline(reel_request: ReelRequest) -> PipelineResponse:
    return await pipeline.run(reel_request)


@app.get("/automation/status", response_model=AutomationStatus)
async def automation_status() -> AutomationStatus:
    return await automation.status()


@app.post("/automation/run-daily", response_model=list[str])
async def run_daily_automation() -> list[str]:
    return await automation.run_daily_batch()
