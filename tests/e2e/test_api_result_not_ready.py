"""E2E test: GET /result when job not completed returns 409."""

from __future__ import annotations


def test_api_result_not_ready(e2e_client) -> None:
    """POST /jobs run_immediately=false; GET /result without running -> 409."""
    response = e2e_client.post(
        "/jobs",
        json={"topic": "seo tools", "run_immediately": False},
    )
    assert response.status_code == 200
    job_id = response.json()["job"]["id"]

    result_response = e2e_client.get(f"/jobs/{job_id}/result")
    assert result_response.status_code == 409
