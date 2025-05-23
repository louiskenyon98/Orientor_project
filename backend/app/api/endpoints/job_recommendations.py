from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from sqlalchemy.orm import Session
from app.services.job_recommendation_service import JobRecommendationService
from app.routers.user import get_current_user
from app.models.user import User
from app.utils.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
job_recommendation_service = JobRecommendationService()

# Modèles Pydantic pour les requêtes et réponses
class JobRecommendationResponse(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]
    
    # Permettre des données supplémentaires
    class Config:
        extra = "allow"

class JobRecommendationsResponse(BaseModel):
    recommendations: List[JobRecommendationResponse]
    user_id: int
    
    # Permettre des données supplémentaires
    class Config:
        extra = "allow"

class EmbeddingTypeRequest(BaseModel):
    embedding_type: Optional[str] = "esco_embedding"

class SkillTreeResponse(BaseModel):
    nodes: Dict[str, Any]
    edges: List[Dict[str, Any]]

async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if authorization:
        try:
            # Remove "Bearer " prefix if present
            token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
            return get_current_user(token=token, db=db)
        except HTTPException:
            return None
    return None

@router.get("/recommendations/{user_id}", response_model=JobRecommendationsResponse)
async def get_job_recommendations(
    user_id: int = Path(..., description="ID de l'utilisateur"),
    embedding_type: str = Query("esco_embedding", description="Type d'embedding à utiliser"),
    top_k: int = Query(3, description="Nombre de recommandations à retourner"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Récupère les recommandations d'emploi pour un utilisateur.
    """
    try:
        # Vérifier que l'utilisateur est autorisé à accéder aux recommandations
        if current_user and current_user.id != user_id:
            logger.warning(f"Tentative d'accès non autorisé aux recommandations de l'utilisateur {user_id} par l'utilisateur {current_user.id}")
            raise HTTPException(status_code=403, detail="Accès non autorisé aux recommandations de cet utilisateur")
        
        # Vérifier que le type d'embedding est valide
        valid_types = ["esco_embedding", "esco_embedding_occupation", "esco_embedding_skill", "esco_embedding_skillsgroup"]
        if embedding_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Type d'embedding invalide. Valeurs acceptées: {', '.join(valid_types)}")
        
        # Vérifier si des recommandations sont déjà stockées
        stored_recommendations = job_recommendation_service.get_stored_recommendations(db, user_id)
        
        # Si aucune recommandation n'est stockée ou si un type d'embedding spécifique est demandé,
        # générer de nouvelles recommandations
        recommendations = stored_recommendations
        if not recommendations or embedding_type != "esco_embedding":
            recommendations = job_recommendation_service.get_job_recommendations(db, user_id, embedding_type, top_k)
        
        if not recommendations:
            raise HTTPException(status_code=404, detail=f"Aucune recommandation trouvée pour l'utilisateur {user_id}")
        
        # Formater la réponse
        return {
            "recommendations": recommendations,
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des recommandations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des recommandations: {str(e)}")

@router.post("/recommendations/{user_id}", response_model=JobRecommendationsResponse)
async def generate_job_recommendations(
    user_id: int = Path(..., description="ID de l'utilisateur"),
    request: EmbeddingTypeRequest = Body(...),
    top_k: int = Query(3, description="Nombre de recommandations à retourner"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Génère de nouvelles recommandations d'emploi pour un utilisateur.
    """
    try:
        # Vérifier que l'utilisateur est autorisé à accéder aux recommandations
        if current_user and current_user.id != user_id:
            logger.warning(f"Tentative d'accès non autorisé aux recommandations de l'utilisateur {user_id} par l'utilisateur {current_user.id}")
            raise HTTPException(status_code=403, detail="Accès non autorisé aux recommandations de cet utilisateur")
        
        # Vérifier que le type d'embedding est valide
        valid_types = ["esco_embedding", "esco_embedding_occupation", "esco_embedding_skill", "esco_embedding_skillsgroup"]
        if request.embedding_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Type d'embedding invalide. Valeurs acceptées: {', '.join(valid_types)}")
        
        # Forcer la génération de nouvelles recommandations
        recommendations = job_recommendation_service.get_job_recommendations(db, user_id, request.embedding_type, top_k)
        
        if not recommendations:
            raise HTTPException(status_code=404, detail=f"Aucune recommandation trouvée pour l'utilisateur {user_id}")
        
        # Formater la réponse
        return {
            "recommendations": recommendations,
            "user_id": user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la génération des recommandations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération des recommandations: {str(e)}")

@router.get("/recommendations/me", response_model=JobRecommendationsResponse, response_model_exclude_unset=True)
async def get_current_user_job_recommendations(
    embedding_type: str = Query("esco_embedding", description="Type d'embedding à utiliser"),
    top_k: int = Query(3, description="Nombre de recommandations à retourner"),
    test_user_id: Optional[int] = Query(None, description="ID utilisateur de test (uniquement pour le débogage)"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Récupère les recommandations d'emploi pour l'utilisateur actuellement authentifié.
    """
    try:
        # Pour le débogage, permettre l'utilisation d'un ID utilisateur de test
        if test_user_id is not None:
            logger.warning(f"Utilisation de l'ID utilisateur de test: {test_user_id}")
            user_id = test_user_id
        else:
            # Vérifier que l'utilisateur est authentifié
            if not current_user:
                logger.warning("Tentative d'accès aux recommandations sans authentification")
                # Pour le débogage, utiliser un ID utilisateur par défaut au lieu de lever une exception
                user_id = 21  # Utiliser un ID utilisateur par défaut pour le débogage
                logger.warning(f"Utilisation de l'ID utilisateur par défaut: {user_id}")
            else:
                # Utiliser l'ID de l'utilisateur authentifié
                user_id = current_user.id
                logger.info(f"Utilisateur authentifié: {user_id}")
        
        # Vérifier que le type d'embedding est valide
        valid_types = ["esco_embedding", "esco_embedding_occupation", "esco_embedding_skill", "esco_embedding_skillsgroup"]
        if embedding_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Type d'embedding invalide. Valeurs acceptées: {', '.join(valid_types)}")
        
        # Vérifier si des recommandations sont déjà stockées
        stored_recommendations = job_recommendation_service.get_stored_recommendations(db, user_id)
        logger.info(f"Recommandations stockées pour l'utilisateur {user_id}: {stored_recommendations}")
        
        # Si aucune recommandation n'est stockée ou si un type d'embedding spécifique est demandé,
        # générer de nouvelles recommandations
        recommendations = stored_recommendations
        if not recommendations or embedding_type != "esco_embedding":
            logger.info(f"Génération de nouvelles recommandations pour l'utilisateur {user_id} avec le type d'embedding {embedding_type}")
            recommendations = job_recommendation_service.get_job_recommendations(db, user_id, embedding_type, top_k)
            logger.info(f"Nouvelles recommandations générées: {recommendations}")
        
        if not recommendations:
            raise HTTPException(status_code=404, detail=f"Aucune recommandation trouvée pour votre profil")
        
        # Vérifier la structure des recommandations et les corriger si nécessaire
        valid_recommendations = []
        for i, rec in enumerate(recommendations):
            logger.info(f"Recommandation {i}: {rec}")
            
            # Vérifier si la recommandation est un dictionnaire valide
            if not isinstance(rec, dict):
                logger.error(f"Recommandation {i} n'est pas un dictionnaire: {rec}")
                continue
                
            # Créer une nouvelle recommandation correctement formatée
            valid_rec = {}
            
            # Gérer l'ID
            if 'id' in rec:
                valid_rec['id'] = str(rec['id'])  # Assurer que l'ID est une chaîne
            elif 'job_id' in rec:
                valid_rec['id'] = str(rec['job_id'])
            else:
                logger.error(f"Recommandation {i} n'a pas d'ID: {rec}")
                valid_rec['id'] = f"unknown_job_{i}"  # ID par défaut
                
            # Gérer le score
            if 'score' in rec:
                valid_rec['score'] = float(rec['score'])  # Assurer que le score est un nombre
            elif 'similarity' in rec:
                valid_rec['score'] = float(rec['similarity'])
            else:
                logger.error(f"Recommandation {i} n'a pas de score: {rec}")
                valid_rec['score'] = 0.5  # Score par défaut
                
            # Gérer les métadonnées
            if 'metadata' in rec and isinstance(rec['metadata'], dict):
                valid_rec['metadata'] = rec['metadata']
            else:
                # Créer des métadonnées à partir des autres champs
                metadata = {k: v for k, v in rec.items() if k not in ['id', 'score', 'metadata']}
                if not metadata:
                    metadata = {
                        "title": f"Emploi {i+1}",
                        "description": "Aucune description disponible",
                        "preferred_label": f"Emploi {i+1}"
                    }
                valid_rec['metadata'] = metadata
                
            valid_recommendations.append(valid_rec)
            
        # Si aucune recommandation valide n'a été trouvée, créer des recommandations factices
        if not valid_recommendations:
            logger.warning("Aucune recommandation valide trouvée, création de recommandations factices")
            for i in range(3):
                valid_recommendations.append({
                    "id": f"dummy_job_{i}",
                    "score": 0.5,
                    "metadata": {
                        "title": f"Emploi exemple {i+1}",
                        "description": "Ceci est un emploi exemple pour le débogage",
                        "preferred_label": f"Emploi exemple {i+1}",
                        "skills": ["Compétence 1", "Compétence 2", "Compétence 3"]
                    }
                })
        
        # Formater la réponse
        response = {
            "recommendations": valid_recommendations,
            "user_id": user_id
        }
        
        # Log détaillé pour le débogage
        logger.info("=== DÉTAILS DE LA RÉPONSE ===")
        logger.info(f"Type de response: {type(response)}")
        logger.info(f"Type de recommendations: {type(response['recommendations'])}")
        logger.info(f"Type de user_id: {type(response['user_id'])}")
        
        for i, rec in enumerate(response['recommendations']):
            logger.info(f"Recommandation {i}:")
            logger.info(f"  Type: {type(rec)}")
            logger.info(f"  ID: {rec.get('id')} (type: {type(rec.get('id'))})")
            logger.info(f"  Score: {rec.get('score')} (type: {type(rec.get('score'))})")
            logger.info(f"  Metadata: {rec.get('metadata')} (type: {type(rec.get('metadata'))})")
            
            if 'metadata' in rec and isinstance(rec['metadata'], dict):
                for key, value in rec['metadata'].items():
                    logger.info(f"    {key}: {value} (type: {type(value)})")
        
        logger.info("=== FIN DES DÉTAILS ===")
        
        # Convertir explicitement les types pour s'assurer qu'ils correspondent au modèle Pydantic
        for rec in response['recommendations']:
            rec['id'] = str(rec['id'])
            rec['score'] = float(rec['score'])
            if not isinstance(rec['metadata'], dict):
                rec['metadata'] = {}
        
        response['user_id'] = int(response['user_id'])
        
        logger.info(f"Réponse formatée et convertie: {response}")
        
        # Tenter de valider manuellement avec le modèle Pydantic
        try:
            # Créer une instance du modèle pour vérifier la validation
            validated_response = JobRecommendationsResponse(**response)
            logger.info("Validation Pydantic réussie!")
            logger.info(f"Réponse validée: {validated_response.dict()}")
            
            # Retourner la réponse validée
            return validated_response.dict()
        except Exception as e:
            logger.error(f"ERREUR DE VALIDATION PYDANTIC: {str(e)}")
            # Retourner la réponse non validée en dernier recours
            return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des recommandations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des recommandations: {str(e)}")

@router.get("/skill-tree/{job_id}", response_model=SkillTreeResponse, response_model_exclude_unset=True)
async def get_skill_tree_for_job(
    job_id: str = Path(..., description="ID de l'emploi (format: 'occupation::key_XXXXX')"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Récupère l'arbre de compétences pour un emploi spécifique.
    """
    try:
        logger.info(f"Récupération de l'arbre de compétences pour l'emploi: {job_id}")
        
        # Vérifier que l'ID de l'emploi est valide
        if not job_id.startswith("occupation::key_"):
            logger.warning(f"Format d'ID d'emploi invalide: {job_id}")
            # Pour le débogage, corriger l'ID au lieu de lever une exception
            if job_id.startswith("dummy_job_"):
                corrected_job_id = "occupation::key_12345"
                logger.info(f"Correction de l'ID d'emploi factice: {job_id} -> {corrected_job_id}")
                job_id = corrected_job_id
            else:
                raise HTTPException(status_code=400, detail="Format d'ID d'emploi invalide. Format attendu: 'occupation::key_XXXXX'")
        
        # Générer l'arbre de compétences
        skill_tree = job_recommendation_service.generate_skill_tree_for_job(job_id)
        logger.info(f"Arbre de compétences généré: {skill_tree}")
        
        # Vérifier si l'arbre de compétences est valide
        if not skill_tree or not skill_tree.get("nodes"):
            logger.warning(f"Aucun arbre de compétences trouvé pour l'emploi {job_id}, création d'un arbre factice")
            
            # Créer un arbre de compétences factice pour le débogage
            dummy_nodes = {
                f"skill_{i}": {
                    "id": f"skill_{i}",
                    "label": f"Compétence {i}",
                    "type": "skill",
                    "level": 1,
                    "score": 0.8 - (i * 0.1)
                } for i in range(1, 6)
            }
            
            # Ajouter le nœud d'emploi
            dummy_nodes[job_id] = {
                "id": job_id,
                "label": "Emploi exemple",
                "type": "occupation",
                "level": 0
            }
            
            # Créer des arêtes
            dummy_edges = [
                {"source": job_id, "target": f"skill_{i}", "weight": 0.8 - (i * 0.1)}
                for i in range(1, 6)
            ]
            
            skill_tree = {
                "nodes": dummy_nodes,
                "edges": dummy_edges
            }
        
        # Log détaillé pour le débogage
        logger.info("=== DÉTAILS DE L'ARBRE DE COMPÉTENCES ===")
        logger.info(f"Type de skill_tree: {type(skill_tree)}")
        logger.info(f"Type de nodes: {type(skill_tree.get('nodes'))}")
        logger.info(f"Type de edges: {type(skill_tree.get('edges'))}")
        logger.info(f"Nombre de nœuds: {len(skill_tree.get('nodes', {}))}")
        logger.info(f"Nombre d'arêtes: {len(skill_tree.get('edges', []))}")
        logger.info("=== FIN DES DÉTAILS ===")
        
        # Tenter de valider manuellement avec le modèle Pydantic
        try:
            # Créer une instance du modèle pour vérifier la validation
            validated_tree = SkillTreeResponse(**skill_tree)
            logger.info("Validation Pydantic de l'arbre réussie!")
            
            # Retourner l'arbre validé
            return validated_tree.dict()
        except Exception as e:
            logger.error(f"ERREUR DE VALIDATION PYDANTIC DE L'ARBRE: {str(e)}")
            # Retourner l'arbre non validé en dernier recours
            return skill_tree
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'arbre de compétences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'arbre de compétences: {str(e)}")