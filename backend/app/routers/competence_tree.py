from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..services.competence_tree_service import CompetenceTreeService
from ..utils.database import get_db

router = APIRouter(
    prefix="/competence-tree",
    tags=["competence-tree"],
    responses={404: {"description": "Not found"}},
)

# Initialiser le service
competence_tree_service = CompetenceTreeService()

@router.post("/generate", response_model=Dict[str, Any])
def generate_competence_tree(user_id: int, db: Session = Depends(get_db)):
    """
    Génère un nouvel arbre de compétences pour un utilisateur.
    """
    try:
        # Créer l'arbre de compétences
        tree_data = competence_tree_service.create_skill_tree(db, user_id)
        
        if not tree_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de la création de l'arbre de compétences"
            )
        
        # Sauvegarder l'arbre dans la base de données
        graph_id = competence_tree_service.save_skill_tree(db, user_id, tree_data)
        
        if not graph_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de la sauvegarde de l'arbre de compétences"
            )
        
        return {"graph_id": graph_id, "message": "Arbre de compétences généré avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de l'arbre de compétences: {str(e)}"
        )

@router.get("/{graph_id}", response_model=Dict[str, Any])
def get_competence_tree(graph_id: str, db: Session = Depends(get_db)):
    """
    Récupère un arbre de compétences existant.
    """
    try:
        # Récupérer l'arbre de compétences depuis la base de données
        query = db.execute(
            "SELECT tree_data FROM user_skill_trees WHERE graph_id = :graph_id",
            {"graph_id": graph_id}
        )
        result = query.fetchone()
        
        if not result or not result[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arbre de compétences avec ID {graph_id} non trouvé"
            )
        
        import json
        tree_data = json.loads(result[0])
        
        return tree_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'arbre de compétences: {str(e)}"
        )

@router.patch("/node/{node_id}/complete", response_model=Dict[str, Any])
def complete_challenge(node_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Marque un défi comme complété et accorde des XP.
    """
    try:
        # Marquer le défi comme complété
        success = competence_tree_service.complete_challenge(db, node_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Impossible de compléter le défi pour le nœud {node_id}"
            )
        
        # Émettre un événement public
        competence_tree_service.emit_public_event(db, user_id, "challenge_completed")
        
        return {"success": True, "message": "Défi complété avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la complétion du défi: {str(e)}"
        )