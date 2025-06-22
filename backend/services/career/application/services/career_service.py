"""
Career Application Service

This module provides the application service layer for the Career bounded context,
orchestrating use cases and coordinating between domain and infrastructure layers.
"""

from typing import List, Dict, Optional, Set
from datetime import datetime
import logging

from backend.services.career.domain.entities.career import Career, ExperienceLevel
from backend.services.career.domain.repositories.career_repository import CareerRepository
from backend.services.career.application.use_cases.recommend_career import (
    RecommendCareerUseCase, RecommendCareerRequest, RecommendCareerResponse
)
from backend.shared.domain.base_entity import DomainException


logger = logging.getLogger(__name__)


class CareerService:
    """
    Application service for career-related operations.
    
    This service provides a high-level interface for career functionality,
    coordinating between multiple use cases and repositories.
    """
    
    def __init__(
        self,
        career_repository: CareerRepository,
        recommend_career_use_case: RecommendCareerUseCase,
        event_publisher: Optional[any] = None
    ):
        self.career_repository = career_repository
        self.recommend_career_use_case = recommend_career_use_case
        self.event_publisher = event_publisher
    
    async def get_career_by_id(self, career_id: str) -> Optional[Career]:
        """
        Retrieve a career by its ID.
        
        Args:
            career_id: The career identifier
            
        Returns:
            The Career if found, None otherwise
        """
        try:
            career = await self.career_repository.find_by_id(career_id)
            if career and not career.is_active:
                logger.warning(f"Career {career_id} is inactive")
                return None
            return career
        except Exception as e:
            logger.error(f"Error retrieving career {career_id}: {str(e)}")
            raise DomainException(f"Failed to retrieve career: {str(e)}")
    
    async def search_careers(
        self,
        query: str,
        industry_ids: Optional[List[str]] = None,
        experience_levels: Optional[List[ExperienceLevel]] = None,
        required_skills: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Career]:
        """
        Search for careers based on various criteria.
        
        Args:
            query: Text search query
            industry_ids: Filter by industries
            experience_levels: Filter by experience levels
            required_skills: Filter by required skills
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List of matching careers
        """
        try:
            filters = {}
            if industry_ids:
                filters["industry_ids"] = industry_ids
            if experience_levels:
                filters["experience_levels"] = [level.value for level in experience_levels]
            if required_skills:
                filters["required_skills"] = required_skills
            
            careers = await self.career_repository.search(
                query=query,
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # Filter out inactive careers
            active_careers = [c for c in careers if c.is_active]
            
            logger.info(f"Found {len(active_careers)} careers for query: {query}")
            return active_careers
            
        except Exception as e:
            logger.error(f"Error searching careers: {str(e)}")
            raise DomainException(f"Failed to search careers: {str(e)}")
    
    async def get_career_recommendations(
        self,
        user_id: str,
        user_skills: Dict[str, int],
        user_interests: List[str],
        personality_profile: Optional[Dict[str, float]] = None,
        experience_years: int = 0,
        preferred_industries: Optional[List[str]] = None,
        excluded_career_ids: Optional[Set[str]] = None,
        count: int = 10
    ) -> RecommendCareerResponse:
        """
        Get personalized career recommendations for a user.
        
        Args:
            user_id: The user identifier
            user_skills: Dictionary of skill_id to proficiency level
            user_interests: List of interest areas
            personality_profile: Optional personality assessment results
            experience_years: Years of experience
            preferred_industries: Optional preferred industries
            excluded_career_ids: Careers to exclude from recommendations
            count: Number of recommendations to generate
            
        Returns:
            Career recommendation response
        """
        try:
            request = RecommendCareerRequest(
                user_id=user_id,
                user_skills=user_skills,
                user_interests=user_interests,
                personality_profile=personality_profile,
                experience_years=experience_years,
                preferred_industries=preferred_industries,
                excluded_career_ids=excluded_career_ids,
                recommendation_count=count
            )
            
            response = await self.recommend_career_use_case.execute(request)
            
            # Publish recommendation event if event publisher is available
            if self.event_publisher and response.recommendations:
                await self._publish_recommendations_generated_event(
                    user_id, 
                    len(response.recommendations)
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {str(e)}")
            raise DomainException(f"Failed to generate recommendations: {str(e)}")
    
    async def get_career_progression_paths(
        self,
        from_career_id: str,
        to_career_id: Optional[str] = None,
        max_steps: int = 3
    ) -> List[Dict[str, any]]:
        """
        Get possible career progression paths.
        
        Args:
            from_career_id: Starting career
            to_career_id: Target career (optional)
            max_steps: Maximum career transitions
            
        Returns:
            List of progression paths
        """
        try:
            paths = await self.career_repository.find_progression_paths(
                from_career_id=from_career_id,
                to_career_id=to_career_id,
                max_steps=max_steps
            )
            
            # Convert to DTOs
            path_dtos = []
            for path in paths:
                path_dto = {
                    "starting_career_id": path.starting_career_id,
                    "target_career_id": path.target_career_id,
                    "intermediate_careers": path.intermediate_careers,
                    "estimated_years": path.estimated_years,
                    "difficulty_score": path.difficulty_score,
                    "required_skills": path.required_skills,
                    "total_steps": path.total_steps,
                    "is_direct": path.is_direct_path
                }
                path_dtos.append(path_dto)
            
            logger.info(
                f"Found {len(path_dtos)} progression paths from career {from_career_id}"
            )
            return path_dtos
            
        except Exception as e:
            logger.error(f"Error finding progression paths: {str(e)}")
            raise DomainException(f"Failed to find progression paths: {str(e)}")
    
    async def get_related_careers(
        self,
        career_id: str,
        max_results: int = 10
    ) -> List[Career]:
        """
        Get careers related to a given career.
        
        Args:
            career_id: The career to find relations for
            max_results: Maximum related careers to return
            
        Returns:
            List of related careers
        """
        try:
            # First check if the career exists
            career = await self.career_repository.find_by_id(career_id)
            if not career:
                raise DomainException(f"Career {career_id} not found")
            
            related = await self.career_repository.find_related_careers(
                career_id=career_id,
                max_results=max_results
            )
            
            # Filter out inactive careers
            active_related = [c for c in related if c.is_active]
            
            logger.info(f"Found {len(active_related)} related careers for {career_id}")
            return active_related
            
        except Exception as e:
            logger.error(f"Error finding related careers: {str(e)}")
            raise DomainException(f"Failed to find related careers: {str(e)}")
    
    async def get_trending_careers(
        self,
        days: int = 30,
        limit: int = 10
    ) -> List[Career]:
        """
        Get trending careers based on recent activity.
        
        Args:
            days: Number of days to consider
            limit: Maximum careers to return
            
        Returns:
            List of trending careers
        """
        try:
            trending = await self.career_repository.get_trending_careers(
                days=days,
                limit=limit
            )
            
            logger.info(f"Retrieved {len(trending)} trending careers")
            return trending
            
        except Exception as e:
            logger.error(f"Error retrieving trending careers: {str(e)}")
            raise DomainException(f"Failed to retrieve trending careers: {str(e)}")
    
    async def get_skill_demand_analysis(
        self,
        industry_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Analyze skill demand across careers.
        
        Args:
            industry_id: Optional filter by industry
            
        Returns:
            Skill demand analysis
        """
        try:
            skill_frequency = await self.career_repository.get_skill_frequency(
                industry_id=industry_id
            )
            
            # Calculate insights
            total_careers = await self.career_repository.count(
                filters={"industry_id": industry_id} if industry_id else None
            )
            
            # Sort by frequency
            top_skills = sorted(
                skill_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:20]
            
            analysis = {
                "industry_id": industry_id,
                "total_careers_analyzed": total_careers,
                "unique_skills_count": len(skill_frequency),
                "top_demanded_skills": [
                    {
                        "skill_id": skill_id,
                        "frequency": freq,
                        "percentage": (freq / total_careers * 100) if total_careers > 0 else 0
                    }
                    for skill_id, freq in top_skills
                ],
                "analysis_date": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated skill demand analysis for industry {industry_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing skill demand: {str(e)}")
            raise DomainException(f"Failed to analyze skill demand: {str(e)}")
    
    async def _publish_recommendations_generated_event(
        self, 
        user_id: str, 
        count: int
    ) -> None:
        """Publish event when recommendations are generated"""
        if not self.event_publisher:
            return
        
        try:
            event = {
                "event_type": "career_recommendations_generated",
                "user_id": user_id,
                "recommendation_count": count,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.event_publisher.publish(event)
        except Exception as e:
            logger.warning(f"Failed to publish event: {str(e)}")