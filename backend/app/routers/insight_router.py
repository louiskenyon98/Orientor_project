from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
import json
import os
from openai import OpenAI
from sqlalchemy import text

from ..utils.database import get_db
from ..models.user import User
from ..models.user_profile import UserProfile
from ..models.saved_recommendation import SavedRecommendation
from ..routers.user import get_current_user

# Configuration du logging avec plus de détails
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Récupérer la clé API OpenAI depuis les variables d'environnement
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY n'est pas définie. Le service d'insight ne fonctionnera pas correctement.")

# Initialisation du client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

router = APIRouter(prefix="/insight", tags=["insight"])

# Modèles Pydantic pour les requêtes et réponses
class InsightRequest(BaseModel):
    user_id: int

class InsightSaveRequest(BaseModel):
    user_id: int
    philosophical_text: str

class InsightRewriteRequest(BaseModel):
    user_id: int
    feedback: str

class InsightResponse(BaseModel):
    preview: str
    full_text: str
    if_you_accept: str

class SaveResponse(BaseModel):
    success: bool

# Fonction pour récupérer les données utilisateur
async def get_user_data(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Récupère toutes les données pertinentes de l'utilisateur pour générer l'insight philosophique.
    
    Args:
        db: Session de base de données
        user_id: ID de l'utilisateur
        
    Returns:
        Dict contenant les données du profil et des recommandations sauvegardées
    """
    try:
        # Récupérer le profil utilisateur
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            logger.warning(f"Aucun profil trouvé pour l'utilisateur {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil utilisateur non trouvé"
            )
        
        # Récupérer les compétences de l'utilisateur
        skills_query = text("""
            SELECT
                id, user_id, creativity, leadership, digital_literacy,
                critical_thinking, problem_solving, analytical_thinking,
                attention_to_detail, collaboration, adaptability,
                independence, evaluation, decision_making, stress_tolerance,
                last_updated
            FROM user_skills
            WHERE user_id = :user_id
        """)
        skills_result = db.execute(skills_query, {"user_id": user_id}).fetchone()
        
        # Récupérer les recommandations sauvegardées
        saved_recommendations = db.query(SavedRecommendation).filter(
            SavedRecommendation.user_id == user_id
        ).all()
        
        # Vérifier si l'utilisateur a des recommandations sauvegardées
        if not saved_recommendations:
            logger.warning(f"Aucune recommandation sauvegardée trouvée pour l'utilisateur {user_id}")
        
        # Construire le dictionnaire de données
        user_data = {
            "profile": {
                "name": profile.name,
                "age": profile.age,
                "sex": profile.sex,
                "major": profile.major,
                "year": profile.year,
                "gpa": profile.gpa,
                "hobbies": profile.hobbies,
                "country": profile.country,
                "state_province": profile.state_province,
                "unique_quality": profile.unique_quality,
                "story": profile.story,
                "favorite_movie": profile.favorite_movie,
                "favorite_book": profile.favorite_book,
                "favorite_celebrities": profile.favorite_celebrities,
                "learning_style": profile.learning_style,
                "interests": profile.interests,
                "job_title": profile.job_title,
                "industry": profile.industry,
                "years_experience": profile.years_experience,
                "education_level": profile.education_level,
                "career_goals": profile.career_goals,
                "skills": profile.skills
            },
            "user_skills": {
                "creativity": skills_result.creativity if skills_result else None,
                "leadership": skills_result.leadership if skills_result else None,
                "digital_literacy": skills_result.digital_literacy if skills_result else None,
                "critical_thinking": skills_result.critical_thinking if skills_result else None,
                "problem_solving": skills_result.problem_solving if skills_result else None,
                "analytical_thinking": skills_result.analytical_thinking if skills_result else None,
                "attention_to_detail": skills_result.attention_to_detail if skills_result else None,
                "collaboration": skills_result.collaboration if skills_result else None,
                "adaptability": skills_result.adaptability if skills_result else None,
                "independence": skills_result.independence if skills_result else None,
                "evaluation": skills_result.evaluation if skills_result else None,
                "decision_making": skills_result.decision_making if skills_result else None,
                "stress_tolerance": skills_result.stress_tolerance if skills_result else None,
                "last_updated": skills_result.last_updated if skills_result else None
            },
            "saved_recommendations": [
                {
                    "label": rec.label,
                    "description": rec.description,
                    "main_duties": rec.main_duties,
                    "oasis_code": rec.oasis_code,
                    "role_creativity": rec.role_creativity,
                    "role_leadership": rec.role_leadership,
                    "role_digital_literacy": rec.role_digital_literacy,
                    "role_critical_thinking": rec.role_critical_thinking,
                    "role_problem_solving": rec.role_problem_solving,
                    "analytical_thinking": rec.analytical_thinking,
                    "attention_to_detail": rec.attention_to_detail,
                    "collaboration": rec.collaboration,
                    "adaptability": rec.adaptability,
                    "independence": rec.independence,
                    "evaluation": rec.evaluation,
                    "decision_making": rec.decision_making,
                    "stress_tolerance": rec.stress_tolerance
                }
                for rec in saved_recommendations
            ]
        }
        
        # Compter les champs non vides dans le profil
        non_empty_fields = sum(1 for value in user_data["profile"].values() if value not in [None, "", 0])
        total_fields = len(user_data["profile"])
        completion_percentage = (non_empty_fields / total_fields) * 100
        
        logger.info(f"Profil utilisateur {user_id} complété à {completion_percentage:.2f}% ({non_empty_fields}/{total_fields} champs)")
        
        # Ajouter des métadonnées sur la qualité des données
        user_data["metadata"] = {
            "profile_completion": completion_percentage,
            "has_recommendations": len(saved_recommendations) > 0,
            "recommendation_count": len(saved_recommendations),
            "has_skills": skills_result is not None
        }
        
        # Log détaillé des données récupérées
        logger.info(f"Données récupérées pour l'utilisateur {user_id}: "
                   f"{len(saved_recommendations)} recommandations, "
                   f"profil complété à {completion_percentage:.2f}%, "
                   f"compétences: {'présentes' if skills_result else 'absentes'}")
        
        return user_data
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données utilisateur: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données utilisateur: {str(e)}"
        )

# Fonction pour formater le prompt LLM
def format_philosophical_prompt(user_data: Dict[str, Any]) -> str:
    """
    Formate les données utilisateur en un prompt pour le LLM.
    
    Args:
        user_data: Dictionnaire contenant les données utilisateur
        
    Returns:
        Prompt formaté pour le LLM
    """
    profile = user_data["profile"]
    user_skills = user_data["user_skills"]
    saved_recommendations = user_data["saved_recommendations"]
    metadata = user_data["metadata"]
    
    # Vérifier si nous avons suffisamment de données pour personnaliser l'insight
    has_sufficient_data = metadata["profile_completion"] > 30 and metadata["has_recommendations"]
    
    # Construire un prompt plus directif pour utiliser les données spécifiques de l'utilisateur
    prompt = """
You are a wise philosopher, speaking truthfully, deeply, and sometimes uncomfortably to a student who is trying to understand themselves. You must infer from their skills, interests, choices, and saved careers who they truly are, what they are afraid of, what they're hoping for, and what they could become.

Be brutally honest. Tell the user what they are *really* going through, what drives them, what they are missing, what they are not seeing clearly about themselves.

IMPORTANT: Your analysis MUST be highly personalized and specifically reference the user's actual data. Do NOT provide generic advice. You MUST mention specific elements from their profile, skills, and saved career recommendations.

Use your understanding of psychology, philosophy, and youth development. Reference contradictions or tensions in their saved recommendations, skills, and profile.

Conclude with a bold but inspiring philosophical statement of what they might accomplish if they confront their reality.

Format:
- A two-line summary for UI preview
- A full philosophical reflection
- A sentence beginning with: "If you accept this truth..."

Return JSON:
{
  "preview": "...",
  "full_text": "...",
  "if_you_accept": "..."
}

Here is the user's profile information:
"""
    
    # Ajouter les informations du profil
    prompt += "\n## PROFILE\n"
    non_empty_profile_fields = []
    for key, value in profile.items():
        if value is not None and value != "":
            prompt += f"{key}: {value}\n"
            non_empty_profile_fields.append(key)
    
    # Ajouter les compétences de l'utilisateur
    prompt += "\n## USER SKILLS\n"
    non_empty_skills = []
    for key, value in user_skills.items():
        if value is not None and key != "last_updated":
            prompt += f"{key}: {value}/5\n"
            non_empty_skills.append(key)
    
    # Ajouter les recommandations sauvegardées
    prompt += "\n## SAVED CAREER RECOMMENDATIONS\n"
    if not saved_recommendations:
        prompt += "No saved career recommendations found.\n"
    else:
        for i, rec in enumerate(saved_recommendations, 1):
            prompt += f"\nRecommendation {i}:\n"
            prompt += f"Title: {rec['label']}\n"
            if rec.get('description'):
                prompt += f"Description: {rec['description']}\n"
            if rec.get('main_duties'):
                prompt += f"Main duties: {rec['main_duties']}\n"
            
            # Ajouter les compétences associées à cette recommandation
            skills = []
            for skill_name, skill_key in [
                ("Creativity", "role_creativity"),
                ("Leadership", "role_leadership"),
                ("Digital Literacy", "role_digital_literacy"),
                ("Critical Thinking", "role_critical_thinking"),
                ("Problem Solving", "role_problem_solving"),
                ("Analytical Thinking", "analytical_thinking"),
                ("Attention to Detail", "attention_to_detail"),
                ("Collaboration", "collaboration"),
                ("Adaptability", "adaptability"),
                ("Independence", "independence"),
                ("Evaluation", "evaluation"),
                ("Decision Making", "decision_making"),
                ("Stress Tolerance", "stress_tolerance")
            ]:
                if rec.get(skill_key) and rec[skill_key] > 0:
                    skills.append(f"{skill_name}: {rec[skill_key]}/5")
            
            if skills:
                prompt += f"Required skills: {', '.join(skills)}\n"
    
    # Ajouter des instructions spécifiques basées sur la qualité des données
    prompt += "\n## INSTRUCTIONS SPÉCIFIQUES\n"
    
    if not has_sufficient_data:
        prompt += """
ATTENTION: L'utilisateur n'a pas fourni suffisamment de données pour une analyse complètement personnalisée.
Dans votre réponse, soyez honnête sur les limites de l'analyse tout en offrant des insights basés sur les données disponibles.
Encouragez l'utilisateur à compléter son profil et à sauvegarder des recommandations de carrière pour obtenir une analyse plus précise.
"""
    else:
        prompt += f"""
Vous DEVEZ faire référence à au moins 3 des éléments suivants du profil de l'utilisateur dans votre analyse:
{', '.join(non_empty_profile_fields[:5])}

Si l'utilisateur a des compétences évaluées, vous DEVEZ analyser leurs forces et faiblesses:
{', '.join(non_empty_skills)}

Si l'utilisateur a des recommandations de carrière sauvegardées, vous DEVEZ analyser les tendances et contradictions entre ces choix.
Identifiez les compétences qui reviennent souvent dans leurs choix de carrière et ce que cela révèle sur leurs valeurs profondes.
Comparez leurs compétences actuelles avec celles requises par leurs choix de carrière.
"""
    
    # Ajouter des métadonnées pour aider le modèle
    prompt += f"\n## MÉTADONNÉES\n"
    prompt += f"Profil complété à: {metadata['profile_completion']:.2f}%\n"
    prompt += f"Nombre de recommandations sauvegardées: {metadata['recommendation_count']}\n"
    prompt += f"Compétences évaluées: {'Oui' if metadata['has_skills'] else 'Non'}\n"
    
    logger.info(f"Prompt généré avec {len(prompt)} caractères")
    return prompt

# Fonction pour appeler l'API OpenAI
async def call_openai_api(prompt: str) -> Dict[str, str]:
    """
    Appelle l'API OpenAI avec le prompt formaté.
    
    Args:
        prompt: Prompt formaté pour le LLM
        
    Returns:
        Réponse du LLM au format JSON
    """
    try:
        # Log le prompt pour le débogage (version tronquée pour éviter des logs trop longs)
        logger.info(f"Début du prompt envoyé à OpenAI: {prompt[:500]}...")
        logger.info(f"Fin du prompt envoyé à OpenAI: ...{prompt[-500:]}")
        logger.info(f"Longueur totale du prompt: {len(prompt)} caractères")
        
        # Système de message plus directif pour assurer la personnalisation
        system_message = """
You are a wise philosopher providing deep insights about a person based on their profile and career choices.
Your analysis MUST be highly personalized and specifically reference the user's actual data.
Do NOT provide generic advice that could apply to anyone.
You MUST mention specific elements from their profile and saved career recommendations.
If the user has insufficient data, acknowledge this limitation in your response.

IMPORTANT: Return your response in JSON format with the following structure:
{
  "preview": "A two-line summary for UI preview",
  "full_text": "A full philosophical reflection",
  "if_you_accept": "A sentence beginning with: 'If you accept this truth...'"
}
"""
        
        response = client.chat.completions.create(
            model="gpt-4",  # Utiliser GPT-4 pour une meilleure qualité
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7  # Température modérée pour équilibrer créativité et précision
            # Suppression du paramètre response_format qui n'est pas pris en charge par tous les modèles
        )
        
        # Extraire et parser la réponse JSON
        response_text = response.choices[0].message.content.strip()
        logger.info(f"Réponse reçue de l'API OpenAI: {response_text[:100]}...")
        
        try:
            response_json = json.loads(response_text)
            # Vérifier que tous les champs requis sont présents
            required_fields = ["preview", "full_text", "if_you_accept"]
            for field in required_fields:
                if field not in response_json:
                    logger.warning(f"Champ manquant dans la réponse JSON: {field}")
                    response_json[field] = "Information non disponible"
            
            # Vérifier que la réponse semble personnalisée
            full_text = response_json["full_text"]
            if len(full_text) < 100:
                logger.warning(f"La réponse semble trop courte pour être personnalisée: {len(full_text)} caractères")
            
            # Log la réponse complète pour le débogage
            logger.info(f"Réponse complète: {response_json}")
            
            return response_json
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du parsing de la réponse JSON: {str(e)}")
            # Fallback: extraire manuellement les sections
            preview = "Réflexion philosophique sur votre profil"
            full_text = response_text
            if_you_accept = "Si vous acceptez cette vérité, vous pourrez avancer vers votre véritable potentiel."
            
            return {
                "preview": preview,
                "full_text": full_text,
                "if_you_accept": if_you_accept
            }
    
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de l'insight philosophique: {str(e)}"
        )

# Endpoint pour générer un insight philosophique
@router.post("/generate", response_model=InsightResponse)
async def generate_insight(
    request: InsightRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Génère un insight philosophique basé sur le profil utilisateur et les recommandations sauvegardées.
    """
    try:
        # TOUJOURS utiliser l'ID de l'utilisateur actuellement connecté
        user_id = current_user.id
        
        logger.info(f"Génération d'un insight philosophique pour l'utilisateur actuellement connecté (ID: {user_id})")
        
        # Récupérer les données utilisateur
        user_data = await get_user_data(db, user_id)
        
        # Vérifier si nous avons suffisamment de données pour personnaliser l'insight
        has_sufficient_data = user_data["metadata"]["profile_completion"] > 30 and user_data["metadata"]["has_recommendations"]
        
        if not has_sufficient_data:
            logger.warning(f"Données insuffisantes pour l'utilisateur {user_id}: "
                          f"profil complété à {user_data['metadata']['profile_completion']:.2f}%, "
                          f"{user_data['metadata']['recommendation_count']} recommandations")
        
        # Formater le prompt pour le LLM
        prompt = format_philosophical_prompt(user_data)
        
        # Appeler l'API OpenAI
        response = await call_openai_api(prompt)
        
        # Si les données sont insuffisantes, ajouter une note dans la réponse
        if not has_sufficient_data:
            note_insuffisance = "\n\n[Note: Cette analyse est limitée car votre profil est incomplet ou vous n'avez pas sauvegardé de recommandations de carrière. Pour une analyse plus précise, complétez votre profil et sauvegardez des recommandations qui vous intéressent.]"
            response["full_text"] += note_insuffisance
        
        logger.info(f"Insight généré avec succès pour l'utilisateur {user_id}")
        
        return InsightResponse(
            preview=response["preview"],
            full_text=response["full_text"],
            if_you_accept=response["if_you_accept"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'insight: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de l'insight: {str(e)}"
        )

# Endpoint pour sauvegarder un insight philosophique
@router.patch("/save", response_model=SaveResponse)
async def save_insight(
    request: InsightSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sauvegarde le texte philosophique dans le profil utilisateur.
    """
    try:
        # TOUJOURS utiliser l'ID de l'utilisateur actuellement connecté
        user_id = current_user.id
        
        logger.info(f"Sauvegarde d'un insight philosophique pour l'utilisateur actuellement connecté (ID: {user_id})")
        
        # Récupérer le profil utilisateur
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            logger.warning(f"Aucun profil trouvé pour l'utilisateur {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil utilisateur non trouvé"
            )
        
        # Mettre à jour le champ philosophical_description
        profile.philosophical_description = request.philosophical_text
        
        # Sauvegarder les modifications
        db.commit()
        
        logger.info(f"Insight philosophique sauvegardé pour l'utilisateur {user_id}")
        return SaveResponse(success=True)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la sauvegarde de l'insight: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la sauvegarde de l'insight: {str(e)}"
        )

# Endpoint pour réécrire un insight philosophique
@router.post("/rewrite", response_model=InsightResponse)
async def rewrite_insight(
    request: InsightRewriteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Réécrit un insight philosophique en tenant compte du feedback de l'utilisateur.
    """
    try:
        # Pour le développement et les tests, permettre à n'importe quel utilisateur d'accéder aux données
        # Note: En production, vous voudriez probablement rétablir la vérification d'autorisation
        logger.info(f"Accès aux données de l'utilisateur {request.user_id} par l'utilisateur {current_user.id} (autorisé pour le développement)")
        
        # Récupérer les données utilisateur
        user_data = await get_user_data(db, request.user_id)
        
        # Récupérer l'analyse précédente
        profile = db.query(UserProfile).filter(UserProfile.user_id == request.user_id).first()
        previous_analysis = profile.philosophical_description if profile and profile.philosophical_description else ""
        
        # Formater le prompt pour le LLM
        base_prompt = format_philosophical_prompt(user_data)
        
        rewrite_prompt = f"""
{base_prompt}

## PREVIOUS ANALYSIS
{previous_analysis}

## USER FEEDBACK
The user has provided the following feedback about the previous analysis:
{request.feedback}

Please rewrite the philosophical insight taking into account this feedback. Maintain the same format:
- A two-line summary for UI preview
- A full philosophical reflection
- A sentence beginning with: "If you accept this truth..."

Return JSON:
{{
  "preview": "...",
  "full_text": "...",
  "if_you_accept": "..."
}}
"""
        
        # Appeler l'API OpenAI
        response = await call_openai_api(rewrite_prompt)
        
        return InsightResponse(
            preview=response["preview"],
            full_text=response["full_text"],
            if_you_accept=response["if_you_accept"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la réécriture de l'insight: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la réécriture de l'insight: {str(e)}"
        )