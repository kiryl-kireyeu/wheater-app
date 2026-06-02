# Weather Scores App

FastAPI application for a recruitment task. The app will fetch hourly weather data from Open-Meteo, calculate weather scores for selected cities, and return a ranked list from best to worst weather conditions.

Current implementation includes the FastAPI app setup, Swagger/OpenAPI metadata, health check endpoint, and the public city weather scores API.

## Requirements

- Python 3.11+
- `pip`

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install runtime and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

## Run The App

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Tests

Run tests:

```bash
pytest
```

## Formatting And Linting

Format code:

```bash
ruff format .
```

Run lint checks:

```bash
ruff check .
```

Run lint checks with auto-fix:

```bash
ruff check . --fix
```

## Git Hooks

Git hooks are stored in `.githooks`.

Configured behavior:

- `pre-commit`: runs `ruff format .` and `ruff check . --fix`.
- `pre-push`: runs `pytest`.

If hooks are not active locally, enable them with:

```bash
git config core.hooksPath .githooks
```

## Main Endpoint

Get ranked city weather scores:

```text
GET /api/v1/cities-scores?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

Both query parameters are optional. If omitted, the app will use yesterday as the default date range.

Example:

```bash
curl "http://127.0.0.1:8000/api/v1/cities-scores?start_date=2026-06-01&end_date=2026-06-01"
```

The endpoint returns a sorted list of cities with aggregated weather data and calculated scores.

Dates must point to historical data. `end_date` cannot be later than yesterday.
