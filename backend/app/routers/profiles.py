from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
import logging
from app.utils.database import get_db
from app.models import User, UserProfile, UserSkill
from app.routers.user import get_current_user
from app.services.embedding_service import process_user_embedding
from app.services.peer_matching_service import generate_peer_suggestions

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Add a more detailed log message to help with debugging
logger.info("Profiles router module loaded with get_current_user from app.routes.user")

class ProfileResponse(BaseModel):
    user_id: int
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    gpa: Optional[float] = None
    hobbies: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    unique_quality: Optional[str] = None
    story: Optional[str] = None
    favorite_movie: Optional[str] = None
    favorite_book: Optional[str] = None
    favorite_celebrities: Optional[str] = None
    learning_style: Optional[str] = None
    interests: Optional[Union[str, List[str]]] = None
    # Add skill fields
    creativity: Optional[float] = None
    leadership: Optional[float] = None
    digital_literacy: Optional[float] = None
    critical_thinking: Optional[float] = None
    problem_solving: Optional[float] = None
    # Job-related fields for embeddings
    job_title: Optional[str] = None
    industry: Optional[str] = None
    years_experience: Optional[int] = None
    education_level: Optional[str] = None
    career_goals: Optional[str] = None
    skills: Optional[List[str]] = None
    analytical_thinking: Optional[float] = None
    attention_to_detail: Optional[float] = None
    collaboration: Optional[float] = None
    adaptability: Optional[float] = None
    independence: Optional[float] = None
    evaluation: Optional[float] = None
    decision_making: Optional[float] = None
    stress_tolerance: Optional[float] = None

    class Config:
        from_attributes = True

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/test")
def test_profiles_route():
    return {"message": "Profiles router is working"}

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0)
    sex: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = Field(None, ge=1)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    hobbies: Optional[str] = None
    country: Optional[str] = None
    state_province: Optional[str] = None
    unique_quality: Optional[str] = None
    story: Optional[str] = None
    favorite_movie: Optional[str] = None
    favorite_book: Optional[str] = None
    favorite_celebrities: Optional[str] = None
    learning_style: Optional[str] = None
    interests: Optional[Union[str, List[str]]] = None
    # Add skill fields
    creativity: Optional[float] = Field(None, ge=0, le=5)
    leadership: Optional[float] = Field(None, ge=0, le=5)
    digital_literacy: Optional[float] = Field(None, ge=0, le=5)
    critical_thinking: Optional[float] = Field(None, ge=0, le=5)
    problem_solving: Optional[float] = Field(None, ge=0, le=5)
    # Add cognitive traits
    analytical_thinking: Optional[float] = Field(None, ge=0, le=5)
    attention_to_detail: Optional[float] = Field(None, ge=0, le=5)
    collaboration: Optional[float] = Field(None, ge=0, le=5)
    adaptability: Optional[float] = Field(None, ge=0, le=5)
    independence: Optional[float] = Field(None, ge=0, le=5)
    evaluation: Optional[float] = Field(None, ge=0, le=5)
    decision_making: Optional[float] = Field(None, ge=0, le=5)
    stress_tolerance: Optional[float] = Field(None, ge=0, le=5)
    # Job-related fields for embeddings
    job_title: Optional[str] = None
    industry: Optional[str] = None
    years_experience: Optional[int] = Field(None, ge=0)
    education_level: Optional[str] = None
    career_goals: Optional[str] = None
    skills: Optional[List[str]] = None

