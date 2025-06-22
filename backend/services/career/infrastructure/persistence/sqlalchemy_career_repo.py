"""
SQLAlchemy Career Repository Implementation

This module provides the concrete implementation of the Career repository
using SQLAlchemy for persistence.
"""

from typing import List, Optional, Dict, Set
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging

from backend.services.career.domain.entities.career import Career, ExperienceLevel, SkillImportance
from backend.services.career.domain.repositories.career_repository import CareerRepository
from backend.services.career.domain.value_objects.recommendation import CareerPath
from backend.services.career.infrastructure.persistence.models import (
    CareerModel, SkillRequirementModel, CareerProgressionModel
)


logger = logging.getLogger(__name__)


class SQLAlchemyCareerRepository(CareerRepository):
    """
    SQLAlchemy implementation of the Career repository.
    
    This class handles the persistence of Career aggregates using
    SQLAlchemy ORM with PostgreSQL.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, career_id: str) -> Optional[Career]:
        """Find a career by its unique identifier"""
        try:
            result = await self.session.execute(
                select(CareerModel)
                .options(
                    selectinload(CareerModel.required_skills),
                    selectinload(CareerModel.progression_paths)
                )
                .where(CareerModel.id == career_id)
            )
            career_model = result.scalar_one_or_none()
            
            if career_model:
                return self._to_domain(career_model)
            return None
            
        except Exception as e:
            logger.error(f"Error finding career by id {career_id}: {str(e)}")
            raise
    
    async def find_by_esco_id(self, esco_occupation_id: str) -> Optional[Career]:
        """Find a career by its ESCO occupation ID"""
        try:
            result = await self.session.execute(
                select(CareerModel)
                .options(
                    selectinload(CareerModel.required_skills),
                    selectinload(CareerModel.progression_paths)
                )
                .where(CareerModel.esco_occupation_id == esco_occupation_id)
            )
            career_model = result.scalar_one_or_none()
            
            if career_model:
                return self._to_domain(career_model)
            return None
            
        except Exception as e:
            logger.error(f"Error finding career by ESCO id {esco_occupation_id}: {str(e)}")
            raise
    
    async def find_by_oasis_code(self, oasis_code: str) -> Optional[Career]:
        """Find a career by its OASIS code"""
        try:
            result = await self.session.execute(
                select(CareerModel)
                .options(
                    selectinload(CareerModel.required_skills),
                    selectinload(CareerModel.progression_paths)
                )
                .where(CareerModel.oasis_code == oasis_code)
            )
            career_model = result.scalar_one_or_none()
            
            if career_model:
                return self._to_domain(career_model)
            return None
            
        except Exception as e:
            logger.error(f"Error finding career by OASIS code {oasis_code}: {str(e)}")
            raise
    
    async def find_by_skills(
        self, 
        skill_ids: List[str], 
        min_match_count: Optional[int] = None
    ) -> List[Career]:
        """Find careers that require specific skills"""
        try:
            min_count = min_match_count or 1
            
            # Subquery to count matching skills per career
            skill_match_subquery = (
                select(
                    SkillRequirementModel.career_id,
                    func.count(SkillRequirementModel.skill_id).label('match_count')
                )
                .where(SkillRequirementModel.skill_id.in_(skill_ids))
                .group_by(SkillRequirementModel.career_id)
                .having(func.count(SkillRequirementModel.skill_id) >= min_count)
                .subquery()
            )
            
            # Main query
            result = await self.session.execute(
                select(CareerModel)
                .options(
                    selectinload(CareerModel.required_skills),
                    selectinload(CareerModel.progression_paths)
                )
                .join(skill_match_subquery, CareerModel.id == skill_match_subquery.c.career_id)
                .where(CareerModel.is_active == True)
                .order_by(skill_match_subquery.c.match_count.desc())
            )
            
            career_models = result.scalars().all()
            return [self._to_domain(model) for model in career_models]
            
        except Exception as e:
            logger.error(f"Error finding careers by skills: {str(e)}")
            raise
    
    async def find_by_industry(
        self, 
        industry_id: str, 
        experience_level: Optional[ExperienceLevel] = None
    ) -> List[Career]:
        """Find careers within a specific industry"""
        try:
            query = select(CareerModel).options(
                selectinload(CareerModel.required_skills),
                selectinload(CareerModel.progression_paths)
            ).where(
                and_(
                    CareerModel.industry_id == industry_id,
                    CareerModel.is_active == True
                )
            )
            
            if experience_level:
                query = query.where(CareerModel.experience_level == experience_level.value)
            
            result = await self.session.execute(query)
            career_models = result.scalars().all()
            
            return [self._to_domain(model) for model in career_models]
            
        except Exception as e:
            logger.error(f"Error finding careers by industry {industry_id}: {str(e)}")
            raise
    
    async def find_related_careers(
        self, 
        career_id: str, 
        max_results: int = 10
    ) -> List[Career]:
        """Find careers related to a given career"""
        try:
            # First get the target career
            target = await self.find_by_id(career_id)
            if not target:
                return []
            
            # Find careers with overlapping skills
            target_skill_ids = [req.skill_id for req in target.required_skills]
            
            if target_skill_ids:
                skill_overlap_query = (
                    select(
                        CareerModel.id,
                        func.count(SkillRequirementModel.skill_id).label('overlap_count')
                    )
                    .join(CareerModel.required_skills)
                    .where(
                        and_(
                            SkillRequirementModel.skill_id.in_(target_skill_ids),
                            CareerModel.id != career_id,
                            CareerModel.is_active == True
                        )
                    )
                    .group_by(CareerModel.id)
                    .order_by(func.count(SkillRequirementModel.skill_id).desc())
                    .limit(max_results * 2)  # Get more for filtering
                    .subquery()
                )
                
                # Get careers with skill overlap
                result = await self.session.execute(
                    select(CareerModel)
                    .options(
                        selectinload(CareerModel.required_skills),
                        selectinload(CareerModel.progression_paths)
                    )
                    .join(skill_overlap_query, CareerModel.id == skill_overlap_query.c.id)
                    .order_by(skill_overlap_query.c.overlap_count.desc())
                )
                
                related_models = result.scalars().all()
            else:
                # Fallback to same industry
                result = await self.session.execute(
                    select(CareerModel)
                    .options(
                        selectinload(CareerModel.required_skills),
                        selectinload(CareerModel.progression_paths)
                    )
                    .where(
                        and_(
                            CareerModel.industry_id == target.industry_id,
                            CareerModel.id != career_id,
                            CareerModel.is_active == True
                        )
                    )
                    .limit(max_results)
                )
                related_models = result.scalars().all()
            
            # Also include careers from related_careers field
            if target.related_careers:
                additional_result = await self.session.execute(
                    select(CareerModel)
                    .options(
                        selectinload(CareerModel.required_skills),
                        selectinload(CareerModel.progression_paths)
                    )
                    .where(
                        and_(
                            CareerModel.id.in_(list(target.related_careers)),
                            CareerModel.is_active == True
                        )
                    )
                )
                additional_models = additional_result.scalars().all()
                related_models.extend(additional_models)
            
            # Convert to domain and deduplicate
            careers = [self._to_domain(model) for model in related_models]
            seen = set()
            unique_careers = []
            for career in careers:
                if career.id not in seen:
                    seen.add(career.id)
                    unique_careers.append(career)
            
            return unique_careers[:max_results]
            
        except Exception as e:
            logger.error(f"Error finding related careers for {career_id}: {str(e)}")
            raise
    
    async def find_progression_paths(
        self, 
        from_career_id: str, 
        to_career_id: Optional[str] = None,
        max_steps: int = 3
    ) -> List[CareerPath]:
        """Find career progression paths"""
        try:
            # This is a simplified implementation
            # In production, you might use graph algorithms or recursive CTEs
            
            paths = []
            
            if to_career_id:
                # Direct path check
                result = await self.session.execute(
                    select(CareerProgressionModel)
                    .where(
                        and_(
                            CareerProgressionModel.from_career_id == from_career_id,
                            CareerProgressionModel.to_career_id == to_career_id
                        )
                    )
                )
                direct_path = result.scalar_one_or_none()
                
                if direct_path:
                    # Get required skills
                    to_career = await self.find_by_id(to_career_id)
                    required_skills = [req.skill_id for req in to_career.required_skills] if to_career else []
                    
                    path = CareerPath(
                        starting_career_id=from_career_id,
                        target_career_id=to_career_id,
                        intermediate_careers=[],
                        estimated_years=direct_path.typical_years,
                        difficulty_score=direct_path.difficulty_score,
                        required_skills=required_skills
                    )
                    paths.append(path)
            else:
                # Find all possible progressions from starting career
                result = await self.session.execute(
                    select(CareerProgressionModel)
                    .where(CareerProgressionModel.from_career_id == from_career_id)
                    .limit(10)
                )
                progressions = result.scalars().all()
                
                for prog in progressions:
                    to_career = await self.find_by_id(prog.to_career_id)
                    if to_career and to_career.is_active:
                        required_skills = [req.skill_id for req in to_career.required_skills]
                        
                        path = CareerPath(
                            starting_career_id=from_career_id,
                            target_career_id=prog.to_career_id,
                            intermediate_careers=[],
                            estimated_years=prog.typical_years,
                            difficulty_score=prog.difficulty_score,
                            required_skills=required_skills
                        )
                        paths.append(path)
            
            return paths
            
        except Exception as e:
            logger.error(f"Error finding progression paths: {str(e)}")
            raise
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, any]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Career]:
        """Search careers by text query and filters"""
        try:
            # Base query
            base_query = select(CareerModel).options(
                selectinload(CareerModel.required_skills),
                selectinload(CareerModel.progression_paths)
            ).where(CareerModel.is_active == True)
            
            # Text search on title and description
            if query:
                search_condition = or_(
                    CareerModel.title.ilike(f"%{query}%"),
                    CareerModel.description.ilike(f"%{query}%")
                )
                base_query = base_query.where(search_condition)
            
            # Apply filters
            if filters:
                if "industry_ids" in filters and filters["industry_ids"]:
                    base_query = base_query.where(
                        CareerModel.industry_id.in_(filters["industry_ids"])
                    )
                
                if "experience_levels" in filters and filters["experience_levels"]:
                    base_query = base_query.where(
                        CareerModel.experience_level.in_(filters["experience_levels"])
                    )
                
                if "required_skills" in filters and filters["required_skills"]:
                    # Careers that have any of the required skills
                    skill_subquery = (
                        select(SkillRequirementModel.career_id)
                        .where(SkillRequirementModel.skill_id.in_(filters["required_skills"]))
                        .distinct()
                        .subquery()
                    )
                    base_query = base_query.where(
                        CareerModel.id.in_(select(skill_subquery))
                    )
            
            # Apply pagination
            base_query = base_query.offset(offset).limit(limit)
            
            result = await self.session.execute(base_query)
            career_models = result.scalars().all()
            
            return [self._to_domain(model) for model in career_models]
            
        except Exception as e:
            logger.error(f"Error searching careers: {str(e)}")
            raise
    
    async def save(self, career: Career) -> Career:
        """Save a career aggregate"""
        try:
            # Convert domain to model
            career_model = self._to_model(career)
            
            # Merge with session (handles both insert and update)
            self.session.add(career_model)
            
            # Handle domain events
            events = career.clear_events()
            for event in events:
                # In a real implementation, publish events to event bus
                logger.info(f"Domain event: {event.to_dict()}")
            
            await self.session.commit()
            await self.session.refresh(career_model)
            
            return self._to_domain(career_model)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving career: {str(e)}")
            raise
    
    async def save_many(self, careers: List[Career]) -> List[Career]:
        """Save multiple career aggregates in batch"""
        try:
            career_models = [self._to_model(career) for career in careers]
            
            # Bulk insert/update
            self.session.add_all(career_models)
            
            # Handle domain events
            for career in careers:
                events = career.clear_events()
                for event in events:
                    logger.info(f"Domain event: {event.to_dict()}")
            
            await self.session.commit()
            
            # Refresh all models
            saved_careers = []
            for model in career_models:
                await self.session.refresh(model)
                saved_careers.append(self._to_domain(model))
            
            return saved_careers
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving careers batch: {str(e)}")
            raise
    
    async def delete(self, career_id: str) -> bool:
        """Delete a career by ID"""
        try:
            result = await self.session.execute(
                select(CareerModel).where(CareerModel.id == career_id)
            )
            career_model = result.scalar_one_or_none()
            
            if career_model:
                await self.session.delete(career_model)
                await self.session.commit()
                return True
            
            return False
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting career {career_id}: {str(e)}")
            raise
    
    async def exists(self, career_id: str) -> bool:
        """Check if a career exists"""
        try:
            result = await self.session.execute(
                select(func.count()).where(CareerModel.id == career_id)
            )
            count = result.scalar()
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking career existence: {str(e)}")
            raise
    
    async def count(self, filters: Optional[Dict[str, any]] = None) -> int:
        """Count careers matching filters"""
        try:
            query = select(func.count()).select_from(CareerModel)
            
            if filters:
                if "industry_id" in filters:
                    query = query.where(CareerModel.industry_id == filters["industry_id"])
                if "is_active" in filters:
                    query = query.where(CareerModel.is_active == filters["is_active"])
            
            result = await self.session.execute(query)
            return result.scalar()
            
        except Exception as e:
            logger.error(f"Error counting careers: {str(e)}")
            raise
    
    async def get_skill_frequency(self, industry_id: Optional[str] = None) -> Dict[str, int]:
        """Get frequency count of skills across careers"""
        try:
            query = (
                select(
                    SkillRequirementModel.skill_id,
                    func.count(SkillRequirementModel.career_id).label('frequency')
                )
                .join(CareerModel)
                .where(CareerModel.is_active == True)
                .group_by(SkillRequirementModel.skill_id)
            )
            
            if industry_id:
                query = query.where(CareerModel.industry_id == industry_id)
            
            result = await self.session.execute(query)
            
            frequency_map = {}
            for row in result:
                frequency_map[row.skill_id] = row.frequency
            
            return frequency_map
            
        except Exception as e:
            logger.error(f"Error getting skill frequency: {str(e)}")
            raise
    
    async def get_trending_careers(
        self, 
        days: int = 30, 
        limit: int = 10
    ) -> List[Career]:
        """Get trending careers based on recent activity"""
        try:
            # For now, return recently updated careers
            # In production, this would track views, applications, etc.
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await self.session.execute(
                select(CareerModel)
                .options(
                    selectinload(CareerModel.required_skills),
                    selectinload(CareerModel.progression_paths)
                )
                .where(
                    and_(
                        CareerModel.updated_at >= cutoff_date,
                        CareerModel.is_active == True
                    )
                )
                .order_by(CareerModel.updated_at.desc())
                .limit(limit)
            )
            
            career_models = result.scalars().all()
            return [self._to_domain(model) for model in career_models]
            
        except Exception as e:
            logger.error(f"Error getting trending careers: {str(e)}")
            raise
    
    def _to_domain(self, model: CareerModel) -> Career:
        """Convert SQLAlchemy model to domain entity"""
        career = Career(
            id=model.id,
            title=model.title,
            description=model.description,
            industry_id=model.industry_id,
            experience_level=ExperienceLevel(model.experience_level),
            esco_occupation_id=model.esco_occupation_id,
            oasis_code=model.oasis_code
        )
        
        # Restore state
        career._version = model.version
        career.created_at = model.created_at
        career.updated_at = model.updated_at
        career.is_active = model.is_active
        
        # Add required skills
        for skill_model in model.required_skills:
            skill_req = career.add_skill_requirement(
                skill_id=skill_model.skill_id,
                skill_name=skill_model.skill_name,
                proficiency_level=skill_model.proficiency_level,
                importance=SkillImportance(skill_model.importance)
            )
            skill_req._id = skill_model.id
        
        # Add progression paths
        for prog_model in model.progression_paths:
            progression = career.add_progression_path(
                to_career_id=prog_model.to_career_id,
                typical_years=prog_model.typical_years,
                difficulty_score=prog_model.difficulty_score
            )
            progression._id = prog_model.id
            progression.skill_gaps = prog_model.skill_gaps or []
        
        # Add related careers
        career.related_careers = set(model.related_careers or [])
        
        # Clear events that were generated during reconstruction
        career.clear_events()
        
        return career
    
    def _to_model(self, career: Career) -> CareerModel:
        """Convert domain entity to SQLAlchemy model"""
        model = CareerModel(
            id=career.id,
            title=career.title,
            description=career.description,
            industry_id=career.industry_id,
            experience_level=career.experience_level.value,
            esco_occupation_id=career.esco_occupation_id,
            oasis_code=career.oasis_code,
            version=career.version,
            created_at=career.created_at,
            updated_at=career.updated_at,
            is_active=career.is_active,
            related_careers=list(career.related_careers)
        )
        
        # Convert required skills
        model.required_skills = [
            SkillRequirementModel(
                id=req.id,
                career_id=career.id,
                skill_id=req.skill_id,
                skill_name=req.skill_name,
                proficiency_level=req.proficiency_level,
                importance=req.importance.value
            )
            for req in career.required_skills
        ]
        
        # Convert progression paths
        model.progression_paths = [
            CareerProgressionModel(
                id=prog.id,
                from_career_id=prog.from_career_id,
                to_career_id=prog.to_career_id,
                typical_years=prog.typical_years,
                difficulty_score=prog.difficulty_score,
                skill_gaps=prog.skill_gaps
            )
            for prog in career.progression_paths
        ]
        
        return model