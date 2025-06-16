#!/usr/bin/env python3
"""
Script de test pour vérifier l'implémentation du service Avatar
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.avatar_service import AvatarService

async def test_avatar_service():
    """Test basique du service Avatar"""
    
    print("🧪 Test du service Avatar...")
    
    # Test de génération de description d'avatar
    user_data = {
        "user_id": 1,
        "email": "test@example.com",
        "profile": {
            "first_name": "Jean",
            "last_name": "Dupont",
            "age": 30,
            "location": "Paris",
            "bio": "Développeur passionné par l'IA"
        }
    }
    
    try:
        description = await AvatarService.generate_avatar_description(
            user_data=user_data,
            language="fr"
        )
        print(f"✅ Description générée: {description}")
        
        # Note: Le test de génération d'image nécessite une clé API OpenAI valide
        print("ℹ️  Pour tester la génération d'image, configurez OPENAI_API_KEY")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

if __name__ == "__main__":
    import asyncio
    
    print("🚀 Démarrage des tests Avatar...")
    success = asyncio.run(test_avatar_service())
    
    if success:
        print("✅ Tests terminés avec succès!")
    else:
        print("❌ Échec des tests")
        sys.exit(1)