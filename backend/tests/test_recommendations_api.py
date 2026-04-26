"""Tests for recommendations API endpoints"""

import pytest


def test_get_recommendations(client, db):
    """Test retrieving all recommendations"""
    response = client.get("/api/recommendations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_recommendations_by_pipeline(client, db):
    """Test filtering recommendations by pipeline"""
    response = client.get("/api/recommendations/?pipeline_name=test_pipeline")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_recommendations_by_impact(client, db):
    """Test filtering recommendations by impact"""
    response = client.get("/api/recommendations/?impact=High")
    assert response.status_code == 200
    data = response.json()
    if data:
        assert all(r["impact"] == "High" for r in data)


def test_get_recommendation_by_id(client, db):
    """Test retrieving specific recommendation"""
    response = client.get("/api/recommendations/9999")
    assert response.status_code == 404


def test_mark_recommendation_implemented(client, db):
    """Test marking recommendation as implemented"""
    # Create metrics and trigger anomaly detection
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

        # Generate recommendation
        gen_response = client.post(
            f"/api/recommendations/generate?anomaly_id={anomaly_id}"
        )

        if gen_response.status_code == 200:
            recommendation = gen_response.json()
            rec_id = recommendation["id"]

            # Mark as implemented
            response = client.patch(f"/api/recommendations/{rec_id}/implement")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "marked_implemented"


def test_generate_recommendation(client, db):
    """Test generating recommendation for anomaly"""
    # Create and detect anomaly first
    for i in range(6):
        client.post(
            "/api/metrics/",
            json={
                "pipeline_name": "pipeline",
                "metric_type": "latency",
                "value": 100.0 if i < 5 else 500.0,
            },
        )

    detect_response = client.post(
        "/api/anomalies/detect?pipeline_name=pipeline&metric_type=latency"
    )
    anomalies = detect_response.json()

    if anomalies:
        anomaly_id = anomalies[0]["id"]
        response = client.post(f"/api/recommendations/generate?anomaly_id={anomaly_id}")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "description" in data
        assert "implementation_steps" in data


def test_batch_generate_recommendations(client, db):
    """Test batch generation of recommendations"""
    # Create multiple metrics with anomalies
    for pipeline in ["pipeline_a", "pipeline_b"]:
        for i in range(6):
            client.post(
                "/api/metrics/",
                json={
                    "pipeline_name": pipeline,
                    "metric_type": "latency",
                    "value": 100.0 if i < 5 else 500.0,
                },
            )

    # Detect anomalies
    client.post("/api/anomalies/batch-detect")

    # Generate recommendations
    response = client.post("/api/recommendations/batch-generate")

    assert response.status_code == 200
    recommendations = response.json()
    assert isinstance(recommendations, list)
