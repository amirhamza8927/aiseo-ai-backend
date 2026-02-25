"""E2E test: POST /jobs run_immediately=false, then POST /run, GET result."""

from __future__ import annotations

from src.domain.models.job import JobStatus


def test_api_deferred_run(e2e_client) -> None:
    """POST /jobs run_immediately=false -> pending; POST /run -> complete; GET result works."""
    response = e2e_client.post(
        "/jobs",
        json={"topic": "seo tools", "run_immediately": False},
    )
    assert response.status_code == 200
    job = response.json()["job"]
    job_id = job["id"]
    assert job["status"] == JobStatus.PENDING.value

    run_response = e2e_client.post(f"/jobs/{job_id}/run")
    assert run_response.status_code == 200
    assert run_response.json()["status"] == JobStatus.COMPLETED.value

    result_response = e2e_client.get(f"/jobs/{job_id}/result")
    assert result_response.status_code == 200
    assert "seo_meta" in result_response.json()["result"]
