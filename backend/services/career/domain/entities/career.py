"""Career domain entity following DDD principles."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from shared.domain.base_entity import AggregateRoot, DomainEvent, ValueObject


class ExperienceLevel(Enum):
    """Experience level enumeration."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    EXPERT = "expert"


class CareerStatus(Enum):
    """Career status enumeration."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DRAFT = "draft"


@dataclass(frozen=True)
class SkillRequirement(ValueObject):
    """Value object representing a skill requirement for a career."""
    skill_id: str
    skill_name: str
    proficiency_level: int  # 1-5
    importance: str  # critical, important, nice-to-have
    
    def __post_init__(self):
        if self.proficiency_level < 1 or self.proficiency_level > 5:
            raise ValueError("Proficiency level must be between 1 and 5")
        if self.importance not in ['critical', 'important', 'nice-to-have']:
            raise ValueError("Importance must be critical, important, or nice-to-have")


@dataclass(frozen=True)
class SalaryRange(ValueObject):
    """Value object representing salary range."""
    min_salary: float
    max_salary: float
    currency: str = "USD"
    period: str = "yearly"
    
    def __post_init__(self):
        if self.min_salary < 0:
            raise ValueError("Minimum salary cannot be negative")
        if self.max_salary < self.min_salary:
            raise ValueError("Maximum salary must be greater than minimum salary")


@dataclass(frozen=True)
class CareerMetadata(ValueObject):
    """Value object for career metadata."""
    growth_rate: float  # Percentage
    job_openings: int
    automation_risk: float  # 0-1
    remote_friendly: bool
    typical_education: str
    
    def __post_init__(self):
        if self.automation_risk < 0 or self.automation_risk > 1:
            raise ValueError("Automation risk must be between 0 and 1")


class CareerRecommendedEvent(DomainEvent):
    """Event raised when a career is recommended to a user."""
    
    def __init__(self, career_id: str, user_id: str, score: float):
        super().__init__(career_id)
        self.user_id = user_id
        self.score = score
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'user_id': self.user_id,
            'score': self.score
        })
        return base


class Career(AggregateRoot):
    """Career aggregate root - represents a career path."""
    
    def __init__(
        self,
        id: Optional[str] = None,
        title: str = "",
        description: str = "",
        industry_id: str = "",
        experience_level: ExperienceLevel = ExperienceLevel.ENTRY,
        status: CareerStatus = CareerStatus.ACTIVE
    ):
        super().__init__(id)
        self.title = title
        self.description = description
        self.industry_id = industry_id
        self.experience_level = experience_level
        self.status = status
        self.required_skills: List[SkillRequirement] = []
        self.salary_range: Optional[SalaryRange] = None
        self.metadata: Optional[CareerMetadata] = None
        self.related_careers: List[str] = []  # IDs of related careers
        self.keywords: List[str] = []
        self.esco_code: Optional[str] = None  # ESCO occupation code
        self.onet_code: Optional[str] = None  # O*NET occupation code
    
    def add_skill_requirement(self, skill_requirement: SkillRequirement):
        """Add a skill requirement to the career."""
        # Check if skill already exists
        for existing in self.required_skills:
            if existing.skill_id == skill_requirement.skill_id:
                raise ValueError(f"Skill {skill_requirement.skill_id} already required")
        
        self.required_skills.append(skill_requirement)
        self.increment_version()
    
    def remove_skill_requirement(self, skill_id: str):
        """Remove a skill requirement from the career."""
        self.required_skills = [
            skill for skill in self.required_skills 
            if skill.skill_id != skill_id
        ]
        self.increment_version()
    
    def update_salary_range(self, salary_range: SalaryRange):
        """Update the salary range for the career."""
        self.salary_range = salary_range
        self.increment_version()
    
    def update_metadata(self, metadata: CareerMetadata):
        """Update career metadata."""
        self.metadata = metadata
        self.increment_version()
    
    def add_related_career(self, career_id: str):
        """Add a related career."""
        if career_id not in self.related_careers:
            self.related_careers.append(career_id)
            self.increment_version()
    
    def deprecate(self):
        """Mark career as deprecated."""
        if self.status == CareerStatus.DEPRECATED:
            raise ValueError("Career is already deprecated")
        
        self.status = CareerStatus.DEPRECATED
        self.increment_version()
    
    def activate(self):
        """Activate the career."""
        if self.status == CareerStatus.ACTIVE:
            raise ValueError("Career is already active")
        
        self.status = CareerStatus.ACTIVE
        self.increment_version()
    
    def get_critical_skills(self) -> List[SkillRequirement]:
        """Get critical skill requirements."""
        return [skill for skill in self.required_skills if skill.importance == 'critical']
    
    def get_skill_match_score(self, user_skills: Dict[str, int]) -> float:
        """Calculate skill match score for a user."""
        if not self.required_skills:
            return 0.0
        
        total_weight = 0.0
        weighted_score = 0.0
        
        importance_weights = {
            'critical': 3.0,
            'important': 2.0,
            'nice-to-have': 1.0
        }
        
        for skill_req in self.required_skills:
            weight = importance_weights[skill_req.importance]
            total_weight += weight
            
            user_level = user_skills.get(skill_req.skill_id, 0)
            if user_level > 0:
                # Calculate match percentage (capped at 100%)
                match = min(user_level / skill_req.proficiency_level, 1.0)
                weighted_score += match * weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def recommend_to_user(self, user_id: str, score: float):
        """Recommend this career to a user."""
        if score < 0 or score > 1:
            raise ValueError("Recommendation score must be between 0 and 1")
        
        event = CareerRecommendedEvent(self.id, user_id, score)
        self.add_domain_event(event)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert career to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'industry_id': self.industry_id,
            'experience_level': self.experience_level.value,
            'status': self.status.value,
            'required_skills': [
                {
                    'skill_id': skill.skill_id,
                    'skill_name': skill.skill_name,
                    'proficiency_level': skill.proficiency_level,
                    'importance': skill.importance
                }
                for skill in self.required_skills
            ],
            'salary_range': {
                'min_salary': self.salary_range.min_salary,
                'max_salary': self.salary_range.max_salary,
                'currency': self.salary_range.currency,
                'period': self.salary_range.period
            } if self.salary_range else None,
            'metadata': {
                'growth_rate': self.metadata.growth_rate,
                'job_openings': self.metadata.job_openings,
                'automation_risk': self.metadata.automation_risk,
                'remote_friendly': self.metadata.remote_friendly,
                'typical_education': self.metadata.typical_education
            } if self.metadata else None,
            'related_careers': self.related_careers,
            'keywords': self.keywords,
            'esco_code': self.esco_code,
            'onet_code': self.onet_code,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }