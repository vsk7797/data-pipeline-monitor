"""Anomaly detection service using statistical methods and LLM analysis"""

import logging
import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from statistics import mean, stdev, StatisticsError
from sqlalchemy.orm import Session

from backend.models import PipelineMetric, Anomaly
from backend.models.schemas import AnomalyCreate, AnomalyResponse
from backend.config import settings

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detects anomalies in pipeline metrics using statistical analysis"""

    def __init__(self, threshold: float = 0.8):
        """
        Initialize anomaly detector

        Args:
            threshold: Confidence threshold for flagging anomalies (0-1)
        """
        self.threshold = threshold

    def detect_anomalies(
        self,
        db: Session,
        pipeline_name: str,
        metric_type: str,
        hours_lookback: int = 24,
    ) -> List[Tuple[float, str, str]]:
        """
        Detect anomalies for a specific metric in a pipeline.

        Returns list of tuples: (severity_score, severity_level, description)
        """
        # Get historical metrics
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_lookback)
        metrics = (
            db.query(PipelineMetric)
            .filter(
                PipelineMetric.pipeline_name == pipeline_name,
                PipelineMetric.metric_type == metric_type,
                PipelineMetric.timestamp >= cutoff_time,
            )
            .order_by(PipelineMetric.timestamp.asc())
            .all()
        )

        if len(metrics) < 5:
            logger.warning(
                f"Insufficient data for anomaly detection: {len(metrics)} metrics"
            )
            return []

        values = [m.value for m in metrics]
        anomalies = []

        # Statistical anomaly detection
        try:
            mean_val = mean(values)
            stdev_val = stdev(values) if len(values) > 1 else 0

            if stdev_val == 0:
                logger.info("No variance in metrics, skipping detection")
                return []

            # Check recent value
            recent_value = values[-1]
            z_score = abs((recent_value - mean_val) / stdev_val) if stdev_val > 0 else 0

            severity_score = min(z_score / 3.0, 1.0)  # Normalize to 0-1

            if severity_score > self.threshold:
                severity = self._classify_severity(severity_score)
                description = (
                    f"Metric {metric_type} for {pipeline_name}: "
                    f"Current value {recent_value:.2f} deviates significantly from "
                    f"average {mean_val:.2f} (Z-score: {z_score:.2f})"
                )

                anomalies.append((severity_score, severity, description))
                logger.info(f"Anomaly detected: {description}")

        except StatisticsError as e:
            logger.error(f"Error calculating statistics: {str(e)}")

        # Check for trend anomalies
        trend_result = self._detect_trend_anomaly(values, metric_type)
        if trend_result:
            anomalies.append(trend_result)

        return anomalies

    def _classify_severity(self, score: float) -> str:
        """Classify severity based on anomaly score"""
        if score >= 0.9:
            return "critical"
        elif score >= 0.7:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"

    def _detect_trend_anomaly(
        self, values: List[float], metric_type: str
    ) -> Optional[Tuple[float, str, str]]:
        """Detect sustained trend anomalies"""
        if len(values) < 10:
            return None

        recent = values[-5:]  # Last 5 values
        older = values[-10:-5]  # Values from 10-5 points ago

        recent_mean = mean(recent)
        older_mean = mean(older)

        # Check if there's a significant trend
        percent_change = abs(recent_mean - older_mean) / (older_mean or 1) * 100

        if percent_change > 50:  # 50% change indicates trend
            severity = "high" if percent_change > 100 else "medium"
            description = (
                f"Significant {'increase' if recent_mean > older_mean else 'decrease'} "
                f"trend detected in {metric_type}: {percent_change:.1f}% change"
            )
            return (percent_change / 100.0, severity, description)

        return None

    def create_anomaly_record(
        self,
        db: Session,
        pipeline_name: str,
        metric_type: str,
        severity: str,
        description: str,
    ) -> Anomaly:
        """Create and save an anomaly record to the database"""
        anomaly = Anomaly(
            pipeline_name=pipeline_name,
            metric_type=metric_type,
            severity=severity,
            description=description,
        )
        db.add(anomaly)
        db.commit()
        db.refresh(anomaly)
        logger.info(f"Anomaly record created: ID={anomaly.id}, {description}")
        return anomaly

    def batch_detect_anomalies(
        self, db: Session, lookback_hours: int = 24
    ) -> List[Anomaly]:
        """
        Scan all pipelines and metrics for anomalies.

        Returns list of newly created anomaly records.
        """
        # Get unique pipeline/metric combinations
        pipeline_metrics = (
            db.query(PipelineMetric.pipeline_name, PipelineMetric.metric_type)
            .distinct()
            .all()
        )

        created_anomalies = []

        for pipeline_name, metric_type in pipeline_metrics:
            anomalies = self.detect_anomalies(db, pipeline_name, metric_type, lookback_hours)

            for score, severity, description in anomalies:
                anomaly = self.create_anomaly_record(
                    db, pipeline_name, metric_type, severity, description
                )
                created_anomalies.append(anomaly)

        return created_anomalies
