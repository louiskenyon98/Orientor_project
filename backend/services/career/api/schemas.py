"""
Career Service API Schemas

This module defines Pydantic schemas for API request/response validation
in the Career microservice.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Set
from datetime import datetime
from enum import Enum

from backend.services.career.domain.entities.career import ExperienceLevel


class SkillRequirementSchema(BaseModel):
    """Schema for skill requirements"""
    skill_id: str
    skill_name: str
    proficiency_level: int = Field(..., ge=1, le=5)
    importance: str = Field(..., pattern="^(critical|important|nice_to_have)$")


class CareerProgressionSchema(BaseModel):
    """Schema for career progression paths"""
    from_career_id: str
    to_career_id: str
    typical_years: int = Field(..., ge=0)
    difficulty_score: float = Field(..., ge=0.0, le=1.0)
    skill_gaps: List[str] = []


class CareerResponse(BaseModel):
    """Response schema for career details"""
    id: str
    title: str
    description: str
    industry_id: str
    experience_level: ExperienceLevel
    esco_occupation_id: Optional[str] = None
    oasis_code: Optional[str] = None
    required_skills: List[SkillRequirementSchema] = []
    progression_paths: List[CareerProgressionSchema] = []
    related_careers: List[str] = []
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    @classmethod
    def from_domain(cls, career):
        """Convert domain entity to response schema"""
        return cls(
            id=career.id,
            title=career.title,
            description=career.description,
            industry_id=career.industry_id,
            experience_level=career.experience_level,
            esco_occupation_id=career.esco_occupation_id,
            oasis_code=career.oasis_code,
            required_skills=[
                SkillRequirementSchema(
                    skill_id=req.skill_id,
                    skill_name=req.skill_name,
                    proficiency_level=req.proficiency_level,
                    importance=req.importance.value
                )
                for req in career.required_skills
            ],
            progression_paths=[
                CareerProgressionSchema(
                    from_career_id=path.from_career_id,
                    to_career_id=path.to_career_id,
                    typical_years=path.typical_years,
                    difficulty_score=path.difficulty_score,
                    skill_gaps=path.skill_gaps
                )
                for path in career.progression_paths
            ],
            related_careers=list(career.related_careers),
            created_at=career.created_at,
            updated_at=career.updated_at,
            is_active=career.is_active
        )


class CareerSearchRequest(BaseModel):
    """Request schema for career search"""
    query: str = Field(..., min_length=1, max_length=200)
    industry_ids: Optional[List[str]] = None
    experience_levels: Optional[List[ExperienceLevel]] = None
    required_skills: Optional[List[str]] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class CareerSearchResponse(BaseModel):
    """Response schema for career search"""
    careers: List[CareerResponse]
    total: int
    limit: int
    offset: int


class CareerRecommendationRequest(BaseModel):
    """Request schema for career recommendations"""
    user_skills: Dict[str, int] = Field(..., description="Skill ID to proficiency level (1-5)")
    user_interests: List[str] = Field(..., min_items=1)
    personality_profile: Optional[Dict[str, float]] = Field(None, description="Personality assessment scores")
    experience_years: int = Field(0, ge=0)
    preferred_industries: Optional[List[str]] = None
    excluded_career_ids: Optional[Set[str]] = None
    count: int = Field(10, ge=1, le=50)
    
    @validator('user_skills')
    def validate_skill_levels(cls, v):
        for skill_id, level in v.items():
            if not 0 <= level <= 5:
                raise ValueError(f"Skill level for {skill_id} must be between 0 and 5")
        return v


class SkillGapSchema(BaseModel):
    """Schema for skill gaps"""
    skill_id: str
    skill_name: str
    current_level: int = Field(..., ge=0, le=5)
    required_level: int = Field(..., ge=1, le=5)
    importance: str
    gap_size: int
    gap_percentage: float


class CareerMatchSchema(BaseModel):
    """Schema for career match scores"""
    career_id: str
    career_title: str
    overall_score: float = Field(..., ge=0.0, le=1.0)
    skill_match_score: float = Field(..., ge=0.0, le=1.0)
    interest_match_score: float = Field(..., ge=0.0, le=1.0)
    personality_match_score: float = Field(..., ge=0.0, le=1.0)
    confidence: str


class RecommendationSchema(BaseModel):
    """Schema for individual career recommendation"""
    career_match: CareerMatchSchema
    skill_gaps: List[SkillGapSchema]
    recommendation_type: str
    reasoning: str
    recommended_at: datetime
    expires_at: Optional[datetime]
    is_expired: bool
    total_gap_score: float


class CareerRecommendationResponse(BaseModel):
    """Response schema for career recommendations"""
    recommendations: List[RecommendationSchema]
    generated_at: datetime
    count: int
    
    @classmethod
    def from_use_case_response(cls, response):
        """Convert use case response to API response"""
        recommendations = []
        for rec in response.recommendations:
            recommendation = RecommendationSchema(
                career_match=CareerMatchSchema(
                    career_id=rec.career_match.career_id,
                    career_title=rec.career_match.career_title,
                    overall_score=rec.career_match.overall_score,
                    skill_match_score=rec.career_match.skill_match_score,
                    interest_match_score=rec.career_match.interest_match_score,
                    personality_match_score=rec.career_match.personality_match_score,
                    confidence=rec.career_match.confidence.value
                ),
                skill_gaps=[
                    SkillGapSchema(
                        skill_id=gap.skill_id,
                        skill_name=gap.skill_name,
                        current_level=gap.current_level,
                        required_level=gap.required_level,
                        importance=gap.importance,
                        gap_size=gap.gap_size,
                        gap_percentage=gap.gap_percentage
                    )
                    for gap in rec.skill_gaps
                ],
                recommendation_type=rec.recommendation_type.value,
                reasoning=rec.reasoning,
                recommended_at=rec.recommended_at,
                expires_at=rec.expires_at,
                is_expired=rec.is_expired,
                total_gap_score=rec.total_gap_score
            )
            recommendations.append(recommendation)
        
        return cls(
            recommendations=recommendations,
            generated_at=response.generated_at,
            count=response.count
        )


class CareerProgressionResponse(BaseModel):
    """Response schema for career progression paths"""
    starting_career_id: str
    target_career_id: str
    intermediate_careers: List[str]
    estimated_years: int
    difficulty_score: float = Field(..., ge=0.0, le=1.0)
    required_skills: List[str]
    total_steps: int
    is_direct: bool


class SkillDemandSchema(BaseModel):
    """Schema for skill demand information"""
    skill_id: str
    frequency: int
    percentage: float


class SkillDemandAnalysisResponse(BaseModel):
    """Response schema for skill demand analysis"""
    industry_id: Optional[str]
    total_careers_analyzed: int
    unique_skills_count: int
    top_demanded_skills: List[SkillDemandSchema]
    analysis_date: str


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: str
    message: str
    timestamp: str
    details: Optional[Dict[str, any]] = None