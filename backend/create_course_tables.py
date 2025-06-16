#!/usr/bin/env python3
"""
Script to create course analysis tables directly using SQLAlchemy
"""
from app.utils.database import engine, Base
from app.models.course import Course, PsychologicalInsight, CareerSignal, ConversationLog, CareerProfileAggregate
from app.models.user import User

def create_tables():
    """Create all tables defined in the models"""
    print("Creating course analysis tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("\nVerifying tables:")
        course_tables = ['courses', 'psychological_insights', 'career_signals', 'conversation_logs', 'career_profile_aggregates']
        
        for table in course_tables:
            if table in tables:
                print(f"✅ {table} - EXISTS")
            else:
                print(f"❌ {table} - MISSING")
        
        print(f"\nTotal tables in database: {len(tables)}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")

if __name__ == "__main__":
    create_tables()