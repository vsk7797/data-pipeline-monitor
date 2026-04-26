"""Tests for anomaly detection service"""

import pytest
from datetime import datetime, timedelta
from backend.services.anomaly_detector import AnomalyDetector
from backend.models import PipelineMetric


@pytest.fixture
def detector():
    """Create an anomaly detector instance"""
    return AnomalyDetector(threshold=0.8)


def test_detector_initialization():
    """Test anomaly detector initialization"""
    detector = AnomalyDetector(threshold=0.75)
    assert detector.threshold == 0.75


def test_detect_anomalies_with_insufficient_data(client, db, detector):
    """Test anomaly detection with insufficient data"""
    # Create only 2 metrics
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
            "metric_type": "latency",
            "value": 101.0,
        },
    )

    anomalies = detector.detect_anomalies(db, "pipeline", "latency")
    assert len(anomalies) == 0  # Not enough data


def test_detect_outlier_anomaly(client, db, detector):
    """Test detection of outlier values"""
    # Create normal metrics
    for i in range(10):
        client.post(
            "/api/metrics/",
            json={
                "pipeline_name": "pipeline",
                "metric_type": "latency",
                "value": 100.0 + (i % 5),  # Values between 100-104
            },
        )

    # Create an outlier
    client.post(
        "/api/metrics/",
        json={
            "pipeline_name": "pipeline",
            "metric_type": "latency",
            "value": 500.0,  # Significant outlier
        },
    )

    anomalies = detector.detect_anomalies(db, "pipeline", "latency")
    assert len(anomalies) > 0
    assert anomalies[0][1] in ["high", "critical"]  # severity level


def test_classify_severity(detector):
    """Test severity classification"""
    assert detector._classify_severity(0.95) == "critical"
    assert detector._classify_severity(0.8) == "high"
    assert detector._classify_severity(0.6) == "medium"
    assert detector._classify_severity(0.4) == "low"


def test_detect_trend_anomaly(detector):
    """Test trend anomaly detection"""
    # Normal trend
    values = list(range(10))
    result = detector._detect_trend_anomaly(values, "latency")
    assert result is None  # Linear trend is not flagged

    # Sharp increase trend
    values = [100] * 10 + [250] * 5  # 150% increase
    result = detector._detect_trend_anomaly(values, "latency")
    assert result is not None
    assert result[1] in ["high", "medium"]


def test_create_anomaly_record(client, db, detector):
    """Test creating an anomaly record in database"""
    anomaly = detector.create_anomaly_record(
        db,
        pipeline_name="test_pipeline",
        metric_type="latency",
        severity="high",
        description="Test anomaly",
    )

    assert anomaly.id is not None
    assert anomaly.pipeline_name == "test_pipeline"
    assert anomaly.severity == "high"
    assert anomaly.resolved == False


def test_batch_detect_anomalies(client, db, detector):
    """Test batch anomaly detection across pipelines"""
    # Create metrics for multiple pipelines
    for pipeline in ["pipeline_a", "pipeline_b"]:
        for i in range(6):
            client.post(
                "/api/metrics/",
                json={
                    "pipeline_name": pipeline,
                    "metric_type": "latency",
                    "value": 100.0 if i < 5 else 500.0,  # Last one is outlier
                },
            )

    anomalies = detector.batch_detect_anomalies(db, lookback_hours=24)
    # Should detect anomalies in both pipelines
    assert len(anomalies) > 0


def test_anomaly_api_detection(client, db):
    """Test anomaly detection via API"""
    # Create some metrics
    for i in range(6):
        client.post(
            "/api/metrics/",
            json={
                "pipeline_name": "test_pipeline",
                "metric_type": "latency",
                "value": 100.0 if i < 5 else 500.0,
            },
        )

    # Trigger detection
    response = client.post(
        "/api/anomalies/detect?pipeline_name=test_pipeline&metric_type=latency"
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
