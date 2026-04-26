"""Recommendations API routes"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Recommendation, Anomaly
from backend.models.schemas import RecommendationResponse, RecommendationCreate
from backend.services.optimizer import RecommendationEngine

router = APIRouter()
engine = RecommendationEngine()


@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    pipeline_name: str = Query(None),
    implemented: bool = Query(None),
    impact: str = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get optimization recommendations with optional filtering.

    Query parameters:
    - pipeline_name: Filter by pipeline name
    - implemented: Filter by implementation status
    - impact: Filter by impact level (High, Medium, Low)
    """
    query = db.query(Recommendation)

    if pipeline_name:
        query = query.filter(Recommendation.pipeline_name == pipeline_name)

    if implemented is not None:
        query = query.filter(Recommendation.implemented == implemented)

    if impact:
        query = query.filter(Recommendation.impact == impact)

    recommendations = query.order_by(Recommendation.created_at.desc()).all()
    return recommendations


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific recommendation by ID"""
    recommendation = (
        db.query(Recommendation)
        .filter(Recommendation.id == recommendation_id)
        .first()
    )

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    return recommendation


@router.post("/generate", response_model=RecommendationResponse)
async def generate_recommendation(
    anomaly_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Generate a recommendation for a specific anomaly.

    Returns the generated recommendation.
    """
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()

    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    # Check if recommendation already exists
    existing = (
        db.query(Recommendation)
        .filter(Recommendation.anomaly_id == anomaly_id)
        .first()
    )

    if existing:
        return existing

    recommendation = engine.generate_recommendations(db, anomaly)
    return recommendation


@router.post("/batch-generate", response_model=List[RecommendationResponse])
async def batch_generate_recommendations(
    limit: int = Query(None, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Generate recommendations for all unresolved anomalies without recommendations.

    Useful for bulk processing after batch anomaly detection.
    """
    recommendations = engine.batch_generate_recommendations(db, limit)
    return recommendations


@router.patch("/{recommendation_id}/implement")
async def mark_implemented(
    recommendation_id: int,
    db: Session = Depends(get_db),
):
    """Mark a recommendation as implemented"""
    recommendation = (
        db.query(Recommendation)
        .filter(Recommendation.id == recommendation_id)
        .first()
    )

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    recommendation.implemented = True
    db.commit()
    db.refresh(recommendation)

    return {
        "status": "marked_implemented",
        "recommendation_id": recommendation_id,
        "title": recommendation.title,
    }
