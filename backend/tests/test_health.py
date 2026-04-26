"""Tests for health/status endpoints"""

import pytest


def test_health_check(client):
    """Test basic health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data
    assert "timestamp" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "endpoints" in data


def test_system_health(client, db):
    """Test system health endpoint"""
    response = client.get("/api/system-health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "pipelines_monitored" in data
    assert "active_anomalies" in data
    assert "pending_recommendations" in data
    assert "uptime_seconds" in data


def test_get_all_pipelines(client, db):
    """Test getting list of all pipelines"""
    # Create metrics for different pipelines
    for pipeline in ["pipeline_a", "pipeline_b", "pipeline_c"]:
        client.post(
            "/api/metrics/",
            json={
                "pipeline_name": pipeline,
                "metric_type": "latency",
                "value": 100.0,
            },
        )

    response = client.get("/api/pipelines")

    assert response.status_code == 200
    pipelines = response.json()
    assert isinstance(pipelines, list)
    assert len(pipelines) == 3
    assert "pipeline_a" in pipelines
    assert "pipeline_b" in pipelines
    assert "pipeline_c" in pipelines


def test_get_pipeline_health(client, db):
    """Test getting health of specific pipeline"""
    # Create metrics
    client.post(
        "/api/metrics/",
        json={
            "pipeline_name": "test_pipeline",
            "metric_type": "latency",
            "value": 100.0,
        },
    )

    response = client.get("/api/pipelines/test_pipeline")

    assert response.status_code == 200
    data = response.json()
    assert data["pipeline_name"] == "test_pipeline"
    assert "status" in data
    assert "last_checked" in data
    assert "metrics_count" in data
    assert "anomalies_count" in data
    assert "recent_anomalies" in data
    assert "active_recommendations" in data


def test_get_nonexistent_pipeline_health(client, db):
    """Test getting health of non-existent pipeline"""
    response = client.get("/api/pipelines/nonexistent_pipeline")

    assert response.status_code == 200
    data = response.json()
    assert data["pipeline_name"] == "nonexistent_pipeline"
    assert data["metrics_count"] == 0
    assert data["anomalies_count"] == 0
