"""AI-powered optimization recommendations engine"""

import logging
import json
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.models import Recommendation, Anomaly
from backend.config import settings

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates optimization recommendations using LLM and heuristics"""

    def __init__(self):
        """Initialize the recommendation engine"""
        self.llm_available = bool(settings.openai_api_key)
        if not self.llm_available:
            logger.warning("OpenAI API key not configured. Using heuristic recommendations only.")

    def generate_recommendations(
        self,
        db: Session,
        anomaly: Anomaly,
    ) -> Recommendation:
        """
        Generate optimization recommendations for an anomaly.

        Uses LLM if available, falls back to heuristic recommendations.
        """
        if self.llm_available:
            return self._generate_llm_recommendation(db, anomaly)
        else:
            return self._generate_heuristic_recommendation(db, anomaly)

    def _generate_llm_recommendation(
        self,
        db: Session,
        anomaly: Anomaly,
    ) -> Recommendation:
        """Generate recommendation using LLM (simulated for now)"""
        # In production, this would call OpenAI API
        # For now, we'll use heuristic approach

        prompt = f"""
        Analyze this pipeline anomaly and provide optimization recommendations:
        
        Pipeline: {anomaly.pipeline_name}
        Metric Type: {anomaly.metric_type}
        Severity: {anomaly.severity}
        Description: {anomaly.description}
        
        Provide:
        1. Root cause analysis
        2. Specific implementation steps
        3. Expected improvement percentage
        4. Impact level (High/Medium/Low)
        """

        logger.info(f"Generating LLM recommendation for anomaly {anomaly.id}")

        # Fallback to heuristic for now
        return self._generate_heuristic_recommendation(db, anomaly)

    def _generate_heuristic_recommendation(
        self,
        db: Session,
        anomaly: Anomaly,
    ) -> Recommendation:
        """Generate recommendation using heuristics"""
        recommendations_map = self._get_heuristic_recommendations()
        
        key = f"{anomaly.metric_type}_{anomaly.severity}"
        rec_data = recommendations_map.get(key, recommendations_map.get("default"))

        recommendation = Recommendation(
            pipeline_name=anomaly.pipeline_name,
            anomaly_id=anomaly.id,
            title=rec_data["title"],
            description=rec_data["description"],
            impact=rec_data["impact"],
            implementation_steps=rec_data["steps"],
            estimated_improvement=rec_data["improvement"],
        )

        db.add(recommendation)
        db.commit()
        db.refresh(recommendation)

        logger.info(
            f"Heuristic recommendation created for anomaly {anomaly.id}: {recommendation.title}"
        )

        return recommendation

    def _get_heuristic_recommendations(self) -> dict:
        """Map of anomaly patterns to recommendations"""
        return {
            "latency_critical": {
                "title": "Optimize Pipeline Parallelization",
                "description": (
                    "Critical latency detected. Implement parallel processing for independent stages "
                    "to reduce end-to-end execution time."
                ),
                "impact": "High",
                "steps": [
                    "Identify independent pipeline stages",
                    "Implement async processing where applicable",
                    "Add connection pooling for database queries",
                    "Consider horizontal scaling of compute resources",
                    "Profile bottlenecks using distributed tracing",
                ],
                "improvement": "30-50% latency reduction",
            },
            "latency_high": {
                "title": "Implement Caching Strategy",
                "description": (
                    "High latency detected. Implement caching for frequently accessed data "
                    "and computed values."
                ),
                "impact": "Medium",
                "steps": [
                    "Identify cacheable data segments",
                    "Implement Redis/Memcached layer",
                    "Add cache invalidation strategy",
                    "Monitor cache hit rates",
                ],
                "improvement": "20-35% latency reduction",
            },
            "throughput_critical": {
                "title": "Scale Processing Capacity",
                "description": (
                    "Critical throughput degradation. Increase processing capacity and optimize "
                    "resource utilization."
                ),
                "impact": "High",
                "steps": [
                    "Add more worker nodes",
                    "Implement batch processing for efficiency",
                    "Optimize memory usage",
                    "Consider queue-based architecture",
                ],
                "improvement": "40-60% throughput improvement",
            },
            "error_rate_high": {
                "title": "Implement Error Recovery and Monitoring",
                "description": (
                    "High error rate detected. Implement robust error handling, retries, "
                    "and better monitoring."
                ),
                "impact": "High",
                "steps": [
                    "Add exponential backoff retry logic",
                    "Implement circuit breaker pattern",
                    "Add detailed error logging",
                    "Set up alerts for error spikes",
                    "Review and update error handling code",
                ],
                "improvement": "50-70% error reduction",
            },
            "error_rate_medium": {
                "title": "Improve Data Validation",
                "description": (
                    "Moderate error rate detected. Improve input validation and data quality checks."
                ),
                "impact": "Medium",
                "steps": [
                    "Add schema validation for inputs",
                    "Implement data quality checks",
                    "Add logging for validation failures",
                    "Test edge cases",
                ],
                "improvement": "25-40% error reduction",
            },
            "default": {
                "title": "Review Pipeline Configuration",
                "description": (
                    "Anomaly detected in pipeline. Review configuration and resource allocation "
                    "for optimization opportunities."
                ),
                "impact": "Medium",
                "steps": [
                    "Audit current pipeline configuration",
                    "Review resource allocation",
                    "Check for configuration drift",
                    "Consider infrastructure updates",
                ],
                "improvement": "10-20% performance improvement",
            },
        }

    def batch_generate_recommendations(
        self,
        db: Session,
        limit: Optional[int] = None,
    ) -> List[Recommendation]:
        """
        Generate recommendations for all unresolved anomalies without recommendations.
        """
        # Get anomalies without recommendations
        anomalies_without_recs = (
            db.query(Anomaly)
            .filter(Anomaly.resolved == False)
            .filter(~Anomaly.recommendations.any())
            .limit(limit)
            .all()
        )

        recommendations = []

        for anomaly in anomalies_without_recs:
            try:
                rec = self.generate_recommendations(db, anomaly)
                recommendations.append(rec)
            except Exception as e:
                logger.error(f"Error generating recommendation for anomaly {anomaly.id}: {str(e)}")

        return recommendations
