#!/usr/bin/env python3
"""
Script de test pour vérifier les endpoints d'insight après les corrections
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.user_representation import UserRepresentation
from app.models.user_profile import UserProfile
from app.utils.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

def test_user_representation_structure():
    """Test de la structure du modèle UserRepresentation"""
    print("=== Test de la structure UserRepresentation ===")
    
    try:
        # Vérifier les colonnes du modèle
        columns = UserRepresentation.__table__.columns.keys()
        expected_columns = ['id', 'user_id', 'generated_at', 'source', 'format_version', 'data', 'summary', 'notes']
        
        print(f"✓ Colonnes du modèle: {list(columns)}")
        
        # Vérifier que toutes les colonnes attendues sont présentes
        missing_columns = set(expected_columns) - set(columns)
        if missing_columns:
            print(f"✗ Colonnes manquantes: {missing_columns}")
            return False
        
        # Vérifier qu'il n'y a pas de colonne 'content'
        if 'content' in columns:
            print("✗ La colonne 'content' existe encore (devrait être 'data')")
            return False
        
        print("✓ Structure du modèle UserRepresentation correcte")
        
        # Tester la création d'une instance
        test_instance = UserRepresentation(
            user_id=1,
            source='test',
            format_version='v1',
            data={'test': 'data'}
        )
        print("✓ Instance UserRepresentation créée avec succès")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False
    
    return True

def test_user_profile_structure():
    """Test de la structure du modèle UserProfile"""
    print("\n=== Test de la structure UserProfile ===")
    
    try:
        # Vérifier les colonnes du modèle
        columns = UserProfile.__table__.columns.keys()
        print(f"✓ Colonnes du modèle UserProfile: {list(columns)}")
        
        # Vérifier qu'il n'y a pas de colonne 'philosophical_description'
        if 'philosophical_description' in columns:
            print("✗ La colonne 'philosophical_description' existe encore (ne devrait pas exister)")
            return False
        
        print("✓ Structure du modèle UserProfile correcte (pas de philosophical_description)")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False
    
    return True

def test_database_connection():
    """Test de la connexion à la base de données"""
    print("\n=== Test de la connexion à la base de données ===")
    
    try:
        db = next(get_db())
        
        # Vérifier que la table user_representation existe
        result = db.execute(text("SELECT COUNT(*) FROM user_representation")).fetchone()
        print(f"✓ Table user_representation existe, nombre d'enregistrements: {result[0]}")
        
        # Vérifier la structure réelle de la table
        table_info = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_representation'
            ORDER BY ordinal_position
        """)).fetchall()
        
        print("✓ Structure réelle de la table user_representation:")
        for column_name, data_type in table_info:
            print(f"  - {column_name}: {data_type}")
        
        # Vérifier qu'il n'y a pas de colonne 'content'
        column_names = [col[0] for col in table_info]
        if 'content' in column_names:
            print("✗ La colonne 'content' existe encore dans la base de données")
            return False
        
        if 'data' not in column_names:
            print("✗ La colonne 'data' n'existe pas dans la base de données")
            return False
        
        print("✓ Structure de la base de données correcte")
        
        db.close()
        
    except Exception as e:
        print(f"✗ Erreur de base de données: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Test des corrections d'insight après les modifications\n")
    
    success = True
    success &= test_user_representation_structure()
    success &= test_user_profile_structure()
    success &= test_database_connection()
    
    if success:
        print("\n🎉 Tous les tests sont passés avec succès!")
        print("✅ Le modèle UserRepresentation utilise maintenant 'data' au lieu de 'content'")
        print("✅ Le modèle UserProfile n'a pas de 'philosophical_description'")
        print("✅ La structure de la base de données correspond aux modèles")
    else:
        print("\n❌ Des erreurs ont été détectées.")
        sys.exit(1)