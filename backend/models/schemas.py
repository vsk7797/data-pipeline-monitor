"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MetricBase(BaseModel):
    """Base schema for pipeline metrics"""

    pipeline_name: str = Field(..., description="Name of the pipeline")
    metric_type: str = Field(..., description="Type of metric (latency, throughput, error_rate)")
    value: float = Field(..., description="Metric value")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MetricCreate(MetricBase):
    """Schema for creating metrics"""

    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class MetricResponse(MetricBase):
    """Schema for metric responses"""

    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AnomalyBase(BaseModel):
    """Base schema for anomalies"""

    pipeline_name: str
    metric_type: str
    severity: str = Field(..., description="Severity level: low, medium, high, critical")
    description: str


class AnomalyCreate(AnomalyBase):
    """Schema for creating anomalies"""

    pass


class AnomalyResponse(AnomalyBase):
    """Schema for anomaly responses"""

    id: int
    detected_at: datetime
    resolved: bool
    root_cause: Optional[str] = None

    class Config:
        from_attributes = True


class RecommendationBase(BaseModel):
    """Base schema for recommendations"""

    pipeline_name: str
    title: str
    description: str
    impact: str = Field(..., description="Impact level: High, Medium, Low")
    implementation_steps: List[str]
    estimated_improvement: str


class RecommendationCreate(RecommendationBase):
    """Schema for creating recommendations"""

    anomaly_id: Optional[int] = None


class RecommendationResponse(RecommendationBase):
    """Schema for recommendation responses"""

    id: int
    anomaly_id: Optional[int]
    created_at: datetime
    implemented: bool

    class Config:
        from_attributes = True


class PipelineHealthResponse(BaseModel):
    """Schema for pipeline health status"""

    pipeline_name: str
    status: str = Field(..., description="Status: healthy, warning, critical")
    last_checked: datetime
    metrics_count: int
    anomalies_count: int
    recent_anomalies: List[AnomalyResponse]
    active_recommendations: List[RecommendationResponse]


class SystemHealthResponse(BaseModel):
    """Schema for system health"""

    status: str = Field(..., description="Status: operational, degraded, down")
    version: str
    pipelines_monitored: int
    active_anomalies: int
    pending_recommendations: int
    uptime_seconds: float
