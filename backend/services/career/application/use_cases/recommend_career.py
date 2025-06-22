"""Use case for recommending careers to users."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from ...domain.repositories.career_repository import CareerRepository
from ...domain.entities.career import Career
from shared.infrastructure.cache.redis_cache import CacheService, CacheKeys
from shared.infrastructure.messaging.event_bus import EventPublisher

logger = logging.getLogger(__name__)


@dataclass
class CareerRecommendation:
    """Career recommendation result."""
    career: Career
    score: float
    match_reasons: List[str]
    skill_gaps: List[Dict[str, Any]]


class RecommendCareerUseCase:
    """Use case for generating career recommendations."""
    
    def __init__(
        self,
        career_repo: CareerRepository,
        cache_service: CacheService,
        event_publisher: EventPublisher,
        llm_service: Optional[Any] = None  # LLM service for AI recommendations
    ):
        self.career_repo = career_repo
        self.cache_service = cache_service
        self.event_publisher = event_publisher
        self.llm_service = llm_service
    
    async def execute(
        self,
        user_id: str,
        user_skills: Dict[str, int],
        user_interests: List[str],
        user_experience_level: str,
        personality_profile: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        use_cache: bool = True
    ) -> List[CareerRecommendation]:
        """Generate career recommendations for a user."""
        
        # Check cache first
        if use_cache:
            cache_key = CacheKeys.career_recommendation(user_id)
            cached = await self.cache_service.get(cache_key)
            if cached:
                logger.info(f"Returning cached recommendations for user {user_id}")
                return self._deserialize_recommendations(cached)
        
        try:
            # Get careers matching user skills
            skill_based_careers = await self._get_skill_based_careers(
                user_skills, 
                limit * 3  # Get more to filter later
            )
            
            # Score and rank careers
            recommendations = []
            for career in skill_based_careers:
                score, reasons, gaps = await self._score_career(
                    career,
                    user_skills,
                    user_interests,
                    user_experience_level,
                    personality_profile
                )
                
                if score >= 0.3:  # Minimum threshold
                    recommendations.append(CareerRecommendation(
                        career=career,
                        score=score,
                        match_reasons=reasons,
                        skill_gaps=gaps
                    ))
            
            # Sort by score and limit
            recommendations.sort(key=lambda x: x.score, reverse=True)
            recommendations = recommendations[:limit]
            
            # Enhance with AI if available
            if self.llm_service and recommendations:
                recommendations = await self._enhance_with_ai(
                    recommendations,
                    user_skills,
                    user_interests,
                    personality_profile
                )
            
            # Cache results
            if use_cache and recommendations:
                await self.cache_service.set(
                    cache_key,
                    self._serialize_recommendations(recommendations),
                    ttl=3600  # 1 hour
                )
            
            # Publish events for top recommendations
            for rec in recommendations[:3]:
                await self.event_publisher.publish_career_recommended(
                    user_id,
                    rec.career.id,
                    rec.score
                )
                # Add domain event to career
                rec.career.recommend_to_user(user_id, rec.score)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            raise
    
    async def _get_skill_based_careers(
        self,
        user_skills: Dict[str, int],
        limit: int
    ) -> List[Career]:
        """Get careers based on user skills."""
        if not user_skills:
            # Return popular careers if no skills
            return await self.career_repo.get_popular_careers(limit)
        
        skill_ids = list(user_skills.keys())
        return await self.career_repo.find_by_skills(
            skill_ids,
            match_threshold=0.3,
            limit=limit
        )
    
    async def _score_career(
        self,
        career: Career,
        user_skills: Dict[str, int],
        user_interests: List[str],
        user_experience_level: str,
        personality_profile: Optional[Dict[str, Any]]
    ) -> tuple[float, List[str], List[Dict[str, Any]]]:
        """Score a career for a user."""
        
        score = 0.0
        reasons = []
        gaps = []
        
        # Skill match score (40% weight)
        skill_score = career.get_skill_match_score(user_skills)
        score += skill_score * 0.4
        
        if skill_score >= 0.7:
            reasons.append(f"Strong skill match ({int(skill_score * 100)}%)")
        elif skill_score >= 0.5:
            reasons.append(f"Good skill match ({int(skill_score * 100)}%)")
        
        # Calculate skill gaps
        for skill_req in career.required_skills:
            user_level = user_skills.get(skill_req.skill_id, 0)
            if user_level < skill_req.proficiency_level:
                gaps.append({
                    'skill_id': skill_req.skill_id,
                    'skill_name': skill_req.skill_name,
                    'current_level': user_level,
                    'required_level': skill_req.proficiency_level,
                    'importance': skill_req.importance
                })
        
        # Interest match (20% weight)
        interest_score = self._calculate_interest_match(career, user_interests)
        score += interest_score * 0.2
        
        if interest_score >= 0.7:
            reasons.append("Aligns with your interests")
        
        # Experience level match (20% weight)
        exp_score = self._calculate_experience_match(
            career.experience_level.value,
            user_experience_level
        )
        score += exp_score * 0.2
        
        if exp_score >= 0.8:
            reasons.append("Matches your experience level")
        
        # Personality fit (20% weight if available)
        if personality_profile:
            personality_score = self._calculate_personality_fit(
                career,
                personality_profile
            )
            score += personality_score * 0.2
            
            if personality_score >= 0.7:
                reasons.append("Good personality fit")
        else:
            # Distribute weight to other factors
            score += 0.2
        
        return score, reasons, gaps
    
    def _calculate_interest_match(
        self,
        career: Career,
        user_interests: List[str]
    ) -> float:
        """Calculate interest match score."""
        if not user_interests:
            return 0.5  # Neutral score
        
        # Check keywords and title
        career_text = f"{career.title} {' '.join(career.keywords)}".lower()
        matches = sum(
            1 for interest in user_interests 
            if interest.lower() in career_text
        )
        
        return min(matches / len(user_interests), 1.0)
    
    def _calculate_experience_match(
        self,
        career_exp: str,
        user_exp: str
    ) -> float:
        """Calculate experience level match."""
        exp_levels = ['entry', 'junior', 'mid', 'senior', 'expert']
        
        try:
            career_idx = exp_levels.index(career_exp)
            user_idx = exp_levels.index(user_exp)
            
            # Perfect match
            if career_idx == user_idx:
                return 1.0
            
            # One level difference
            if abs(career_idx - user_idx) == 1:
                return 0.8
            
            # Two level difference
            if abs(career_idx - user_idx) == 2:
                return 0.5
            
            # More than two levels
            return 0.2
            
        except ValueError:
            return 0.5  # Default neutral score
    
    def _calculate_personality_fit(
        self,
        career: Career,
        personality_profile: Dict[str, Any]
    ) -> float:
        """Calculate personality fit score."""
        # This is a simplified version
        # In production, this would use more sophisticated matching
        
        # Example: Match based on Holland codes or HEXACO traits
        career_traits = career.metadata.__dict__ if career.metadata else {}
        
        # Simple matching logic
        score = 0.5  # Base score
        
        # Adjust based on personality traits
        if personality_profile.get('openness', 0) > 0.7 and career_traits.get('remote_friendly'):
            score += 0.1
        
        if personality_profile.get('conscientiousness', 0) > 0.7:
            score += 0.1
        
        return min(score, 1.0)
    
    async def _enhance_with_ai(
        self,
        recommendations: List[CareerRecommendation],
        user_skills: Dict[str, int],
        user_interests: List[str],
        personality_profile: Optional[Dict[str, Any]]
    ) -> List[CareerRecommendation]:
        """Enhance recommendations using AI/LLM service."""
        # This would call the LLM service to refine recommendations
        # For now, return as-is
        return recommendations
    
    def _serialize_recommendations(
        self,
        recommendations: List[CareerRecommendation]
    ) -> List[Dict[str, Any]]:
        """Serialize recommendations for caching."""
        return [
            {
                'career': rec.career.to_dict(),
                'score': rec.score,
                'match_reasons': rec.match_reasons,
                'skill_gaps': rec.skill_gaps
            }
            for rec in recommendations
        ]
    
    def _deserialize_recommendations(
        self,
        data: List[Dict[str, Any]]
    ) -> List[CareerRecommendation]:
        """Deserialize recommendations from cache."""
        recommendations = []
        for item in data:
            # Reconstruct Career object
            career_data = item['career']
            career = Career(
                id=career_data['id'],
                title=career_data['title'],
                description=career_data['description'],
                industry_id=career_data['industry_id']
            )
            # Note: This is simplified - in production, fully reconstruct the object
            
            recommendations.append(CareerRecommendation(
                career=career,
                score=item['score'],
                match_reasons=item['match_reasons'],
                skill_gaps=item['skill_gaps']
            ))
        
        return recommendations