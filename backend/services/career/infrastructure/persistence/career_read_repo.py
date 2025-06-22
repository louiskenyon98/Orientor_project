"""
Read-Only Career Repository Implementation

This module provides optimized read queries for the Career service,
supporting CQRS pattern with specialized read models.
"""

from typing import List, Dict, Optional
from sqlalchemy import select, and_, or_, func, text, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging

from backend.services.career.domain.repositories.career_repository import CareerReadRepository
from backend.services.career.domain.value_objects.recommendation import CareerMatch, MatchConfidence
from backend.services.career.infrastructure.persistence.models import (
    CareerModel, SkillRequirementModel, CareerProgressionModel
)


logger = logging.getLogger(__name__)


class SQLAlchemyCareerReadRepository(CareerReadRepository):
    """
    Optimized read repository for career queries.
    
    This repository provides specialized queries for reading career data,
    optimized for performance with proper indexing and query optimization.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_career_matches(
        self,
        user_skills: Dict[str, int],
        user_interests: List[str],
        personality_profile: Optional[Dict[str, float]] = None,
        limit: int = 10
    ) -> List[CareerMatch]:
        """
        Find career matches using optimized queries.
        
        This implementation uses PostgreSQL-specific features for performance.
        """
        try:
            # Build skill matching subquery
            skill_match_cte = self._build_skill_match_cte(user_skills)
            
            # Build the main query
            query = f"""
            WITH skill_matches AS (
                {skill_match_cte}
            ),
            career_scores AS (
                SELECT 
                    c.id,
                    c.title,
                    c.industry_id,
                    COALESCE(sm.skill_score, 0) as skill_match_score,
                    CASE 
                        WHEN c.industry_id = ANY(:interests) THEN 0.8
                        ELSE 0.3
                    END as interest_match_score,
                    0.5 as personality_match_score, -- Placeholder
                    (
                        COALESCE(sm.skill_score, 0) * 0.5 +
                        CASE 
                            WHEN c.industry_id = ANY(:interests) THEN 0.8
                            ELSE 0.3
                        END * 0.3 +
                        0.5 * 0.2
                    ) as overall_score
                FROM careers c
                LEFT JOIN skill_matches sm ON c.id = sm.career_id
                WHERE c.is_active = true
            )
            SELECT 
                id,
                title,
                skill_match_score,
                interest_match_score,
                personality_match_score,
                overall_score
            FROM career_scores
            ORDER BY overall_score DESC
            LIMIT :limit
            """
            
            result = await self.session.execute(
                text(query),
                {
                    "interests": user_interests,
                    "limit": limit,
                    **{f"skill_{k}": v for k, v in user_skills.items()}
                }
            )
            
            matches = []
            for row in result:
                confidence = CareerMatch.calculate_confidence(row.overall_score)
                
                match = CareerMatch(
                    career_id=row.id,
                    career_title=row.title,
                    overall_score=row.overall_score,
                    skill_match_score=row.skill_match_score,
                    interest_match_score=row.interest_match_score,
                    personality_match_score=row.personality_match_score,
                    confidence=confidence
                )
                matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding career matches: {str(e)}")
            raise
    
    def _build_skill_match_cte(self, user_skills: Dict[str, int]) -> str:
        """Build CTE for skill matching calculation"""
        if not user_skills:
            return "SELECT NULL::varchar as career_id, 0::float as skill_score WHERE false"
        
        # Build CASE statements for each skill
        skill_cases = []
        for skill_id, user_level in user_skills.items():
            skill_cases.append(f"""
                CASE 
                    WHEN sr.skill_id = '{skill_id}' THEN
                        CASE sr.importance
                            WHEN 'critical' THEN 3.0
                            WHEN 'important' THEN 2.0
                            ELSE 1.0
                        END * 
                        CASE 
                            WHEN {user_level} >= sr.proficiency_level THEN 1.0
                            ELSE {user_level}::float / sr.proficiency_level::float
                        END
                    ELSE 0
                END
            """)
        
        return f"""
        SELECT 
            sr.career_id,
            SUM({' + '.join(skill_cases)}) / 
            NULLIF(SUM(
                CASE sr.importance
                    WHEN 'critical' THEN 3.0
                    WHEN 'important' THEN 2.0
                    ELSE 1.0
                END
            ), 0) as skill_score
        FROM skill_requirements sr
        WHERE sr.skill_id IN ({','.join([f"'{sid}'" for sid in user_skills.keys()])})
        GROUP BY sr.career_id
        """
    
    async def get_career_statistics(self, career_id: str) -> Dict[str, any]:
        """Get detailed statistics for a specific career"""
        try:
            # Get basic career info with counts
            query = """
            SELECT 
                c.id,
                c.title,
                c.industry_id,
                c.experience_level,
                COUNT(DISTINCT sr.id) as skill_count,
                COUNT(DISTINCT cp.to_career_id) as progression_count,
                COUNT(DISTINCT cvl.id) as view_count_30d,
                AVG(sr.proficiency_level) as avg_skill_level
            FROM careers c
            LEFT JOIN skill_requirements sr ON c.id = sr.career_id
            LEFT JOIN career_progressions cp ON c.id = cp.from_career_id
            LEFT JOIN career_view_logs cvl ON c.id = cvl.career_id 
                AND cvl.viewed_at >= CURRENT_DATE - INTERVAL '30 days'
            WHERE c.id = :career_id
            GROUP BY c.id, c.title, c.industry_id, c.experience_level
            """
            
            result = await self.session.execute(
                text(query),
                {"career_id": career_id}
            )
            
            row = result.first()
            if not row:
                return {}
            
            # Get skill distribution
            skill_dist_query = """
            SELECT 
                importance,
                COUNT(*) as count
            FROM skill_requirements
            WHERE career_id = :career_id
            GROUP BY importance
            """
            
            skill_dist_result = await self.session.execute(
                text(skill_dist_query),
                {"career_id": career_id}
            )
            
            skill_distribution = {
                row.importance: row.count 
                for row in skill_dist_result
            }
            
            return {
                "career_id": row.id,
                "title": row.title,
                "industry_id": row.industry_id,
                "experience_level": row.experience_level,
                "total_skills": row.skill_count or 0,
                "avg_skill_level": float(row.avg_skill_level or 0),
                "progression_paths": row.progression_count or 0,
                "views_last_30_days": row.view_count_30d or 0,
                "skill_distribution": skill_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting career statistics: {str(e)}")
            raise
    
    async def get_industry_insights(self, industry_id: str) -> Dict[str, any]:
        """Get insights for an industry"""
        try:
            # Get industry overview
            overview_query = """
            SELECT 
                COUNT(DISTINCT c.id) as total_careers,
                COUNT(DISTINCT c.id) FILTER (WHERE c.experience_level = 'entry') as entry_level_careers,
                COUNT(DISTINCT c.id) FILTER (WHERE c.experience_level = 'senior') as senior_level_careers,
                COUNT(DISTINCT sr.skill_id) as unique_skills,
                AVG(skill_counts.skill_count) as avg_skills_per_career
            FROM careers c
            LEFT JOIN skill_requirements sr ON c.id = sr.career_id
            LEFT JOIN (
                SELECT career_id, COUNT(*) as skill_count
                FROM skill_requirements
                GROUP BY career_id
            ) skill_counts ON c.id = skill_counts.career_id
            WHERE c.industry_id = :industry_id AND c.is_active = true
            """
            
            result = await self.session.execute(
                text(overview_query),
                {"industry_id": industry_id}
            )
            
            overview = result.first()
            
            # Get top skills
            top_skills_query = """
            SELECT 
                sr.skill_id,
                sr.skill_name,
                COUNT(DISTINCT sr.career_id) as career_count,
                AVG(sr.proficiency_level) as avg_proficiency
            FROM skill_requirements sr
            JOIN careers c ON sr.career_id = c.id
            WHERE c.industry_id = :industry_id AND c.is_active = true
            GROUP BY sr.skill_id, sr.skill_name
            ORDER BY career_count DESC
            LIMIT 10
            """
            
            skills_result = await self.session.execute(
                text(top_skills_query),
                {"industry_id": industry_id}
            )
            
            top_skills = [
                {
                    "skill_id": row.skill_id,
                    "skill_name": row.skill_name,
                    "career_count": row.career_count,
                    "avg_proficiency": float(row.avg_proficiency)
                }
                for row in skills_result
            ]
            
            # Get career progression insights
            progression_query = """
            SELECT 
                AVG(cp.typical_years) as avg_progression_years,
                AVG(cp.difficulty_score) as avg_difficulty,
                COUNT(DISTINCT cp.id) as total_progressions
            FROM career_progressions cp
            JOIN careers c1 ON cp.from_career_id = c1.id
            JOIN careers c2 ON cp.to_career_id = c2.id
            WHERE c1.industry_id = :industry_id AND c2.industry_id = :industry_id
            """
            
            prog_result = await self.session.execute(
                text(progression_query),
                {"industry_id": industry_id}
            )
            
            progression = prog_result.first()
            
            return {
                "industry_id": industry_id,
                "overview": {
                    "total_careers": overview.total_careers or 0,
                    "entry_level_careers": overview.entry_level_careers or 0,
                    "senior_level_careers": overview.senior_level_careers or 0,
                    "unique_skills": overview.unique_skills or 0,
                    "avg_skills_per_career": float(overview.avg_skills_per_career or 0)
                },
                "top_skills": top_skills,
                "progression": {
                    "avg_years": float(progression.avg_progression_years or 0),
                    "avg_difficulty": float(progression.avg_difficulty or 0),
                    "total_paths": progression.total_progressions or 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting industry insights: {str(e)}")
            raise