@router.get("/me", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to get profile for user ID: {current_user.id}")
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if not profile:
            logger.info(f"No profile found for user ID: {current_user.id}, creating a new one")
            # If no profile exists, create a blank one to avoid 404 errors
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        # Get user skills
        skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
        response = ProfileResponse.model_validate(profile)
        
        # Add all skills to response if they exist
        if skills:
            response.creativity = skills.creativity
            response.leadership = skills.leadership
            response.digital_literacy = skills.digital_literacy
            response.critical_thinking = skills.critical_thinking
            response.problem_solving = skills.problem_solving
            response.analytical_thinking = skills.analytical_thinking
            response.attention_to_detail = skills.attention_to_detail
            response.collaboration = skills.collaboration
            response.adaptability = skills.adaptability
            response.independence = skills.independence
            response.evaluation = skills.evaluation
            response.decision_making = skills.decision_making
            response.stress_tolerance = skills.stress_tolerance
        
        return response
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")

@router.put("/update", response_model=ProfileResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Attempting to update profile for user ID: {current_user.id}")
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        if not profile:
            logger.info(f"No profile found for user ID: {current_user.id}, creating a new one")
            # Create new profile if it doesn't exist
            profile = UserProfile(user_id=current_user.id)
            db.add(profile)
        
        # Extract and remove skill fields from profile data
        skill_fields = {
            "creativity": profile_data.creativity, 
            "leadership": profile_data.leadership,
            "digital_literacy": profile_data.digital_literacy,
            "critical_thinking": profile_data.critical_thinking,
            "problem_solving": profile_data.problem_solving,
            "analytical_thinking": profile_data.analytical_thinking,
            "attention_to_detail": profile_data.attention_to_detail,
            "collaboration": profile_data.collaboration,
            "adaptability": profile_data.adaptability,
            "independence": profile_data.independence,
            "evaluation": profile_data.evaluation,
            "decision_making": profile_data.decision_making,
            "stress_tolerance": profile_data.stress_tolerance
        }
        
        # Get existing skills or create new
        skills = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first()
        if not skills:
            skills = UserSkill(user_id=current_user.id)
            db.add(skills)
        
        # Update skill fields
        for field, value in skill_fields.items():
            if value is not None:
                setattr(skills, field, value)
        
        # Convert to dict excluding the skill fields and unset values
        profile_fields = profile_data.dict(
            exclude={
                "creativity", "leadership", "digital_literacy", "critical_thinking", "problem_solving",
                "analytical_thinking", "attention_to_detail", "collaboration", "adaptability",
                "independence", "evaluation", "decision_making", "stress_tolerance"
            },
            exclude_unset=True
        )
        
        # Update profile fields
        logger.info(f"Updating profile fields: {list(profile_fields.keys())}")
        for field, value in profile_fields.items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        db.refresh(skills)
        
        # Build response with combined data
        response = ProfileResponse.model_validate(profile)
        
        # Add all skills to response
        response.creativity = skills.creativity
        response.leadership = skills.leadership
        response.digital_literacy = skills.digital_literacy
        response.critical_thinking = skills.critical_thinking
        response.problem_solving = skills.problem_solving
        response.analytical_thinking = skills.analytical_thinking
        response.attention_to_detail = skills.attention_to_detail
        response.collaboration = skills.collaboration
        response.adaptability = skills.adaptability
        response.independence = skills.independence
        response.evaluation = skills.evaluation
        response.decision_making = skills.decision_making
        response.stress_tolerance = skills.stress_tolerance
        
        # Generate user embedding based on profile data
        try:
            # Prepare profile data for embedding generation
            embedding_data = {
                "job_title": profile_data.job_title if profile_data.job_title else "",
                "industry": profile_data.industry if profile_data.industry else "",
                "years_experience": profile_data.years_experience if profile_data.years_experience else 0,
                "education_level": profile_data.education_level if profile_data.education_level else "",
                "career_goals": profile_data.career_goals if profile_data.career_goals else "",
                "skills": profile_fields.get("skills", []),
                "interests": profile_fields.get("interests", [])
            }
            
            # Process embedding generation
            embedding_success = process_user_embedding(db, current_user.id, embedding_data)
            
            if embedding_success:
                logger.info(f"Successfully generated embedding for user ID: {current_user.id}")
                
                # Generate peer suggestions
                peer_success = generate_peer_suggestions(db, current_user.id)
                if peer_success:
                    logger.info(f"Successfully generated peer suggestions for user ID: {current_user.id}")
                else:
                    logger.warning(f"Failed to generate peer suggestions for user ID: {current_user.id}")
            else:
                logger.warning(f"Failed to generate embedding for user ID: {current_user.id}")
        except Exception as e:
            logger.error(f"Error in embedding/peer suggestion process: {str(e)}")
            # Don't fail the profile update if embedding generation fails
        
        logger.info(f"Successfully updated profile for user ID: {current_user.id}")
        return response
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.get("/{user_id}", response_model=ProfileResponse)
def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get profile information for a specific user."""
    try:
        logger.info(f"Attempting to get profile for user ID: {user_id}")
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            logger.info(f"No profile found for user ID: {user_id}, creating a new one")
            # Create a new profile if it doesn't exist
            profile = UserProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        # Get user skills
        skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).first()
        response = ProfileResponse.model_validate(profile)
        
        # Add skills to response if they exist
        if skills:
            response.creativity = skills.creativity
            response.leadership = skills.leadership
            response.digital_literacy = skills.digital_literacy
            response.critical_thinking = skills.critical_thinking
            response.problem_solving = skills.problem_solving
        
        return response
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")

# Add module-level debug message after routes are defined
logger.debug("Initializing profiles router module")
logger.debug(f"Created profiles router with routes: {[route.path for route in router.routes]}") 