"""Tests for metrics endpoints"""

import pytest
from datetime import datetime
from backend.models import PipelineMetric
from backend.models.schemas import MetricCreate


def test_create_single_metric(client, db):
    """Test creating a single metric"""
    metric_data = {
        "pipeline_name": "etl_pipeline",
        "metric_type": "latency",
        "value": 123.45,
        "metadata": {"stage": "transform"},
    }

    response = client.post("/api/metrics/", json=metric_data)

    assert response.status_code == 201
    data = response.json()
    assert data["pipeline_name"] == "etl_pipeline"
    assert data["metric_type"] == "latency"
    assert data["value"] == 123.45
    assert "id" in data
    assert "created_at" in data


def test_create_batch_metrics(client, db):
    """Test creating multiple metrics at once"""
    metrics_data = [
        {
            "pipeline_name": "etl_pipeline",
            "metric_type": "latency",
            "value": 100.0,
        },
        {
            "pipeline_name": "etl_pipeline",
            "metric_type": "throughput",
            "value": 500.0,
        },
        {
            "pipeline_name": "ml_pipeline",
            "metric_type": "error_rate",
            "value": 0.02,
        },
    ]

    response = client.post("/api/metrics/batch", json=metrics_data)

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 3
    assert all("id" in m for m in data)


def test_batch_size_limit(client, db):
    """Test that batch size is limited"""
    metrics_data = [
        {
            "pipeline_name": "pipeline",
            "metric_type": "latency",
            "value": 100.0,
        }
    ] * 1001

    response = client.post("/api/metrics/batch", json=metrics_data)

    assert response.status_code == 400
    assert "exceeded" in response.json()["detail"].lower()


def test_get_all_metrics(client, db):
    """Test retrieving all metrics"""
    # Create test metrics
    for i in range(3):
        client.post(
            "/api/metrics/",
            json={
                "pipeline_name": "test_pipeline",
                "metric_type": "latency",
                "value": 100.0 + i,
            },
        )

    response = client.get("/api/metrics/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_get_metrics_by_pipeline(client, db):
    """Test filtering metrics by pipeline name"""
    # Create metrics for different pipelines
    client.post(
        "/api/metrics/",
        json={
            "pipeline_name": "pipeline_a",
            "metric_type": "latency",
            "value": 100.0,
        },
    )

    client.post(
        "/api/metrics/",
        json={
            "pipeline_name": "pipeline_b",
            "metric_type": "latency",
            "value": 200.0,
        },
    )

    response = client.get("/api/metrics/?pipeline_name=pipeline_a")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["pipeline_name"] == "pipeline_a"


def test_get_metrics_by_type(client, db):
    """Test filtering metrics by metric type"""
    client.post(
        "/api/metrics/",
        json={
            "pipeline_name": "pipeline",
            "metric_type": "latency",
            "value": 100.0,
        },
    )

    client.post(
        "/api/metrics/",
        json={
            "pipeline_name": "pipeline",
            "metric_type": "throughput",
            "value": 500.0,
        },
    )

    response = client.get("/api/metrics/?metric_type=latency")

    assert response.status_code == 200
    data = response.json()
    assert all(m["metric_type"] == "latency" for m in data)


def test_get_specific_metric(client, db):
    """Test retrieving a specific metric by ID"""
    # Create a metric
    create_response = client.post(
        "/api/metrics/",
        json={
            "pipeline_name": "pipeline",
            "metric_type": "latency",
            "value": 100.0,
        },
    )
    metric_id = create_response.json()["id"]

    # Get the metric
    response = client.get(f"/api/metrics/{metric_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == metric_id
    assert data["value"] == 100.0


def test_get_nonexistent_metric(client, db):
    """Test retrieving a non-existent metric"""
    response = client.get("/api/metrics/9999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_pipeline_metrics_by_name(client, db):
    """Test getting all metrics for a specific pipeline"""
    pipeline_name = "test_etl"

    # Create multiple metrics for the same pipeline
    for i in range(5):
        client.post(
            "/api/metrics/",
            json={
                "pipeline_name": pipeline_name,
                "metric_type": "latency" if i % 2 == 0 else "throughput",
                "value": 100.0 + i,
            },
        )

    response = client.get(f"/api/metrics/pipeline/{pipeline_name}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert all(m["pipeline_name"] == pipeline_name for m in data)
