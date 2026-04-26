"""Pipeline health API routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import PipelineMetric, Anomaly, Recommendation
from backend.models.schemas import PipelineHealthResponse, AnomalyResponse, RecommendationResponse, SystemHealthResponse

router = APIRouter()


@router.get("/pipelines", response_model=List[str])
async def get_all_pipelines(db: Session = Depends(get_db)):
    """Get list of all monitored pipelines"""
    pipelines = (
        db.query(PipelineMetric.pipeline_name)
        .distinct()
        .order_by(PipelineMetric.pipeline_name)
        .all()
    )
    return [p[0] for p in pipelines]


@router.get("/pipelines/{pipeline_name}", response_model=PipelineHealthResponse)
async def get_pipeline_health(
    pipeline_name: str,
    db: Session = Depends(get_db),
):
    """Get comprehensive health status for a specific pipeline"""
    # Get metrics count
    metrics_count = (
        db.query(func.count(PipelineMetric.id))
        .filter(PipelineMetric.pipeline_name == pipeline_name)
        .scalar()
    )

    # Get anomalies
    anomalies = (
        db.query(Anomaly)
        .filter(
            Anomaly.pipeline_name == pipeline_name,
            Anomaly.resolved == False,
        )
        .order_by(Anomaly.detected_at.desc())
        .all()
    )

    # Get recommendations
    recommendations = (
        db.query(Recommendation)
        .filter(
            Recommendation.pipeline_name == pipeline_name,
            Recommendation.implemented == False,
        )
        .order_by(Recommendation.created_at.desc())
        .all()
    )

    # Calculate status
    if not anomalies:
        status = "healthy"
    elif any(a.severity == "critical" for a in anomalies):
        status = "critical"
    elif any(a.severity == "high" for a in anomalies):
        status = "warning"
    else:
        status = "warning"

    return PipelineHealthResponse(
        pipeline_name=pipeline_name,
        status=status,
        last_checked=datetime.utcnow(),
        metrics_count=metrics_count,
        anomalies_count=len(anomalies),
        recent_anomalies=anomalies[:10],
        active_recommendations=recommendations[:5],
    )


@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health(db: Session = Depends(get_db)):
    """Get overall system health"""
    # Count total pipelines
    pipelines_count = (
        db.query(func.count(func.distinct(PipelineMetric.pipeline_name)))
        .scalar()
    )

    # Count active anomalies
    active_anomalies = (
        db.query(func.count(Anomaly.id))
        .filter(Anomaly.resolved == False)
        .scalar()
    )

    # Count pending recommendations
    pending_recs = (
        db.query(func.count(Recommendation.id))
        .filter(Recommendation.implemented == False)
        .scalar()
    )

    # Determine overall status
    if active_anomalies > 10:
        overall_status = "degraded"
    elif active_anomalies > 0:
        overall_status = "degraded" if db.query(Anomaly).filter(
            Anomaly.severity.in_(["critical", "high"]),
            Anomaly.resolved == False,
        ).count() > 0 else "operational"
    else:
        overall_status = "operational"

    return SystemHealthResponse(
        status=overall_status,
        version="1.0.0",
        pipelines_monitored=pipelines_count or 0,
        active_anomalies=active_anomalies or 0,
        pending_recommendations=pending_recs or 0,
        uptime_seconds=3600.0,  # Placeholder
    )
