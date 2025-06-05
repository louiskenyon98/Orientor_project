#!/usr/bin/env python3
"""
Script de test pour vérifier le modèle UserRepresentation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.user_representation import UserRepresentation
from app.utils.database import get_db, engine
from sqlalchemy.orm import Session
from sqlalchemy import text

def test_user_representation_model():
    """Test du modèle UserRepresentation"""
    print("=== Test du modèle UserRepresentation ===")
    
    try:
        # Vérifier les colonnes du modèle
        columns = UserRepresentation.__table__.columns.keys()
        print(f"✓ Colonnes du modèle: {list(columns)}")
        
        # Tester la création d'une instance
        test_instance = UserRepresentation(
            user_id=1,
            source='test',
            format_version='v1',
            data={'test': 'data'}
        )
        print("✓ Instance UserRepresentation créée avec succès")
        
        # Tester avec une session de base de données
        db = next(get_db())
        
        # Vérifier que la table existe
        result = db.execute(text("SELECT COUNT(*) FROM user_representation")).fetchone()
        print(f"✓ Table user_representation existe, nombre d'enregistrements: {result[0]}")
        
        # Vérifier la structure de la table
        table_info = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_representation'
            ORDER BY ordinal_position
        """)).fetchall()
        
        print("✓ Structure de la table user_representation:")
        for column_name, data_type in table_info:
            print(f"  - {column_name}: {data_type}")
        
        db.close()
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_user_representation_model()
    if success:
        print("\n🎉 Tous les tests sont passés avec succès!")
    else:
        print("\n❌ Des erreurs ont été détectées.")
        sys.exit(1)