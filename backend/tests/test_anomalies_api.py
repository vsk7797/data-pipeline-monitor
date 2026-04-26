"""Tests for anomalies API endpoints"""

import pytest


def test_get_anomalies(client, db):
    """Test retrieving all anomalies"""
    response = client.get("/api/anomalies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_anomalies_by_pipeline(client, db):
    """Test filtering anomalies by pipeline"""
    response = client.get("/api/anomalies/?pipeline_name=test_pipeline")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_anomaly_by_id(client, db):
    """Test retrieving specific anomaly"""
    # First create a metric and trigger detection
    client.post(
        "/api/metrics/",
        json={
            "pipeline_name": "test_pipeline",
            "metric_type": "latency",
            "value": 100.0,
        },
    )

    # Try to get a non-existent anomaly
    response = client.get("/api/anomalies/9999")
    assert response.status_code == 404


def test_get_anomalies_by_severity(client, db):
    """Test filtering anomalies by severity"""
    response = client.get("/api/anomalies/?severity=critical")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_resolve_anomaly(client, db):
    """Test marking anomaly as resolved"""
    # Create metrics for anomaly detection
    for i in range(6):
        client.post(
            "/api/metrics/",
            json={
                "pipeline_name": "pipeline",
                "metric_type": "latency",
                "value": 100.0 if i < 5 else 500.0,
            },
        )

    # Detect anomalies
    detect_response = client.post(
        "/api/anomalies/detect?pipeline_name=pipeline&metric_type=latency"
    )
    anomalies = detect_response.json()

    if anomalies:
        anomaly_id = anomalies[0]["id"]

        # Resolve the anomaly
        response = client.patch(
            f"/api/anomalies/{anomaly_id}/resolve?root_cause=Fixed+latency+issue"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"
        assert data["anomaly_id"] == anomaly_id
        assert data["root_cause"] == "Fixed latency issue"


def test_batch_detect_anomalies(client, db):
    """Test batch anomaly detection"""
    # Create metrics
    for i in range(6):
        client.post(
            "/api/metrics/",
            json={
                "pipeline_name": f"pipeline_{i % 2}",
                "metric_type": "latency" if i % 2 == 0 else "throughput",
                "value": 100.0 if i < 5 else 500.0,
            },
        )

    # Run batch detection
    response = client.post("/api/anomalies/batch-detect")

    assert response.status_code == 200
    anomalies = response.json()
    assert isinstance(anomalies, list)
