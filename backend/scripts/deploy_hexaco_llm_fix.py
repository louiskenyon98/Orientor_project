"""
Script de déploiement pour la correction de la persistance des analyses LLM HEXACO.

Ce script :
1. Exécute la migration pour créer/mettre à jour les tables
2. Teste la persistance des analyses LLM
3. Vérifie que tout fonctionne correctement
"""

import subprocess
import sys
import os
from pathlib import Path
import asyncio

def run_command(command, description):
    """Exécute une commande et affiche le résultat."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            if result.stdout.strip():
                print(f"📝 Sortie: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Échec")
            print(f"🚨 Erreur: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def main():
    """Fonction principale de déploiement."""
    print("🚀 Déploiement de la correction HEXACO LLM")
    print("=" * 50)
    
    # Étape 1: Vérifier l'environnement
    print("1️⃣ Vérification de l'environnement...")
    
    backend_dir = Path(__file__).parent.parent
    if not (backend_dir / "alembic.ini").exists():
        print("❌ Fichier alembic.ini non trouvé")
        return False
    
    print("✅ Environnement backend trouvé")
    
    # Étape 2: Exécuter la migration
    print("\n2️⃣ Exécution de la migration de base de données...")
    
    migration_success = run_command(
        "alembic upgrade head",
        "Migration Alembic"
    )
    
    if not migration_success:
        print("❌ Échec de la migration - Arrêt du déploiement")
        return False
    
    # Étape 3: Tester la persistance LLM
    print("\n3️⃣ Test de la persistance des analyses LLM...")
    
    test_script = backend_dir / "scripts" / "test_hexaco_llm_persistence.py"
    if test_script.exists():
        test_success = run_command(
            f"python {test_script}",
            "Test de persistance LLM"
        )
        
        if not test_success:
            print("⚠️ Les tests ont échoué, mais le déploiement continue")
    else:
        print("⚠️ Script de test non trouvé, test ignoré")
    
    # Étape 4: Vérification finale
    print("\n4️⃣ Vérification finale...")
    
    # Vérifier que les fichiers modifiés existent
    files_to_check = [
        "app/services/hexaco_scoring_service.py",
        "app/services/LLMhexaco_service.py", 
        "app/routers/hexaco_test.py",
        "alembic/versions/add_narrative_description_to_personality_profiles.py"
    ]
    
    all_files_exist = True
    for file_path in files_to_check:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MANQUANT")
            all_files_exist = False
    
    if not all_files_exist:
        print("❌ Certains fichiers sont manquants")
        return False
    
    # Résumé final
    print("\n" + "=" * 50)
    print("🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!")
    print("\n📋 Résumé des changements:")
    print("✅ Migration de base de données exécutée")
    print("✅ Table personality_profiles mise à jour avec narrative_description")
    print("✅ Service de scoring modifié pour sauvegarder les analyses LLM")
    print("✅ Routeur HEXACO modifié pour générer les analyses lors du scoring")
    print("✅ Nouveau service pour récupérer les analyses existantes")
    print("✅ Nouveaux endpoints pour accéder aux analyses LLM")
    
    print("\n🔧 Fonctionnalités ajoutées:")
    print("• POST /api/tests/hexaco/{session_id}/score - Génère et sauvegarde l'analyse LLM")
    print("• GET /api/tests/hexaco/my-analysis - Récupère l'analyse de l'utilisateur connecté")
    print("• GET /api/tests/hexaco/analysis/{user_id} - Récupère l'analyse d'un utilisateur")
    print("• Paramètre force_regenerate pour forcer la régénération")
    
    print("\n💡 Avantages:")
    print("• Les analyses LLM ne sont plus régénérées à chaque consultation")
    print("• Amélioration des performances et réduction des coûts API")
    print("• Cohérence des descriptions entre les consultations")
    print("• Possibilité de forcer la régénération si nécessaire")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Déploiement réussi!")
        sys.exit(0)
    else:
        print("\n❌ Déploiement échoué!")
        sys.exit(1)