"""E2E test: POST /jobs with run_immediately, GET status, GET result."""

from __future__ import annotations

from src.domain.models.job import JobStatus


def test_api_job_flow(e2e_client) -> None:
    """POST /jobs run_immediately=true -> 200, job completed; GET /jobs/{id} and /result work."""
    response = e2e_client.post(
        "/jobs",
        json={"topic": "seo tools", "run_immediately": True},
    )
    assert response.status_code == 200
    data = response.json()
    job = data["job"]
    job_id = job["id"]
    assert job["status"] in (JobStatus.COMPLETED.value, JobStatus.FAILED.value)

    get_response = e2e_client.get(f"/jobs/{job_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == job["status"]

    if job["status"] == JobStatus.COMPLETED.value:
        result_response = e2e_client.get(f"/jobs/{job_id}/result")
        assert result_response.status_code == 200
        result = result_response.json()["result"]
        assert "seo_meta" in result
        assert "article_markdown" in result
