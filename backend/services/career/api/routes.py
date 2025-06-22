"""
Career Service API Routes

This module defines the FastAPI routes for the Career microservice,
exposing RESTful endpoints for career-related operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional, Set
from datetime import datetime
import logging

from backend.services.career.api.schemas import (
    CareerResponse,
    CareerSearchRequest,
    CareerSearchResponse,
    CareerRecommendationRequest,
    CareerRecommendationResponse,
    CareerProgressionResponse,
    SkillDemandAnalysisResponse,
    ErrorResponse
)
from backend.services.career.application.services.career_service import CareerService
from backend.services.career.infrastructure.dependencies import get_career_service
from backend.shared.api.middleware import get_current_user, require_auth


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/careers", tags=["careers"])


@router.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint for the Career service."""
    return {
        "service": "career",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/{career_id}", response_model=CareerResponse)
async def get_career(
    career_id: str,
    career_service: CareerService = Depends(get_career_service)
):
    """
    Get a specific career by ID.
    
    Args:
        career_id: The career identifier
        
    Returns:
        Career details
        
    Raises:
        404: Career not found
    """
    try:
        career = await career_service.get_career_by_id(career_id)
        if not career:
            raise HTTPException(status_code=404, detail="Career not found")
        
        return CareerResponse.from_domain(career)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving career {career_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/search", response_model=CareerSearchResponse)
async def search_careers(
    request: CareerSearchRequest,
    career_service: CareerService = Depends(get_career_service)
):
    """
    Search for careers based on various criteria.
    
    Args:
        request: Search criteria including query, filters, and pagination
        
    Returns:
        List of matching careers with pagination info
    """
    try:
        careers = await career_service.search_careers(
            query=request.query,
            industry_ids=request.industry_ids,
            experience_levels=request.experience_levels,
            required_skills=request.required_skills,
            limit=request.limit,
            offset=request.offset
        )
        
        return CareerSearchResponse(
            careers=[CareerResponse.from_domain(c) for c in careers],
            total=len(careers),
            limit=request.limit,
            offset=request.offset
        )
        
    except Exception as e:
        logger.error(f"Error searching careers: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/recommendations", response_model=CareerRecommendationResponse)
async def get_career_recommendations(
    request: CareerRecommendationRequest,
    current_user = Depends(require_auth),
    career_service: CareerService = Depends(get_career_service)
):
    """
    Get personalized career recommendations for the authenticated user.
    
    Args:
        request: User profile data for generating recommendations
        
    Returns:
        Personalized career recommendations
        
    Requires:
        Authentication
    """
    try:
        # Use authenticated user's ID
        user_id = current_user.id
        
        response = await career_service.get_career_recommendations(
            user_id=user_id,
            user_skills=request.user_skills,
            user_interests=request.user_interests,
            personality_profile=request.personality_profile,
            experience_years=request.experience_years,
            preferred_industries=request.preferred_industries,
            excluded_career_ids=request.excluded_career_ids,
            count=request.count
        )
        
        return CareerRecommendationResponse.from_use_case_response(response)
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@router.get("/{career_id}/progression-paths", response_model=List[CareerProgressionResponse])
async def get_career_progression_paths(
    career_id: str,
    to_career_id: Optional[str] = Query(None, description="Target career ID"),
    max_steps: int = Query(3, ge=1, le=5, description="Maximum career transitions"),
    career_service: CareerService = Depends(get_career_service)
):
    """
    Get possible career progression paths from a starting career.
    
    Args:
        career_id: Starting career ID
        to_career_id: Optional target career ID
        max_steps: Maximum number of career transitions (1-5)
        
    Returns:
        List of possible progression paths
    """
    try:
        paths = await career_service.get_career_progression_paths(
            from_career_id=career_id,
            to_career_id=to_career_id,
            max_steps=max_steps
        )
        
        return [CareerProgressionResponse(**path) for path in paths]
        
    except Exception as e:
        logger.error(f"Error finding progression paths: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to find progression paths")


@router.get("/{career_id}/related", response_model=List[CareerResponse])
async def get_related_careers(
    career_id: str,
    max_results: int = Query(10, ge=1, le=50, description="Maximum results"),
    career_service: CareerService = Depends(get_career_service)
):
    """
    Get careers related to a specific career.
    
    Args:
        career_id: The career to find relations for
        max_results: Maximum number of related careers (1-50)
        
    Returns:
        List of related careers
    """
    try:
        related = await career_service.get_related_careers(
            career_id=career_id,
            max_results=max_results
        )
        
        return [CareerResponse.from_domain(c) for c in related]
        
    except Exception as e:
        logger.error(f"Error finding related careers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to find related careers")


@router.get("/trending/list", response_model=List[CareerResponse])
async def get_trending_careers(
    days: int = Query(30, ge=7, le=365, description="Number of days to consider"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    career_service: CareerService = Depends(get_career_service)
):
    """
    Get trending careers based on recent activity.
    
    Args:
        days: Number of days to consider for trending (7-365)
        limit: Maximum number of results (1-50)
        
    Returns:
        List of trending careers
    """
    try:
        trending = await career_service.get_trending_careers(
            days=days,
            limit=limit
        )
        
        return [CareerResponse.from_domain(c) for c in trending]
        
    except Exception as e:
        logger.error(f"Error retrieving trending careers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trending careers")


@router.get("/analytics/skill-demand", response_model=SkillDemandAnalysisResponse)
async def get_skill_demand_analysis(
    industry_id: Optional[str] = Query(None, description="Filter by industry"),
    career_service: CareerService = Depends(get_career_service)
):
    """
    Analyze skill demand across careers.
    
    Args:
        industry_id: Optional industry filter
        
    Returns:
        Skill demand analysis including top demanded skills
    """
    try:
        analysis = await career_service.get_skill_demand_analysis(
            industry_id=industry_id
        )
        
        return SkillDemandAnalysisResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing skill demand: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze skill demand")


@router.post("/webhook/sync")
async def sync_careers_webhook(
    payload: dict = Body(...),
    career_service: CareerService = Depends(get_career_service)
):
    """
    Webhook endpoint for syncing careers from external systems.
    
    This endpoint is typically called by ESCO or other career databases
    when updates are available.
    
    Args:
        payload: Webhook payload with sync information
        
    Returns:
        Sync status
    """
    try:
        # This would typically trigger a background job
        logger.info(f"Received career sync webhook: {payload.get('event_type', 'unknown')}")
        
        # TODO: Implement actual sync logic
        # - Validate webhook signature
        # - Queue sync job
        # - Return immediate response
        
        return {
            "status": "accepted",
            "message": "Sync request queued",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing sync webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


# Error handlers
@router.exception_handler(404)
async def not_found_handler(request, exc):
    return ErrorResponse(
        error="not_found",
        message=str(exc.detail),
        timestamp=datetime.utcnow().isoformat()
    )


@router.exception_handler(500)
async def internal_error_handler(request, exc):
    return ErrorResponse(
        error="internal_error",
        message="An internal error occurred",
        timestamp=datetime.utcnow().isoformat()
    )