"""
Script de test pour vérifier la persistance des analyses LLM HEXACO.

Ce script teste que :
1. Les analyses LLM sont bien sauvegardées lors du calcul des scores
2. Les analyses sont récupérées depuis la DB lors des consultations ultérieures
3. Les analyses ne sont pas régénérées inutilement
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.LLMhexaco_service import LLMHexacoService
from app.services.hexaco_scoring_service import HexacoScoringService
from app.utils.database import get_db
from sqlalchemy import text
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_llm_persistence():
    """Test de la persistance des analyses LLM HEXACO."""
    
    print("🧪 Test de la persistance des analyses LLM HEXACO")
    print("=" * 60)
    
    # Données de test simulées
    test_user_id = 999999  # ID utilisateur fictif pour le test
    test_session_id = "test_session_hexaco_llm"
    test_assessment_version = "hexaco_100_fr"
    
    # Scores HEXACO simulés
    mock_scores = {
        "domains": {
            "Honesty-Humility": 4.2,
            "Emotionality": 3.8,
            "Extraversion": 3.5,
            "Agreeableness": 4.0,
            "Conscientiousness": 4.5,
            "Openness": 3.9
        },
        "facets": {
            "Sincerity": 4.1,
            "Fairness": 4.3,
            "Greed-Avoidance": 4.2,
            "Modesty": 4.1
        },
        "percentiles": {
            "Honesty-Humility": 85.0,
            "Emotionality": 70.0,
            "Extraversion": 60.0
        },
        "reliability": {
            "Honesty-Humility": 0.92,
            "Emotionality": 0.89
        },
        "total_responses": 100,
        "completion_rate": 1.0
    }
    
    try:
        # Obtenir une session de base de données
        db_gen = get_db()
        db = next(db_gen)
        
        print("1️⃣ Nettoyage des données de test précédentes...")
        cleanup_query = text("""
            DELETE FROM personality_profiles 
            WHERE user_id = :user_id AND profile_type = 'hexaco'
        """)
        db.execute(cleanup_query, {"user_id": test_user_id})
        db.commit()
        
        print("2️⃣ Test de génération et sauvegarde d'analyse LLM...")
        
        # Initialiser les services
        llm_service = LLMHexacoService()
        scoring_service = HexacoScoringService()
        
        # Générer une analyse LLM
        analysis = await llm_service.generate_hexaco_profile_description(
            hexaco_scores=mock_scores,
            user_profile={"user_id": test_user_id},
            language="fr"
        )
        
        print(f"✅ Analyse LLM générée ({len(analysis)} caractères)")
        print(f"📝 Extrait: {analysis[:100]}...")
        
        print("3️⃣ Test de sauvegarde du profil avec analyse...")
        
        # Créer un assessment fictif pour le test
        assessment_query = text("""
            INSERT INTO personality_assessments (
                user_id, session_id, assessment_type, assessment_version, status
            ) VALUES (
                :user_id, :session_id, 'hexaco', :version, 'completed'
            ) ON CONFLICT (session_id) DO UPDATE SET
                status = 'completed'
            RETURNING id
        """)
        
        try:
            assessment_result = db.execute(assessment_query, {
                "user_id": test_user_id,
                "session_id": test_session_id,
                "version": test_assessment_version
            }).fetchone()
            db.commit()
        except Exception as e:
            print(f"⚠️ Erreur lors de la création de l'assessment (peut être ignorée): {e}")
            db.rollback()
        
        # Sauvegarder le profil avec l'analyse
        success = scoring_service.save_hexaco_profile(
            db=db,
            user_id=test_user_id,
            session_id=test_session_id,
            scores=mock_scores,
            assessment_version=test_assessment_version,
            language="fr",
            narrative_description=analysis
        )
        
        if success:
            print("✅ Profil sauvegardé avec succès")
        else:
            print("❌ Échec de la sauvegarde du profil")
            return False
        
        print("4️⃣ Test de récupération de l'analyse depuis la DB...")
        
        # Récupérer le profil
        profile = scoring_service.get_user_hexaco_profile(
            db=db,
            user_id=test_user_id,
            assessment_version=test_assessment_version
        )
        
        if profile and profile.get("narrative_description"):
            print("✅ Analyse récupérée depuis la base de données")
            print(f"📝 Extrait récupéré: {profile['narrative_description'][:100]}...")
            
            # Vérifier que l'analyse est identique
            if profile["narrative_description"] == analysis:
                print("✅ L'analyse récupérée est identique à celle sauvegardée")
            else:
                print("❌ L'analyse récupérée diffère de celle sauvegardée")
                return False
        else:
            print("❌ Aucune analyse trouvée dans la base de données")
            return False
        
        print("5️⃣ Test de la méthode get_or_generate_personality_insights...")
        
        # Tester la récupération sans régénération
        cached_analysis = await llm_service.get_or_generate_personality_insights(
            user_id=test_user_id,
            hexaco_scores=mock_scores,
            db_session=db,
            language="fr",
            force_regenerate=False
        )
        
        if cached_analysis == analysis:
            print("✅ L'analyse a été récupérée depuis le cache (pas de régénération)")
        else:
            print("❌ L'analyse a été régénérée au lieu d'être récupérée")
            return False
        
        print("6️⃣ Nettoyage des données de test...")
        db.execute(cleanup_query, {"user_id": test_user_id})
        
        # Nettoyer l'assessment de test
        cleanup_assessment = text("""
            DELETE FROM personality_assessments 
            WHERE session_id = :session_id
        """)
        db.execute(cleanup_assessment, {"session_id": test_session_id})
        db.commit()
        
        print("✅ Données de test nettoyées")
        
        print("\n🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("✅ Les analyses LLM HEXACO sont maintenant correctement persistées")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    # Exécuter le test
    result = asyncio.run(test_llm_persistence())
    
    if result:
        print("\n✅ Test réussi - La persistance des analyses LLM fonctionne correctement")
        sys.exit(0)
    else:
        print("\n❌ Test échoué - Problème avec la persistance des analyses LLM")
        sys.exit(1)