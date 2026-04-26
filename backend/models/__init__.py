"""Models package"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from backend.database import Base
from datetime import datetime


class PipelineMetric(Base):
    """Database model for pipeline metrics"""

    __tablename__ = "pipeline_metrics"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_name = Column(String, index=True)
    metric_type = Column(String, index=True)  # e.g., "latency", "throughput", "error_rate"
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Anomaly(Base):
    """Database model for detected anomalies"""

    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_name = Column(String, index=True)
    metric_type = Column(String)
    severity = Column(String)  # "low", "medium", "high", "critical"
    description = Column(String)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved = Column(Boolean, default=False)
    root_cause = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    """Database model for AI-generated optimization recommendations"""

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_name = Column(String, index=True)
    anomaly_id = Column(Integer, nullable=True)
    title = Column(String)
    description = Column(String)
    impact = Column(String)  # e.g., "High", "Medium", "Low"
    implementation_steps = Column(JSON)  # Array of steps
    estimated_improvement = Column(String)  # e.g., "20-30% faster"
    created_at = Column(DateTime, default=datetime.utcnow)
    implemented = Column(Boolean, default=False)


class Alert(Base):
    """Database model for alerts"""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_name = Column(String, index=True)
    anomaly_id = Column(Integer)
    alert_type = Column(String)  # "email", "webhook", "in_app"
    status = Column(String)  # "pending", "sent", "acknowledged"
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
