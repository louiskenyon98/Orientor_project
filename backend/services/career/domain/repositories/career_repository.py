"""Career repository interface following repository pattern."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from shared.domain.base_entity import Repository
from ..entities.career import Career, ExperienceLevel, CareerStatus


class CareerRepository(Repository):
    """Repository interface for Career aggregate."""
    
    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[Career]:
        """Find career by ID."""
        pass
    
    @abstractmethod
    async def find_by_title(self, title: str) -> Optional[Career]:
        """Find career by exact title match."""
        pass
    
    @abstractmethod
    async def search_by_title(self, query: str, limit: int = 20) -> List[Career]:
        """Search careers by title (partial match)."""
        pass
    
    @abstractmethod
    async def find_by_skills(
        self, 
        skill_ids: List[str], 
        match_threshold: float = 0.5,
        limit: int = 20
    ) -> List[Career]:
        """Find careers matching given skills with minimum threshold."""
        pass
    
    @abstractmethod
    async def find_by_industry(
        self, 
        industry_id: str,
        experience_level: Optional[ExperienceLevel] = None,
        status: CareerStatus = CareerStatus.ACTIVE,
        limit: int = 50
    ) -> List[Career]:
        """Find careers by industry and optional filters."""
        pass
    
    @abstractmethod
    async def find_related_careers(self, career_id: str, limit: int = 10) -> List[Career]:
        """Find careers related to a given career."""
        pass
    
    @abstractmethod
    async def save(self, career: Career) -> None:
        """Save or update career."""
        pass
    
    @abstractmethod
    async def save_many(self, careers: List[Career]) -> None:
        """Save multiple careers in batch."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> None:
        """Delete career by ID."""
        pass
    
    @abstractmethod
    async def exists(self, id: str) -> bool:
        """Check if career exists."""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: CareerStatus) -> int:
        """Count careers by status."""
        pass
    
    @abstractmethod
    async def find_by_keywords(self, keywords: List[str], limit: int = 20) -> List[Career]:
        """Find careers by keywords."""
        pass
    
    @abstractmethod
    async def find_by_esco_code(self, esco_code: str) -> Optional[Career]:
        """Find career by ESCO occupation code."""
        pass
    
    @abstractmethod
    async def find_by_salary_range(
        self,
        min_salary: float,
        max_salary: float,
        currency: str = "USD",
        limit: int = 20
    ) -> List[Career]:
        """Find careers within salary range."""
        pass
    
    @abstractmethod
    async def get_popular_careers(self, limit: int = 20) -> List[Career]:
        """Get most popular/recommended careers."""
        pass


class CareerSearchCriteria:
    """Search criteria for advanced career queries."""
    
    def __init__(self):
        self.keywords: List[str] = []
        self.industries: List[str] = []
        self.skills: List[str] = []
        self.experience_levels: List[ExperienceLevel] = []
        self.min_salary: Optional[float] = None
        self.max_salary: Optional[float] = None
        self.remote_only: bool = False
        self.max_automation_risk: Optional[float] = None
        self.min_growth_rate: Optional[float] = None
        self.status: CareerStatus = CareerStatus.ACTIVE
        self.limit: int = 20
        self.offset: int = 0
    
    def add_keyword(self, keyword: str) -> 'CareerSearchCriteria':
        """Add keyword to search."""
        self.keywords.append(keyword)
        return self
    
    def add_skill(self, skill_id: str) -> 'CareerSearchCriteria':
        """Add required skill to search."""
        self.skills.append(skill_id)
        return self
    
    def add_industry(self, industry_id: str) -> 'CareerSearchCriteria':
        """Add industry to search."""
        self.industries.append(industry_id)
        return self
    
    def set_salary_range(self, min_salary: float, max_salary: float) -> 'CareerSearchCriteria':
        """Set salary range filter."""
        self.min_salary = min_salary
        self.max_salary = max_salary
        return self
    
    def set_experience_levels(self, levels: List[ExperienceLevel]) -> 'CareerSearchCriteria':
        """Set experience level filter."""
        self.experience_levels = levels
        return self
    
    def set_remote_only(self, remote_only: bool = True) -> 'CareerSearchCriteria':
        """Filter for remote-friendly careers only."""
        self.remote_only = remote_only
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert criteria to dictionary."""
        return {
            'keywords': self.keywords,
            'industries': self.industries,
            'skills': self.skills,
            'experience_levels': [level.value for level in self.experience_levels],
            'min_salary': self.min_salary,
            'max_salary': self.max_salary,
            'remote_only': self.remote_only,
            'max_automation_risk': self.max_automation_risk,
            'min_growth_rate': self.min_growth_rate,
            'status': self.status.value,
            'limit': self.limit,
            'offset': self.offset
        }