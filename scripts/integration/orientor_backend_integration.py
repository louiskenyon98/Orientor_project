"""
Orientor School Programs - Backend Integration Services
Integrates school programs with existing Orientor platform architecture
Following Orientor coding standards and service layer patterns
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func, text
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

# Orientor imports - in production, these would be actual imports
# For testing, we'll use mock/stub implementations
try:
    from app.dependencies import get_db, get_current_user
    from app.models.user import User
    from app.services.holland_service import HollandService
    from app.services.recommendation_service import RecommendationService
    from app.models.gca_results import GCAResult
    from app.models.user_profiles import UserProfile
    from app.models.saved_recommendations import SavedRecommendation
    from school_programs.models import Program, Institution, ProgramClassification, UserProgramInteraction
except ImportError:
    # Mock implementations for testing
    class User:
        def __init__(self, id=1, email="test@example.com"):
            self.id = id
            self.email = email
    
    class HollandService:
        def __init__(self, db):
            self.db = db
    
    class RecommendationService:
        def __init__(self, db):
            self.db = db
        
        @staticmethod
        async def get_user_recommendations(user_id):
            return []
    
    class GCAResult:
        def __init__(self, user_id=1, top_3_code="IRA", 
                     r_score=7.5, i_score=8.2, a_score=5.1,
                     s_score=6.3, e_score=4.8, c_score=5.9,
                     created_at=None):
            self.user_id = user_id
            self.top_3_code = top_3_code
            self.r_score = r_score
            self.i_score = i_score
            self.a_score = a_score
            self.s_score = s_score
            self.e_score = e_score
            self.c_score = c_score
            self.created_at = created_at or datetime.now()
    
    class UserProfile:
        def __init__(self, user_id=1, **kwargs):
            self.user_id = user_id
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class SavedRecommendation:
        def __init__(self, user_id=1, oasis_code="2171", 
                     label="Software Developer", description="Develops software"):
            self.user_id = user_id
            self.oasis_code = oasis_code
            self.label = label
            self.description = description
    
    class Program:
        def __init__(self, id="prog-123", title="Computer Science", 
                     program_type="technical", level="diploma", **kwargs):
            self.id = id
            self.title = title
            self.program_type = program_type
            self.level = level
            self.active = True
            # Set all other attributes from kwargs
            for k, v in kwargs.items():
                setattr(self, k, v)
            # Ensure institution exists
            if not hasattr(self, 'institution'):
                self.institution = Institution()
    
    class Institution:
        def __init__(self, id="inst-456", name="Test Institution", 
                     city="Montreal", **kwargs):
            self.id = id
            self.name = name
            self.city = city
            self.active = True
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class ProgramClassification:
        pass
    
    class UserProgramInteraction:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    def get_db():
        return None
    
    def get_current_user():
        return User()

logger = logging.getLogger(__name__)

# ================================
# Pydantic Models for API Responses
# ================================

class PersonalizedProgramResponse(BaseModel):
    """Response model for personalized program recommendations"""
    id: str
    title: str
    title_fr: Optional[str] = None
    institution_name: str
    institution_city: str
    program_type: str
    level: str
    duration_months: Optional[int] = None
    tuition_domestic: Optional[float] = None
    employment_rate: Optional[float] = None
    
    # Orientor-specific enhancements
    holland_compatibility: Optional[Dict[str, Any]] = None
    career_alignment_score: Optional[float] = None
    skill_match_score: Optional[float] = None
    recommendation_reasons: List[str] = Field(default_factory=list)
    
class CareerEducationPathway(BaseModel):
    """Career with associated education pathways"""
    career_code: str
    career_title: str
    career_description: str
    recommended_programs: List[PersonalizedProgramResponse]
    pathway_strength: float
    timeline_years: Optional[int] = None

class EducationDashboardResponse(BaseModel):
    """Complete education dashboard data for user"""
    personalized_programs: List[PersonalizedProgramResponse]
    career_pathways: List[CareerEducationPathway]
    saved_programs: List[PersonalizedProgramResponse]
    user_preferences: Dict[str, Any]
    holland_profile_summary: Optional[Dict[str, Any]] = None

# ================================
# Core Integration Service
# ================================

class OrientorEducationService:
    """
    Integrates school programs with existing Orientor services
    Follows Orientor service layer organization patterns
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.holland_service = HollandService(db)
        self.recommendation_service = RecommendationService(db)
    
    async def get_user_education_dashboard(self, user: User) -> EducationDashboardResponse:
        """
        Generate complete education dashboard for user
        Integrates with existing Orientor user profile and assessments
        """
        try:
            # Get user's Holland RIASEC profile from existing system
            holland_profile = await self._get_user_holland_profile(user.id)
            
            # Get personalized program recommendations
            personalized_programs = await self._get_personalized_programs(user, holland_profile)
            
            # Get career-education pathways using existing recommendation system
            career_pathways = await self._get_career_education_pathways(user, holland_profile)
            
            # Get user's saved programs
            saved_programs = await self._get_user_saved_programs(user.id)
            
            # Get user education preferences from profile
            user_preferences = await self._get_user_education_preferences(user.id)
            
            return EducationDashboardResponse(
                personalized_programs=personalized_programs,
                career_pathways=career_pathways,
                saved_programs=saved_programs,
                user_preferences=user_preferences,
                holland_profile_summary=holland_profile
            )
            
        except Exception as e:
            logger.error(f"Error generating education dashboard for user {user.id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate education dashboard")
    
    async def _get_user_holland_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's Holland RIASEC profile from existing GCA results"""
        try:
            # Query existing GCA results table
            latest_result = self.db.query(GCAResult).filter(
                GCAResult.user_id == user_id
            ).order_by(GCAResult.created_at.desc()).first()
            
            if not latest_result:
                return None
            
            return {
                'top_3_code': latest_result.top_3_code,
                'scores': {
                    'R': float(latest_result.r_score),
                    'I': float(latest_result.i_score),
                    'A': float(latest_result.a_score),
                    'S': float(latest_result.s_score),
                    'E': float(latest_result.e_score),
                    'C': float(latest_result.c_score)
                },
                'assessment_date': latest_result.created_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching Holland profile for user {user_id}: {e}")
            return None
    
    async def _get_personalized_programs(self, user: User, holland_profile: Optional[Dict]) -> List[PersonalizedProgramResponse]:
        """Get programs personalized for user based on Holland profile and preferences"""
        try:
            programs = []
            
            if not holland_profile:
                # Fallback to general recommendations based on user profile
                return await self._get_general_program_recommendations(user)
            
            # Get programs compatible with Holland codes
            top_codes = holland_profile.get('top_3_code', '')
            
            for code_letter in top_codes:
                compatible_programs = await self._find_programs_by_holland_code(code_letter)
                
                for program in compatible_programs:
                    # Calculate compatibility score
                    compatibility_score = await self._calculate_holland_compatibility(
                        program, holland_profile
                    )
                    
                    # Calculate career alignment score using existing saved recommendations
                    career_alignment = await self._calculate_career_alignment(user.id, program)
                    
                    # Calculate skill match score using existing user skills
                    skill_match = await self._calculate_skill_match(user.id, program)
                    
                    # Generate recommendation reasons
                    reasons = await self._generate_recommendation_reasons(
                        program, holland_profile, career_alignment, skill_match
                    )
                    
                    program_response = PersonalizedProgramResponse(
                        id=str(program.id),
                        title=program.title,
                        title_fr=program.title_fr,
                        institution_name=program.institution.name,
                        institution_city=program.institution.city,
                        program_type=program.program_type,
                        level=program.level,
                        duration_months=program.duration_months,
                        tuition_domestic=float(program.tuition_domestic) if program.tuition_domestic else None,
                        employment_rate=float(program.employment_rate) if program.employment_rate else None,
                        holland_compatibility=compatibility_score,
                        career_alignment_score=career_alignment,
                        skill_match_score=skill_match,
                        recommendation_reasons=reasons
                    )
                    
                    programs.append(program_response)
            
            # Sort by overall compatibility score
            programs.sort(key=lambda p: (
                (p.holland_compatibility.get('score', 0) * 0.4) +
                (p.career_alignment_score * 0.3) +
                (p.skill_match_score * 0.3)
            ), reverse=True)
            
            return programs[:20]  # Return top 20 recommendations
            
        except Exception as e:
            logger.error(f"Error getting personalized programs for user {user.id}: {e}")
            return []
    
    async def _get_career_education_pathways(self, user: User, holland_profile: Optional[Dict]) -> List[CareerEducationPathway]:
        """Get education pathways for user's existing career recommendations"""
        try:
            pathways = []
            
            # Get existing career recommendations from Orientor platform
            career_recs = self.db.query(SavedRecommendation).filter(
                SavedRecommendation.user_id == user.id
            ).limit(10).all()
            
            for career_rec in career_recs:
                # Find programs that lead to this career
                programs = await self._find_programs_for_career(career_rec.oasis_code)
                
                if programs:
                    # Score programs based on Holland compatibility
                    scored_programs = []
                    for program in programs:
                        program_response = await self._create_program_response(program, holland_profile)
                        scored_programs.append(program_response)
                    
                    # Calculate pathway strength based on program quality and fit
                    pathway_strength = await self._calculate_pathway_strength(
                        scored_programs, holland_profile
                    )
                    
                    pathway = CareerEducationPathway(
                        career_code=career_rec.oasis_code,
                        career_title=career_rec.label,
                        career_description=career_rec.description or "",
                        recommended_programs=scored_programs[:5],  # Top 5 programs
                        pathway_strength=pathway_strength,
                        timeline_years=self._estimate_education_timeline(scored_programs)
                    )
                    
                    pathways.append(pathway)
            
            # Sort by pathway strength
            pathways.sort(key=lambda p: p.pathway_strength, reverse=True)
            
            return pathways
            
        except Exception as e:
            logger.error(f"Error getting career education pathways for user {user.id}: {e}")
            return []
    
    async def _find_programs_by_holland_code(self, holland_code: str) -> List[Program]:
        """Find programs compatible with Holland RIASEC code"""
        
        # Holland code to CIP code mappings (from research agent's work)
        holland_to_cip = {
            'R': ['15.%', '01.%', '14.%'],  # Engineering, Agriculture, Technology
            'I': ['11.%', '26.%', '27.%', '40.%'],  # Computer Science, Biology, Math, Science
            'A': ['50.%', '09.%', '23.%'],  # Visual Arts, Communications, Media
            'S': ['51.%', '13.%', '44.%', '42.%'],  # Health, Education, Social Work, Psychology
            'E': ['52.%', '45.%'],  # Business, Public Administration
            'C': ['52.03%', '52.08%']  # Accounting, Finance
        }
        
        cip_patterns = holland_to_cip.get(holland_code, [])
        if not cip_patterns:
            return []
        
        # Query programs using CIP code patterns
        programs = self.db.query(Program).join(Institution).filter(
            and_(
                Program.active == True,
                Institution.active == True,
                or_(*[Program.cip_code.like(pattern) for pattern in cip_patterns])
            )
        ).options(selectinload(Program.institution)).limit(50).all()
        
        return programs
    
    async def _calculate_career_alignment(self, user_id: int, program: Program) -> float:
        """Calculate how well program aligns with user's career recommendations"""
        try:
            # Get user's saved career recommendations
            career_recs = self.db.query(SavedRecommendation).filter(
                SavedRecommendation.user_id == user_id
            ).all()
            
            if not career_recs:
                return 0.5  # Neutral score if no career recommendations
            
            max_alignment = 0.0
            
            for career in career_recs:
                # Check if program's career outcomes match this career
                if program.career_outcomes:
                    career_outcomes = program.career_outcomes
                    if isinstance(career_outcomes, dict) and 'job_titles' in career_outcomes:
                        job_titles = career_outcomes['job_titles']
                        
                        # Simple text matching - could be enhanced with NLP
                        career_title_lower = career.label.lower()
                        for job_title in job_titles:
                            if job_title.lower() in career_title_lower or career_title_lower in job_title.lower():
                                max_alignment = max(max_alignment, 0.9)
                            elif any(word in job_title.lower() for word in career_title_lower.split()):
                                max_alignment = max(max_alignment, 0.6)
            
            return min(max_alignment, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating career alignment: {e}")
            return 0.5
    
    async def _calculate_skill_match(self, user_id: int, program: Program) -> float:
        """Calculate how well program matches user's existing skills"""
        try:
            # Get user's skill profile from existing user_skills table
            try:
                from app.models.user_skills import UserSkill
            except ImportError:
                # Mock UserSkill for testing
                class UserSkill:
                    def __init__(self, user_id=1, creativity=7.5, leadership=6.2,
                                 digital_literacy=8.8, critical_thinking=7.9,
                                 problem_solving=8.1, analytical_thinking=8.5,
                                 collaboration=7.3):
                        self.user_id = user_id
                        self.creativity = creativity
                        self.leadership = leadership
                        self.digital_literacy = digital_literacy
                        self.critical_thinking = critical_thinking
                        self.problem_solving = problem_solving
                        self.analytical_thinking = analytical_thinking
                        self.collaboration = collaboration
            
            user_skills = self.db.query(UserSkill).filter(
                UserSkill.user_id == user_id
            ).first()
            
            if not user_skills:
                return 0.5  # Neutral score if no skills data
            
            # Map program requirements to user skills
            skill_scores = []
            
            # Check if program matches user's strong skills
            strong_skills = []
            for skill_name in ['creativity', 'leadership', 'digital_literacy', 'critical_thinking', 
                             'problem_solving', 'analytical_thinking', 'collaboration']:
                skill_value = getattr(user_skills, skill_name, None)
                if skill_value and skill_value >= 7.0:  # Strong skill (7+/10)
                    strong_skills.append(skill_name)
            
            # Simple matching based on program type and strong skills
            match_score = 0.5  # Base score
            
            if program.program_type == 'technical' and 'digital_literacy' in strong_skills:
                match_score += 0.3
            if program.program_type == 'business' and 'leadership' in strong_skills:
                match_score += 0.3
            if 'design' in program.title.lower() and 'creativity' in strong_skills:
                match_score += 0.3
            if 'research' in program.description.lower() and 'analytical_thinking' in strong_skills:
                match_score += 0.2
            
            return min(match_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating skill match: {e}")
            return 0.5
    
    async def _calculate_holland_compatibility(self, program, holland_profile):
        """Calculate Holland compatibility score for a program"""
        if not holland_profile or not holland_profile.get('top_3_code'):
            return {'score': 0.5, 'codes': []}
        
        # Simple scoring based on top Holland codes
        top_codes = holland_profile['top_3_code']
        compatibility_score = 0.0
        matching_codes = []
        
        # Map program types to Holland codes
        program_holland_map = {
            'technical': ['R', 'I'],
            'academic': ['I', 'A'],
            'business': ['E', 'C'],
            'health': ['S', 'I'],
            'creative': ['A', 'S']
        }
        
        program_codes = program_holland_map.get(program.program_type, ['I'])
        
        for i, code in enumerate(top_codes):
            if code in program_codes:
                # Higher weight for primary codes
                weight = 1.0 - (i * 0.2)
                compatibility_score += weight * 0.3
                matching_codes.append(code)
        
        return {
            'score': min(compatibility_score + 0.5, 1.0),  # Base score + compatibility
            'codes': matching_codes
        }
    
    async def _generate_recommendation_reasons(self, program, holland_profile, career_alignment, skill_match):
        """Generate human-readable recommendation reasons"""
        reasons = []
        
        if holland_profile and holland_profile.get('top_3_code'):
            top_code = holland_profile['top_3_code'][0]
            holland_descriptions = {
                'R': 'Realistic (hands-on, practical)',
                'I': 'Investigative (analytical, scientific)', 
                'A': 'Artistic (creative, expressive)',
                'S': 'Social (helping, teaching)',
                'E': 'Enterprising (leadership, business)',
                'C': 'Conventional (organized, detail-oriented)'
            }
            if top_code in holland_descriptions:
                reasons.append(f"Matches your {holland_descriptions[top_code]} personality")
        
        if career_alignment > 0.7:
            reasons.append("Strong alignment with your career goals")
        
        if skill_match > 0.7:
            reasons.append("Builds on your existing strengths")
        
        if program.employment_rate and program.employment_rate > 0.8:
            reasons.append(f"High employment rate ({float(program.employment_rate)*100:.0f}%)")
        
        if not reasons:
            reasons.append("Recommended based on your profile")
        
        return reasons
    
    async def _get_general_program_recommendations(self, user):
        """Get general program recommendations when no Holland profile available"""
        # Return empty list for now - could implement based on user demographics
        return []
    
    async def _find_programs_for_career(self, oasis_code):
        """Find programs that lead to a specific career"""
        # Mock implementation - in production would query based on career outcomes
        return []
    
    async def _create_program_response(self, program, holland_profile):
        """Create a PersonalizedProgramResponse from a Program object"""
        compatibility = await self._calculate_holland_compatibility(program, holland_profile)
        
        return PersonalizedProgramResponse(
            id=str(program.id),
            title=program.title,
            title_fr=getattr(program, 'title_fr', None),
            institution_name=program.institution.name,
            institution_city=program.institution.city,
            program_type=program.program_type,
            level=program.level,
            duration_months=program.duration_months,
            tuition_domestic=float(program.tuition_domestic) if program.tuition_domestic else None,
            employment_rate=float(program.employment_rate) if program.employment_rate else None,
            holland_compatibility=compatibility,
            career_alignment_score=0.5,  # Default
            skill_match_score=0.5,  # Default
            recommendation_reasons=await self._generate_recommendation_reasons(
                program, holland_profile, 0.5, 0.5
            )
        )
    
    async def _calculate_pathway_strength(self, programs, holland_profile):
        """Calculate overall strength of an education pathway"""
        if not programs:
            return 0.0
        
        # Average of program compatibility scores
        total_score = sum(p.holland_compatibility.get('score', 0.5) for p in programs)
        return total_score / len(programs)
    
    def _estimate_education_timeline(self, programs):
        """Estimate education timeline in years"""
        if not programs:
            return None
        
        # Take the shortest program duration
        durations = [p.duration_months for p in programs if p.duration_months]
        if not durations:
            return None
        
        return min(durations) // 12  # Convert months to years
    
    async def _get_user_saved_programs(self, user_id):
        """Get user's saved programs"""
        # Mock implementation
        return []
    
    async def _get_user_education_preferences(self, user_id):
        """Get user's education preferences"""
        # Mock implementation
        return {}
    
    async def _filter_programs_by_preferences(self, programs, preferences):
        """Filter programs based on user preferences"""
        filtered = []
        
        max_duration = preferences.get('max_duration')
        max_budget = preferences.get('max_budget')
        preferred_locations = preferences.get('preferred_locations', [])
        
        for program in programs:
            # Check duration
            if max_duration and program.duration_months and program.duration_months > max_duration:
                continue
            
            # Check budget
            if max_budget and program.tuition_domestic and float(program.tuition_domestic) > max_budget:
                continue
            
            # Check location (simplified - in real implementation would check institution location)
            if preferred_locations:
                # For mock purposes, assume all programs pass location filter
                pass
            
            filtered.append(program)
        
        return filtered

# ================================
# FastAPI Router Implementation
# ================================

router = APIRouter(prefix="/api/v1/education", tags=["education"])

@router.get("/dashboard", response_model=EducationDashboardResponse)
async def get_education_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete education dashboard for user
    Integrates with existing Orientor user assessments and recommendations
    """
    service = OrientorEducationService(db)
    dashboard = await service.get_user_education_dashboard(current_user)
    return dashboard

@router.get("/programs/personalized")
async def get_personalized_programs(
    limit: int = Query(20, ge=1, le=100),
    include_reasons: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized program recommendations based on Holland profile"""
    service = OrientorEducationService(db)
    
    # Get user's Holland profile
    holland_profile = await service._get_user_holland_profile(current_user.id)
    
    if not holland_profile:
        raise HTTPException(
            status_code=404, 
            detail="No Holland RIASEC assessment found. Please complete the assessment first."
        )
    
    programs = await service._get_personalized_programs(current_user, holland_profile)
    
    return {
        "programs": programs[:limit],
        "holland_profile": holland_profile if include_reasons else None,
        "total_available": len(programs)
    }

@router.get("/career-pathways")
async def get_career_education_pathways(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get education pathways for user's career recommendations"""
    service = OrientorEducationService(db)
    
    holland_profile = await service._get_user_holland_profile(current_user.id)
    pathways = await service._get_career_education_pathways(current_user, holland_profile)
    
    return {
        "pathways": pathways,
        "total_pathways": len(pathways)
    }

@router.post("/programs/{program_id}/save")
async def save_program(
    program_id: str,
    notes: Optional[str] = None,
    priority: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a program to user's list"""
    try:
        # Record interaction in user_program_interactions table
        interaction = UserProgramInteraction(
            user_id=current_user.id,
            program_id=program_id,
            interaction_type='saved',
            personal_notes=notes,
            priority_level=priority,
            saved_at=datetime.utcnow()
        )
        
        db.add(interaction)
        db.commit()
        
        return {"message": "Program saved successfully", "program_id": program_id}
        
    except Exception as e:
        logger.error(f"Error saving program {program_id} for user {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save program")

@router.get("/programs/saved")
async def get_saved_programs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's saved programs"""
    try:
        saved_interactions = db.query(UserProgramInteraction).filter(
            and_(
                UserProgramInteraction.user_id == current_user.id,
                UserProgramInteraction.interaction_type == 'saved'
            )
        ).order_by(UserProgramInteraction.saved_at.desc()).all()
        
        saved_programs = []
        for interaction in saved_interactions:
            program = db.query(Program).filter(Program.id == interaction.program_id).first()
            if program:
                program_response = await OrientorEducationService(db)._create_program_response(
                    program, None
                )
                saved_programs.append(program_response)
        
        return {"saved_programs": saved_programs, "total": len(saved_programs)}
        
    except Exception as e:
        logger.error(f"Error fetching saved programs for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch saved programs")

# ================================
# Integration with Existing Orientor Router Registration
# ================================

def register_education_routes(app):
    """
    Register education routes with the main Orientor FastAPI app
    Call this from your main app setup
    """
    app.include_router(router)

# ================================
# Database Migration for Integration
# ================================

INTEGRATION_MIGRATION_SQL = """
-- Add education preferences to existing user_profiles table
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS education_preferences JSONB DEFAULT '{}';
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS preferred_education_level VARCHAR(50);
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS preferred_study_locations VARCHAR(100)[] DEFAULT ARRAY[];

-- Connect saved recommendations to school programs
ALTER TABLE saved_recommendations ADD COLUMN IF NOT EXISTS related_programs UUID[] DEFAULT ARRAY[];
ALTER TABLE saved_recommendations ADD COLUMN IF NOT EXISTS education_pathway_notes TEXT;

-- Create bridge table for Holland-program mappings
CREATE TABLE IF NOT EXISTS holland_program_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    holland_code VARCHAR(6) NOT NULL,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    compatibility_score DECIMAL(3,2) DEFAULT 0.5,
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(holland_code, program_id)
);

-- Create bridge table for skill-program alignments
CREATE TABLE IF NOT EXISTS skill_program_alignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    alignment_type VARCHAR(50) DEFAULT 'related',
    alignment_strength DECIMAL(3,2) DEFAULT 0.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, program_id, alignment_type)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_holland_mappings_code ON holland_program_mappings(holland_code);
CREATE INDEX IF NOT EXISTS idx_skill_alignments_user ON skill_program_alignments(user_id);
CREATE INDEX IF NOT EXISTS idx_skill_alignments_program ON skill_program_alignments(program_id);
"""

def run_integration_migration(db_connection):
    """Run the database migration for Orientor integration"""
    try:
        db_connection.execute(text(INTEGRATION_MIGRATION_SQL))
        db_connection.commit()
        logger.info("Integration migration completed successfully")
    except Exception as e:
        logger.error(f"Error running integration migration: {e}")
        db_connection.rollback()
        raise