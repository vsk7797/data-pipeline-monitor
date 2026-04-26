"""Metrics API routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import PipelineMetric
from backend.models.schemas import MetricCreate, MetricResponse

router = APIRouter()


@router.post("/", response_model=MetricResponse, status_code=201)
async def create_metric(
    metric: MetricCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new pipeline metric.

    This endpoint accepts metric data from pipeline monitoring systems and stores it
    for anomaly detection and analysis.
    """
    db_metric = PipelineMetric(
        pipeline_name=metric.pipeline_name,
        metric_type=metric.metric_type,
        value=metric.value,
        timestamp=metric.timestamp,
        metadata=metric.metadata,
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


@router.post("/batch", response_model=List[MetricResponse], status_code=201)
async def create_metrics_batch(
    metrics: List[MetricCreate],
    db: Session = Depends(get_db),
):
    """
    Create multiple metrics in a single request (batch operation).

    Useful for ingesting metrics from multiple pipeline stages at once.
    """
    if len(metrics) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Batch size exceeded. Maximum 1000 metrics per request.",
        )

    db_metrics = []
    for metric in metrics:
        db_metric = PipelineMetric(
            pipeline_name=metric.pipeline_name,
            metric_type=metric.metric_type,
            value=metric.value,
            timestamp=metric.timestamp,
            metadata=metric.metadata,
        )
        db_metrics.append(db_metric)

    db.add_all(db_metrics)
    db.commit()

    for metric in db_metrics:
        db.refresh(metric)

    return db_metrics


@router.get("/", response_model=List[MetricResponse])
async def get_metrics(
    pipeline_name: str = Query(None),
    metric_type: str = Query(None),
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
):
    """
    Get metrics with optional filtering.

    Query parameters:
    - pipeline_name: Filter by pipeline name
    - metric_type: Filter by metric type (latency, throughput, error_rate)
    - hours: Retrieve metrics from the last N hours (default: 24)
    """
    query = db.query(PipelineMetric)

    if pipeline_name:
        query = query.filter(PipelineMetric.pipeline_name == pipeline_name)

    if metric_type:
        query = query.filter(PipelineMetric.metric_type == metric_type)

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    query = query.filter(PipelineMetric.timestamp >= cutoff_time)

    metrics = query.order_by(PipelineMetric.timestamp.desc()).all()
    return metrics


@router.get("/pipeline/{pipeline_name}", response_model=List[MetricResponse])
async def get_pipeline_metrics(
    pipeline_name: str,
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
):
    """
    Get all metrics for a specific pipeline.

    Returns all metrics from the specified pipeline in the last N hours.
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    metrics = (
        db.query(PipelineMetric)
        .filter(
            PipelineMetric.pipeline_name == pipeline_name,
            PipelineMetric.timestamp >= cutoff_time,
        )
        .order_by(PipelineMetric.timestamp.desc())
        .all()
    )

    return metrics


@router.get("/{metric_id}", response_model=MetricResponse)
async def get_metric(metric_id: int, db: Session = Depends(get_db)):
    """Get a specific metric by ID"""
    metric = db.query(PipelineMetric).filter(PipelineMetric.id == metric_id).first()

    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    return metric
