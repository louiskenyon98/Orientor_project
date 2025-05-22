"""
Exemple de route FastAPI pour l'analyse LLM des recommandations d'emploi.
Ce fichier est un exemple d'implémentation qui peut être intégré au backend existant.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import SavedRecommendation, User
from schemas import LLMAnalysisInput, LLMAnalysisResult, RecommendationCreate, RecommendationResponse
from auth import get_current_user
from scripts.llm_analysis_service import generate_llm_analysis

router = APIRouter(prefix="/space", tags=["space"])

@router.post("/recommendations/llm-analysis", response_model=LLMAnalysisResult)
async def create_llm_analysis(
    input_data: LLMAnalysisInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère une analyse LLM pour une recommandation d'emploi.
    """
    try:
        # Générer l'analyse LLM
        analysis_result = await generate_llm_analysis(input_data)
        return analysis_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de l'analyse LLM: {str(e)}"
        )

@router.post("/recommendations", response_model=RecommendationResponse)
async def save_recommendation(
    recommendation: RecommendationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sauvegarde une recommandation avec les champs d'analyse LLM.
    """
    try:
        # Vérifier si la recommandation existe déjà
        existing_recommendation = db.query(SavedRecommendation).filter(
            SavedRecommendation.user_id == current_user.id,
            SavedRecommendation.oasis_code == recommendation.oasis_code
        ).first()
        
        if existing_recommendation:
            # Mettre à jour la recommandation existante
            for key, value in recommendation.dict(exclude_unset=True).items():
                setattr(existing_recommendation, key, value)
            db.commit()
            db.refresh(existing_recommendation)
            return existing_recommendation
        
        # Créer une nouvelle recommandation
        new_recommendation = SavedRecommendation(
            user_id=current_user.id,
            **recommendation.dict()
        )
        db.add(new_recommendation)
        db.commit()
        db.refresh(new_recommendation)
        return new_recommendation
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la sauvegarde de la recommandation: {str(e)}"
        )

# Exemple de mise à jour du modèle de base de données pour inclure les nouveaux champs
"""
# Dans models.py

class SavedRecommendation(Base):
    __tablename__ = "saved_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    oasis_code = Column(String, index=True)
    label = Column(String)
    description = Column(Text, nullable=True)
    main_duties = Column(Text, nullable=True)
    # ... autres champs existants ...
    
    # Nouveaux champs pour l'analyse LLM
    personal_analysis = Column(Text, nullable=True)
    entry_qualifications = Column(Text, nullable=True)
    suggested_improvements = Column(Text, nullable=True)
    
    # Relations
    user = relationship("User", back_populates="saved_recommendations")
    notes = relationship("Note", back_populates="saved_recommendation", cascade="all, delete-orphan")
"""

# Exemple de migration Alembic pour ajouter les nouveaux champs
"""
# Dans une nouvelle migration Alembic

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('saved_recommendations', sa.Column('personal_analysis', sa.Text(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('entry_qualifications', sa.Text(), nullable=True))
    op.add_column('saved_recommendations', sa.Column('suggested_improvements', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('saved_recommendations', 'personal_analysis')
    op.drop_column('saved_recommendations', 'entry_qualifications')
    op.drop_column('saved_recommendations', 'suggested_improvements')
"""