"""
SQLAlchemy Models for Career Service

This module defines the database models for the Career microservice
using SQLAlchemy ORM.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid

from backend.shared.infrastructure.database import Base


class CareerModel(Base):
    """SQLAlchemy model for Career entity"""
    
    __tablename__ = "careers"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic attributes
    title = Column(String(255), nullable=False, index=True)
    description = Column(String(2000), nullable=False)
    industry_id = Column(String(100), nullable=False, index=True)
    experience_level = Column(String(50), nullable=False, index=True)
    
    # External identifiers
    esco_occupation_id = Column(String(100), unique=True, nullable=True, index=True)
    oasis_code = Column(String(50), unique=True, nullable=True, index=True)
    
    # Relationships
    required_skills = relationship(
        "SkillRequirementModel", 
        back_populates="career",
        cascade="all, delete-orphan",
        lazy="select"
    )
    progression_paths = relationship(
        "CareerProgressionModel",
        foreign_keys="CareerProgressionModel.from_career_id",
        back_populates="from_career",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Additional fields
    related_careers = Column(ARRAY(String), default=list)
    
    # Versioning and timestamps
    version = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_career_industry_level', 'industry_id', 'experience_level'),
        Index('idx_career_active_updated', 'is_active', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<Career(id={self.id}, title='{self.title}', industry='{self.industry_id}')>"


class SkillRequirementModel(Base):
    """SQLAlchemy model for Skill Requirements"""
    
    __tablename__ = "skill_requirements"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    career_id = Column(String, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    
    # Skill information
    skill_id = Column(String(100), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False)
    proficiency_level = Column(Integer, nullable=False)  # 1-5
    importance = Column(String(20), nullable=False)  # critical, important, nice_to_have
    
    # Relationship
    career = relationship("CareerModel", back_populates="required_skills")
    
    # Indexes
    __table_args__ = (
        Index('idx_skill_req_career_skill', 'career_id', 'skill_id'),
        Index('idx_skill_req_skill_importance', 'skill_id', 'importance'),
    )
    
    def __repr__(self):
        return f"<SkillRequirement(id={self.id}, skill='{self.skill_name}', level={self.proficiency_level})>"


class CareerProgressionModel(Base):
    """SQLAlchemy model for Career Progression Paths"""
    
    __tablename__ = "career_progressions"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    from_career_id = Column(String, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    to_career_id = Column(String, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False)
    
    # Progression details
    typical_years = Column(Integer, nullable=False)
    difficulty_score = Column(Float, nullable=False)  # 0.0 - 1.0
    skill_gaps = Column(ARRAY(String), default=list)
    
    # Relationships
    from_career = relationship(
        "CareerModel", 
        foreign_keys=[from_career_id],
        back_populates="progression_paths"
    )
    to_career = relationship(
        "CareerModel",
        foreign_keys=[to_career_id]
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_progression_from_to', 'from_career_id', 'to_career_id'),
        Index('idx_progression_difficulty', 'difficulty_score'),
    )
    
    def __repr__(self):
        return f"<CareerProgression(from={self.from_career_id}, to={self.to_career_id}, years={self.typical_years})>"


class CareerViewLogModel(Base):
    """SQLAlchemy model for tracking career views (for trending)"""
    
    __tablename__ = "career_view_logs"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # View information
    career_id = Column(String, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    viewed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(50), nullable=True)  # search, recommendation, direct, etc.
    
    # Indexes
    __table_args__ = (
        Index('idx_view_log_career_date', 'career_id', 'viewed_at'),
        Index('idx_view_log_user_date', 'user_id', 'viewed_at'),
    )
    
    def __repr__(self):
        return f"<CareerViewLog(career={self.career_id}, user={self.user_id}, date={self.viewed_at})>"


class IndustryModel(Base):
    """SQLAlchemy model for Industries"""
    
    __tablename__ = "industries"
    
    # Primary key
    id = Column(String, primary_key=True)
    
    # Industry information
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    parent_id = Column(String, ForeignKey("industries.id"), nullable=True)
    
    # Metadata
    icon_url = Column(String(500), nullable=True)
    color_code = Column(String(7), nullable=True)  # Hex color
    
    # Relationships
    parent = relationship("IndustryModel", remote_side=[id])
    
    # Indexes
    __table_args__ = (
        Index('idx_industry_parent', 'parent_id'),
    )
    
    def __repr__(self):
        return f"<Industry(id={self.id}, name='{self.name}')>"