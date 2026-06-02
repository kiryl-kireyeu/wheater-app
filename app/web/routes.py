from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the minimal UI for requesting ranked weather scores."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"page_title": "Weather Scores"},
    )
