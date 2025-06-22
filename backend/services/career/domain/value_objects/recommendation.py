"""
Career Recommendation Value Objects

This module defines value objects related to career recommendations
and matching in the Career bounded context.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

from backend.shared.domain.base_entity import ValueObject, DomainException


class RecommendationType(str, Enum):
    """Type of career recommendation"""
    SKILL_BASED = "skill_based"
    INTEREST_BASED = "interest_based"
    PERSONALITY_BASED = "personality_based"
    PROGRESSION_BASED = "progression_based"
    HYBRID = "hybrid"


class MatchConfidence(str, Enum):
    """Confidence level of a match"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass(frozen=True)
class SkillGap(ValueObject):
    """Value object representing a skill gap"""
    
    skill_id: str
    skill_name: str
    current_level: int
    required_level: int
    importance: str
    
    def __post_init__(self):
        if self.current_level < 0 or self.current_level > 5:
            raise DomainException("Current skill level must be between 0 and 5")
        if self.required_level < 1 or self.required_level > 5:
            raise DomainException("Required skill level must be between 1 and 5")
        if self.current_level >= self.required_level:
            raise DomainException("Not a skill gap - current level meets or exceeds required level")
    
    @property
    def gap_size(self) -> int:
        """Calculate the size of the skill gap"""
        return self.required_level - self.current_level
    
    @property
    def gap_percentage(self) -> float:
        """Calculate gap as percentage of required level"""
        return (self.gap_size / self.required_level) * 100
    
    def __eq__(self, other):
        if not isinstance(other, SkillGap):
            return False
        return (
            self.skill_id == other.skill_id and
            self.current_level == other.current_level and
            self.required_level == other.required_level
        )
    
    def __hash__(self):
        return hash((self.skill_id, self.current_level, self.required_level))


@dataclass(frozen=True)
class CareerMatch(ValueObject):
    """Value object representing a career match score"""
    
    career_id: str
    career_title: str
    overall_score: float
    skill_match_score: float
    interest_match_score: float
    personality_match_score: float
    confidence: MatchConfidence
    
    def __post_init__(self):
        # Validate scores are between 0 and 1
        for score_name, score_value in [
            ("overall_score", self.overall_score),
            ("skill_match_score", self.skill_match_score),
            ("interest_match_score", self.interest_match_score),
            ("personality_match_score", self.personality_match_score)
        ]:
            if not 0 <= score_value <= 1:
                raise DomainException(f"{score_name} must be between 0 and 1")
    
    @staticmethod
    def calculate_confidence(overall_score: float) -> MatchConfidence:
        """Calculate confidence level based on overall score"""
        if overall_score >= 0.9:
            return MatchConfidence.VERY_HIGH
        elif overall_score >= 0.75:
            return MatchConfidence.HIGH
        elif overall_score >= 0.5:
            return MatchConfidence.MEDIUM
        elif overall_score >= 0.25:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.VERY_LOW
    
    def __eq__(self, other):
        if not isinstance(other, CareerMatch):
            return False
        return (
            self.career_id == other.career_id and
            abs(self.overall_score - other.overall_score) < 0.001
        )
    
    def __hash__(self):
        return hash((self.career_id, round(self.overall_score, 3)))


@dataclass(frozen=True)
class CareerRecommendation(ValueObject):
    """Value object representing a complete career recommendation"""
    
    user_id: str
    career_match: CareerMatch
    skill_gaps: List[SkillGap]
    recommendation_type: RecommendationType
    reasoning: str
    recommended_at: datetime
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.expires_at and self.expires_at <= self.recommended_at:
            raise DomainException("Expiration date must be after recommendation date")
    
    @property
    def is_expired(self) -> bool:
        """Check if recommendation has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def critical_skill_gaps(self) -> List[SkillGap]:
        """Get only critical skill gaps"""
        return [gap for gap in self.skill_gaps if gap.importance == "critical"]
    
    @property
    def total_gap_score(self) -> float:
        """Calculate total skill gap score (0-1, lower is better)"""
        if not self.skill_gaps:
            return 0.0
        
        importance_weights = {
            "critical": 3.0,
            "important": 2.0,
            "nice_to_have": 1.0
        }
        
        total_weighted_gap = sum(
            gap.gap_percentage * importance_weights.get(gap.importance, 1.0)
            for gap in self.skill_gaps
        )
        
        total_weight = sum(
            importance_weights.get(gap.importance, 1.0)
            for gap in self.skill_gaps
        )
        
        return (total_weighted_gap / total_weight / 100) if total_weight > 0 else 0.0
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for serialization"""
        return {
            "user_id": self.user_id,
            "career_match": {
                "career_id": self.career_match.career_id,
                "career_title": self.career_match.career_title,
                "overall_score": self.career_match.overall_score,
                "skill_match_score": self.career_match.skill_match_score,
                "interest_match_score": self.career_match.interest_match_score,
                "personality_match_score": self.career_match.personality_match_score,
                "confidence": self.career_match.confidence.value
            },
            "skill_gaps": [
                {
                    "skill_id": gap.skill_id,
                    "skill_name": gap.skill_name,
                    "current_level": gap.current_level,
                    "required_level": gap.required_level,
                    "importance": gap.importance,
                    "gap_size": gap.gap_size
                }
                for gap in self.skill_gaps
            ],
            "recommendation_type": self.recommendation_type.value,
            "reasoning": self.reasoning,
            "recommended_at": self.recommended_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired,
            "total_gap_score": self.total_gap_score
        }
    
    def __eq__(self, other):
        if not isinstance(other, CareerRecommendation):
            return False
        return (
            self.user_id == other.user_id and
            self.career_match == other.career_match and
            self.recommendation_type == other.recommendation_type
        )
    
    def __hash__(self):
        return hash((
            self.user_id,
            self.career_match,
            self.recommendation_type
        ))


@dataclass(frozen=True)
class CareerPath(ValueObject):
    """Value object representing a career progression path"""
    
    starting_career_id: str
    target_career_id: str
    intermediate_careers: List[str]
    estimated_years: int
    difficulty_score: float
    required_skills: List[str]
    
    def __post_init__(self):
        if self.estimated_years < 0:
            raise DomainException("Estimated years cannot be negative")
        if not 0 <= self.difficulty_score <= 1:
            raise DomainException("Difficulty score must be between 0 and 1")
        if self.starting_career_id == self.target_career_id:
            raise DomainException("Starting and target careers must be different")
    
    @property
    def total_steps(self) -> int:
        """Total number of career transitions in path"""
        return len(self.intermediate_careers) + 1
    
    @property
    def is_direct_path(self) -> bool:
        """Check if this is a direct career transition"""
        return len(self.intermediate_careers) == 0
    
    def __eq__(self, other):
        if not isinstance(other, CareerPath):
            return False
        return (
            self.starting_career_id == other.starting_career_id and
            self.target_career_id == other.target_career_id and
            self.intermediate_careers == other.intermediate_careers
        )
    
    def __hash__(self):
        return hash((
            self.starting_career_id,
            self.target_career_id,
            tuple(self.intermediate_careers)
        ))