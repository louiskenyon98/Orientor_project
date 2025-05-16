"""
Script de test pour les embeddings OaSIS.
Ce script permet de tester la génération d'embeddings OaSIS pour un utilisateur spécifique.
"""

import os
import sys
import logging
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import numpy as np

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au chemin de recherche pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les services nécessaires
from app.services.embedding_service import (
    format_user_profile_oasis,
    generate_oasis_embedding,
    process_user_oasis_embedding,
    get_user_oasis_embedding
)
from app.services.career_recommendation_service import get_career_recommendations

def get_db_session():
    """
    Crée et retourne une session de base de données.
    """
    # Récupérer l'URL de la base de données depuis les variables d'environnement
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("La variable d'environnement DATABASE_URL n'est pas définie")
        sys.exit(1)
        
    # Créer le moteur de base de données
    engine = create_engine(database_url)
    
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def test_oasis_formatting(db: Session, user_id: int):
    """
    Teste le formatage OaSIS pour un utilisateur spécifique.
    """
    logger.info(f"Test du formatage OaSIS pour l'utilisateur {user_id}")
    
    # Formater le profil selon le style OaSIS
    formatted_profile = format_user_profile_oasis(db, user_id)
    
    if formatted_profile:
        logger.info("Profil OaSIS formaté avec succès:")
        logger.info("-" * 50)
        logger.info(formatted_profile)
        logger.info("-" * 50)
        return True
    else:
        logger.error("Échec du formatage OaSIS")
        return False

def test_oasis_embedding_generation(db: Session, user_id: int):
    """
    Teste la génération d'embeddings OaSIS pour un utilisateur spécifique.
    """
    logger.info(f"Test de la génération d'embeddings OaSIS pour l'utilisateur {user_id}")
    
    # Générer l'embedding OaSIS
    embedding = generate_oasis_embedding(db, user_id)
    
    if embedding is not None:
        logger.info("Embedding OaSIS généré avec succès:")
        logger.info(f"Dimension: {embedding.shape}")
        logger.info(f"Premières valeurs: {embedding[:5]}")
        return True
    else:
        logger.error("Échec de la génération d'embedding OaSIS")
        return False

def test_oasis_embedding_storage(db: Session, user_id: int):
    """
    Teste le stockage d'embeddings OaSIS pour un utilisateur spécifique.
    """
    logger.info(f"Test du stockage d'embeddings OaSIS pour l'utilisateur {user_id}")
    
    # Traiter l'embedding OaSIS (génération + stockage)
    success = process_user_oasis_embedding(db, user_id)
    
    if success:
        logger.info("Embedding OaSIS stocké avec succès")
        
        # Vérifier que l'embedding a bien été stocké
        embedding = get_user_oasis_embedding(db, user_id)
        if embedding is not None:
            logger.info("Embedding OaSIS récupéré avec succès:")
            logger.info(f"Dimension: {embedding.shape}")
            logger.info(f"Premières valeurs: {embedding[:5]}")
            return True
        else:
            logger.error("Échec de la récupération de l'embedding OaSIS")
            return False
    else:
        logger.error("Échec du stockage de l'embedding OaSIS")
        return False

def test_oasis_recommendations(db: Session, user_id: int):
    """
    Teste les recommandations basées sur les embeddings OaSIS pour un utilisateur spécifique.
    """
    logger.info(f"Test des recommandations OaSIS pour l'utilisateur {user_id}")
    
    try:
        # Obtenir les recommandations basées sur l'embedding OaSIS
        recommendations = get_career_recommendations(db, user_id, limit=5, use_oasis=True)
        
        if recommendations:
            logger.info("Recommandations OaSIS obtenues avec succès:")
            for i, rec in enumerate(recommendations[:5], 1):
                logger.info(f"{i}. {rec.get('title', 'N/A')} - Score: {rec.get('score', 'N/A')}")
            return True
        else:
            logger.error("Aucune recommandation OaSIS obtenue")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de l'obtention des recommandations OaSIS: {str(e)}")
        return False

def compare_recommendations(db: Session, user_id: int):
    """
    Compare les recommandations basées sur les embeddings standard et OaSIS.
    """
    logger.info(f"Comparaison des recommandations pour l'utilisateur {user_id}")
    
    try:
        # Rediriger temporairement stdout pour supprimer les logs verbeux
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
        try:
            # Obtenir les recommandations basées sur l'embedding standard
            std_recommendations = get_career_recommendations(db, user_id, limit=5, use_oasis=False)
            
            # Obtenir les recommandations basées sur l'embedding OaSIS
            oasis_recommendations = get_career_recommendations(db, user_id, limit=5, use_oasis=True)
        finally:
            # Restaurer stdout
            sys.stdout.close()
            sys.stdout = original_stdout
        
        if std_recommendations and oasis_recommendations:
            logger.info("Recommandations standard:")
            for i, rec in enumerate(std_recommendations[:5], 1):
                logger.info(f"{i}. {rec.get('title', 'N/A')} - Score: {rec.get('score', 'N/A')}")
                
            logger.info("\nRecommandations OaSIS:")
            for i, rec in enumerate(oasis_recommendations[:5], 1):
                logger.info(f"{i}. {rec.get('title', 'N/A')} - Score: {rec.get('score', 'N/A')}")
                
            # Calculer le chevauchement entre les deux ensembles de recommandations
            std_titles = {rec.get('title') for rec in std_recommendations}
            oasis_titles = {rec.get('title') for rec in oasis_recommendations}
            overlap = std_titles.intersection(oasis_titles)
            
            logger.info(f"\nChevauchement: {len(overlap)} sur 5 recommandations")
            logger.info(f"Recommandations communes: {overlap}")
            
            return True
        else:
            logger.error("Impossible d'obtenir les deux ensembles de recommandations")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la comparaison des recommandations: {str(e)}")
        return False

def main():
    """
    Fonction principale du script.
    """
    parser = argparse.ArgumentParser(description="Test des embeddings OaSIS")
    parser.add_argument("--user_id", type=int, required=True, help="ID de l'utilisateur à tester")
    parser.add_argument("--format", action="store_true", help="Tester le formatage OaSIS")
    parser.add_argument("--generate", action="store_true", help="Tester la génération d'embeddings OaSIS")
    parser.add_argument("--store", action="store_true", help="Tester le stockage d'embeddings OaSIS")
    parser.add_argument("--recommend", action="store_true", help="Tester les recommandations OaSIS")
    parser.add_argument("--compare", action="store_true", help="Comparer les recommandations standard et OaSIS")
    parser.add_argument("--all", action="store_true", help="Exécuter tous les tests")
    
    args = parser.parse_args()
    
    # Si aucune option n'est spécifiée, afficher l'aide
    if not (args.format or args.generate or args.store or args.recommend or args.compare or args.all):
        parser.print_help()
        sys.exit(1)
    
    # Obtenir une session de base de données
    db = get_db_session()
    
    try:
        # Exécuter les tests demandés
        if args.all or args.format:
            test_oasis_formatting(db, args.user_id)
            
        if args.all or args.generate:
            test_oasis_embedding_generation(db, args.user_id)
            
        if args.all or args.store:
            test_oasis_embedding_storage(db, args.user_id)
            
        if args.all or args.recommend:
            test_oasis_recommendations(db, args.user_id)
            
        if args.all or args.compare:
            compare_recommendations(db, args.user_id)
            
    finally:
        # Fermer la session de base de données
        db.close()

if __name__ == "__main__":
    main()