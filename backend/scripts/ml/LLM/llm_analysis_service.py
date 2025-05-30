"""
Service pour générer des analyses LLM pour les recommandations d'emploi.
Ce fichier est un exemple d'implémentation qui peut être intégré au backend.
"""

import os
from typing import Dict, Any, Optional
import openai
from pydantic import BaseModel

# Configuration de l'API OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

class UserProfile(BaseModel):
    skills: Dict[str, float]
    experience: Optional[str] = None
    education: Optional[str] = None
    interests: Optional[str] = None

class LLMAnalysisInput(BaseModel):
    oasis_code: str
    job_description: str
    user_profile: UserProfile

class LLMAnalysisResult(BaseModel):
    personal_analysis: str
    entry_qualifications: str
    suggested_improvements: str

async def generate_llm_analysis(input_data: LLMAnalysisInput) -> LLMAnalysisResult:
    """
    Génère une analyse LLM pour une recommandation d'emploi.
    
    Args:
        input_data: Les données d'entrée pour l'analyse LLM
        
    Returns:
        Un objet LLMAnalysisResult contenant les résultats de l'analyse
    """
    # Construire le prompt pour le LLM
    skills_text = "\n".join([f"- {skill}: {score}/5" for skill, score in input_data.user_profile.skills.items()])
    
    prompt = f"""
    # Analyse d'adéquation emploi-candidat
    
    ## Informations sur l'emploi
    Code OASIS: {input_data.oasis_code}
    
    Description de l'emploi:
    {input_data.job_description}
    
    ## Profil de l'utilisateur
    
    Compétences:
    {skills_text}
    
    """
    
    if input_data.user_profile.experience:
        prompt += f"\nExpérience:\n{input_data.user_profile.experience}\n"
    
    if input_data.user_profile.education:
        prompt += f"\nFormation:\n{input_data.user_profile.education}\n"
    
    if input_data.user_profile.interests:
        prompt += f"\nIntérêts:\n{input_data.user_profile.interests}\n"
    
    prompt += """
    ## Tâches à réaliser
    
    1. Analyse personnelle: Fournir une analyse détaillée de l'adéquation entre le profil de l'utilisateur et l'emploi.
    2. Qualifications requises: Identifier les qualifications clés nécessaires pour cet emploi.
    3. Suggestions d'amélioration: Proposer des actions concrètes que l'utilisateur pourrait entreprendre pour améliorer son adéquation avec cet emploi.
    
    Veuillez structurer votre réponse en trois sections distinctes, une pour chaque tâche.
    """
    
    # Appel à l'API OpenAI
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Vous êtes un conseiller en orientation professionnelle expert qui analyse l'adéquation entre un candidat et un emploi."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Traiter la réponse
        full_response = response.choices[0].message.content
        
        # Diviser la réponse en sections
        sections = full_response.split("##")
        
        # Extraire les sections pertinentes
        personal_analysis = ""
        entry_qualifications = ""
        suggested_improvements = ""
        
        for section in sections:
            if "Analyse personnelle" in section or "Analyse personnalisée" in section or "Analyse d'adéquation" in section:
                personal_analysis = section.split(":", 1)[1].strip() if ":" in section else section.strip()
            elif "Qualifications" in section:
                entry_qualifications = section.split(":", 1)[1].strip() if ":" in section else section.strip()
            elif "Suggestions" in section or "Améliorations" in section:
                suggested_improvements = section.split(":", 1)[1].strip() if ":" in section else section.strip()
        
        # Si les sections n'ont pas été correctement identifiées, essayer une autre approche
        if not personal_analysis and not entry_qualifications and not suggested_improvements:
            parts = full_response.split("\n\n")
            if len(parts) >= 3:
                personal_analysis = parts[0]
                entry_qualifications = parts[1]
                suggested_improvements = parts[2]
        
        return LLMAnalysisResult(
            personal_analysis=personal_analysis,
            entry_qualifications=entry_qualifications,
            suggested_improvements=suggested_improvements
        )
    
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API OpenAI: {e}")
        # Retourner des valeurs par défaut en cas d'erreur
        return LLMAnalysisResult(
            personal_analysis="Analyse non disponible pour le moment.",
            entry_qualifications="Qualifications non disponibles pour le moment.",
            suggested_improvements="Suggestions non disponibles pour le moment."
        )

# Exemple d'utilisation
async def example_usage():
    input_data = LLMAnalysisInput(
        oasis_code="2512.1",
        job_description="Développeur de logiciels qui conçoit, code et teste des applications informatiques.",
        user_profile=UserProfile(
            skills={
                "creativity": 3.5,
                "leadership": 2.0,
                "digital_literacy": 4.5,
                "critical_thinking": 4.0,
                "problem_solving": 4.2
            },
            experience="2 ans d'expérience en développement web avec React et Node.js",
            education="Licence en informatique",
            interests="Intelligence artificielle, développement de jeux vidéo"
        )
    )
    
    result = await generate_llm_analysis(input_data)
    print("Analyse personnelle:", result.personal_analysis)
    print("Qualifications requises:", result.entry_qualifications)
    print("Suggestions d'amélioration:", result.suggested_improvements)

# Pour tester le script indépendamment
if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())