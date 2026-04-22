from fastapi.testclient import TestClient

from app.main import create_app


def test_stage_four_routes_are_registered() -> None:
    client = TestClient(create_app())

    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/study-sessions" in paths
    assert "/api/reviews/next" in paths
    assert "/api/reviews/answer" in paths
    assert "/api/study-sessions/{session_id}/finish" in paths


def test_stage_five_routes_are_registered() -> None:
    client = TestClient(create_app())

    paths = client.get("/openapi.json").json()["paths"]

    assert "get" in paths["/api/study-sessions"]
    assert "/api/study-sessions/{session_id}" in paths
