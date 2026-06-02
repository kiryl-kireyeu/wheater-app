from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.health import router as health_router
from app.api.v1.cities_scores import router as cities_scores_router
from app.core.config import settings
from app.web.routes import router as web_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description=(
            "Weather scoring API that ranks selected cities using hourly weather data "
            "from Open-Meteo."
        ),
        version=settings.app_version,
    )

    # Static assets are served by FastAPI because this task does not need a frontend build step.
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    app.include_router(web_router)
    app.include_router(health_router)
    app.include_router(cities_scores_router)

    return app


app = create_app()
