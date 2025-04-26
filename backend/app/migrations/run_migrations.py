#!/usr/bin/env python3
import os
import sys
import logging
import argparse
import psycopg2
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def run_migration(migration_file):
    """Run a single migration file against the database"""
    # Get database connection settings from environment variables
    db_host = os.getenv("DB_HOST", "navigo-db.cezukgaam3m7.us-east-1.rds.amazonaws.com")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "Navigo.phil.007")

    # Read the migration SQL
    with open(migration_file, 'r') as f:
        sql = f.read()

    # Connect to the database
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        conn.autocommit = True  # Set autocommit to avoid having to manually commit the transaction
        cursor = conn.cursor()

        # Execute the migration
        logger.info(f"Running migration: {migration_file}")
        cursor.execute(sql)
        logger.info("Migration completed successfully")

    except Exception as e:
        logger.error(f"Error running migration: {str(e)}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def main():
    """Main entry point for the migration script"""
    parser = argparse.ArgumentParser(description='Run database migrations')
    parser.add_argument('--file', help='Specific migration file to run')
    parser.add_argument('--all', action='store_true', help='Run all migrations')
    args = parser.parse_args()

    # Get the directory of this script
    migrations_dir = os.path.dirname(os.path.abspath(__file__))

    if args.file:
        # Run a specific migration file
        migration_file = os.path.join(migrations_dir, args.file)
        if not os.path.exists(migration_file):
            logger.error(f"Migration file not found: {migration_file}")
            sys.exit(1)
        run_migration(migration_file)
    elif args.all:
        # Run all migration files
        migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.sql')]
        migration_files.sort()  # Sort to ensure migrations run in order
        
        for file in migration_files:
            run_migration(os.path.join(migrations_dir, file))
    else:
        logger.error("Please specify either --file or --all")
        sys.exit(1)

if __name__ == "__main__":
    main() 