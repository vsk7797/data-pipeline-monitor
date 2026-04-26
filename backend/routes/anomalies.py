"""Anomalies API routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Anomaly
from backend.models.schemas import AnomalyResponse
from backend.services.anomaly_detector import AnomalyDetector

router = APIRouter()
detector = AnomalyDetector()


@router.get("/", response_model=List[AnomalyResponse])
async def get_anomalies(
    pipeline_name: str = Query(None),
    resolved: bool = Query(None),
    severity: str = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get anomalies with optional filtering.

    Query parameters:
    - pipeline_name: Filter by pipeline name
    - resolved: Filter by resolution status (true/false)
    - severity: Filter by severity level (low, medium, high, critical)
    """
    query = db.query(Anomaly)

    if pipeline_name:
        query = query.filter(Anomaly.pipeline_name == pipeline_name)

    if resolved is not None:
        query = query.filter(Anomaly.resolved == resolved)

    if severity:
        query = query.filter(Anomaly.severity == severity)

    anomalies = query.order_by(Anomaly.detected_at.desc()).all()
    return anomalies


@router.get("/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    """Get a specific anomaly by ID"""
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()

    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    return anomaly


@router.post("/detect", response_model=List[AnomalyResponse])
async def detect_anomalies(
    pipeline_name: str = Query(...),
    metric_type: str = Query(...),
    hours_lookback: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
):
    """
    Manually trigger anomaly detection for a specific metric.

    Returns newly detected anomalies.
    """
    anomalies = detector.detect_anomalies(db, pipeline_name, metric_type, hours_lookback)

    created_anomalies = []
    for score, severity, description in anomalies:
        anomaly = detector.create_anomaly_record(
            db, pipeline_name, metric_type, severity, description
        )
        created_anomalies.append(anomaly)

    return created_anomalies


@router.post("/batch-detect", response_model=List[AnomalyResponse])
async def batch_detect_anomalies(
    lookback_hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
):
    """
    Trigger comprehensive anomaly detection across all pipelines and metrics.

    Scans all collected metrics and creates anomaly records for detected issues.
    """
    created_anomalies = detector.batch_detect_anomalies(db, lookback_hours)
    return created_anomalies


@router.patch("/{anomaly_id}/resolve")
async def resolve_anomaly(
    anomaly_id: int,
    root_cause: str = Query(None),
    db: Session = Depends(get_db),
):
    """Mark an anomaly as resolved"""
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()

    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    anomaly.resolved = True
    if root_cause:
        anomaly.root_cause = root_cause

    db.commit()
    db.refresh(anomaly)

    return {"status": "resolved", "anomaly_id": anomaly_id, "root_cause": anomaly.root_cause}
