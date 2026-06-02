from fastapi.testclient import TestClient

from app.main import app


def test_index_page_renders_minimal_ui() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Weather Scores" in response.text
    assert 'id="start-date"' in response.text
    assert 'id="end-date"' in response.text
    assert 'id="get-data"' in response.text
    assert 'id="scores-table-body"' in response.text


def test_static_assets_are_served() -> None:
    client = TestClient(app)

    script_response = client.get("/static/app.js")
    styles_response = client.get("/static/styles.css")

    assert script_response.status_code == 200
    assert "fetchScores" in script_response.text
    assert styles_response.status_code == 200
    assert ".controls" in styles_response.text
