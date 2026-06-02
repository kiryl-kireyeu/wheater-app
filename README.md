# Weather Scores App

FastAPI application for a recruitment task. The app fetches hourly weather data from Open-Meteo, calculates weather scores for selected cities, and returns a ranked list from best to worst weather conditions.

The app includes:

- FastAPI backend.
- Swagger/OpenAPI documentation.
- Public city weather scores API.
- Minimal server-rendered HTML UI.
- Unit and API tests.
- Docker support.

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

Minimal UI:

```text
http://127.0.0.1:8000/
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

Current test suite covers scoring, date range resolution, Open-Meteo parsing, API behavior, service orchestration, and web page smoke checks.

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

## Frontend Performance Notes

The UI intentionally uses small vanilla JavaScript and server-served static assets instead of a frontend bundle.

Current choices:

- The script is loaded with `defer`, so it does not block initial HTML rendering.
- JavaScript has no external dependencies.
- CSS and JavaScript are intentionally small.
- The UI performs API requests only after the user clicks `Get Data`.
- Loading and error states are handled in the browser.
- HTTP caching headers can be added later during Docker or production hardening if needed.

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

## Scoring Algorithm

Hourly weather values are aggregated with an arithmetic mean for each metric.

Component scores:

- Temperature:
  - `24°C` gives `10` points.
  - Every degree of deviation subtracts `1` point.
  - Minimum score is `0`.
- Wind speed:
  - `0 m/s` gives `10` points.
  - Every `1 m/s` subtracts `1` point.
  - Minimum score is `0`.
- Relative humidity:
  - `50%` gives `10` points.
  - `0%` and `100%` give `0` points.
  - Values are interpolated linearly around `50%`.
- Cloud cover:
  - `25%` gives `10` points.
  - `0%` and `100%` give `0` points.
  - Values are interpolated linearly from `0 -> 25 -> 100`.

Total score:

```text
temperature_score * 0.35
+ wind_score * 0.20
+ humidity_score * 0.20
+ cloud_score * 0.25
```

## Docker

Make sure Docker Desktop or another Docker daemon is running.

Build the image:

```bash
docker build -t weather-scores-app .
```

Run the container:

```bash
docker run --rm -p 8000:8000 weather-scores-app
```

Then open:

```text
http://127.0.0.1:8000
```

## External API

Weather data source:

- [Open-Meteo Forecast API](https://open-meteo.com/en/docs)
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)

The app uses fixed city coordinates because the task defines a fixed city list and Open-Meteo weather endpoints require coordinates. This avoids unnecessary geocoding calls and keeps responses deterministic.
