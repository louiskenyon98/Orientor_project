#!/usr/bin/env python3
"""
Temporary script to create chat persistence tables manually
since the Alembic migration chain is broken.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app.models import (
    Base, Conversation, ChatMessage, ConversationCategory, 
    ConversationShare, UserChatAnalytics
)

load_dotenv()

def create_database_url():
    """Create database URL from environment variables"""
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def create_tables():
    """Create the chat persistence tables"""
    try:
        # Create database engine
        database_url = create_database_url()
        engine = create_engine(database_url)
        
        print("Creating chat persistence tables...")
        
        # Create all tables defined in the models
        Base.metadata.create_all(engine, tables=[
            ConversationCategory.__table__,
            Conversation.__table__,
            ChatMessage.__table__,
            ConversationShare.__table__,
            UserChatAnalytics.__table__
        ])
        
        # Create the full-text search index
        with engine.connect() as conn:
            try:
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_content_search "
                    "ON chat_messages USING gin(to_tsvector('english', content));"
                ))
                conn.commit()
                print("Created full-text search index.")
            except Exception as e:
                print(f"Note: Full-text search index may already exist: {e}")
        
        print("✅ Chat persistence tables created successfully!")
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name IN "
                "('conversations', 'chat_messages', 'conversation_categories', "
                "'conversation_shares', 'user_chat_analytics');"
            ))
            tables = [row[0] for row in result]
            print(f"Verified tables: {tables}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_tables()