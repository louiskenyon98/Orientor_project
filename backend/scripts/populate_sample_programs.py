#!/usr/bin/env python3
"""
Sample Program Data Population Script

This script adds sample CEGEP and university programs for testing purposes.
Run this after creating the database tables to have some data to work with.
"""

import asyncio
import sys
import os
from uuid import uuid4

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_db

# Sample program data
SAMPLE_PROGRAMS = [
    # CEGEP Programs
    {
        "title": "Computer Science Technology",
        "title_fr": "Technologie de l'informatique",
        "institution_name": "Dawson College",
        "institution_type": "cegep",
        "city": "Montreal",
        "province": "QC",
        "program_type": "technical",
        "level": "diploma",
        "duration_months": 36,
        "language": ["en", "fr"],
        "description": "Learn programming, databases, web development, and software engineering principles.",
        "field_of_study": "Computer Science",
        "tuition_domestic": 184.0,  # CEGEP tuition per semester
        "employment_rate": 0.92
    },
    {
        "title": "Health Sciences",
        "title_fr": "Sciences de la santé",
        "institution_name": "Collège de Maisonneuve",
        "institution_type": "cegep",
        "city": "Montreal",
        "province": "QC",
        "program_type": "pre-university",
        "level": "diploma",
        "duration_months": 24,
        "language": ["fr"],
        "description": "Prepare for university studies in medicine, nursing, and health sciences.",
        "field_of_study": "Health Sciences",
        "tuition_domestic": 184.0,
        "employment_rate": 0.88
    },
    {
        "title": "Business Administration",
        "title_fr": "Administration des affaires",
        "institution_name": "Champlain College",
        "institution_type": "cegep",
        "city": "Quebec City",
        "province": "QC",
        "program_type": "technical",
        "level": "diploma",
        "duration_months": 36,
        "language": ["en"],
        "description": "Comprehensive business education covering management, finance, and marketing.",
        "field_of_study": "Business",
        "tuition_domestic": 184.0,
        "employment_rate": 0.85
    },
    
    # University Programs
    {
        "title": "Bachelor of Computer Science",
        "title_fr": "Baccalauréat en informatique",
        "institution_name": "McGill University",
        "institution_type": "university",
        "city": "Montreal",
        "province": "QC",
        "program_type": "academic",
        "level": "bachelor",
        "duration_months": 48,
        "language": ["en"],
        "description": "Comprehensive computer science education with focus on algorithms, software engineering, and AI.",
        "field_of_study": "Computer Science",
        "tuition_domestic": 4536.0,  # Per year
        "employment_rate": 0.95
    },
    {
        "title": "Bachelor of Engineering",
        "title_fr": "Baccalauréat en génie",
        "institution_name": "École Polytechnique Montréal",
        "institution_type": "university",
        "city": "Montreal",
        "province": "QC",
        "program_type": "academic",
        "level": "bachelor",
        "duration_months": 48,
        "language": ["fr"],
        "description": "Professional engineering program with multiple specializations available.",
        "field_of_study": "Engineering",
        "tuition_domestic": 4500.0,
        "employment_rate": 0.96
    },
    {
        "title": "Bachelor of Medicine",
        "title_fr": "Doctorat en médecine",
        "institution_name": "Université de Montréal",
        "institution_type": "university",
        "city": "Montreal",
        "province": "QC",
        "program_type": "professional",
        "level": "professional",
        "duration_months": 60,
        "language": ["fr"],
        "description": "Medical degree program preparing students for medical practice.",
        "field_of_study": "Medicine",
        "tuition_domestic": 4800.0,
        "employment_rate": 0.98
    },
    {
        "title": "Bachelor of Arts in Psychology",
        "institution_name": "Concordia University",
        "institution_type": "university",
        "city": "Montreal",
        "province": "QC",
        "program_type": "academic",
        "level": "bachelor",
        "duration_months": 36,
        "language": ["en"],
        "description": "Study human behavior, cognition, and mental processes.",
        "field_of_study": "Psychology",
        "tuition_domestic": 4200.0,
        "employment_rate": 0.82
    },
    {
        "title": "Master of Business Administration",
        "institution_name": "HEC Montréal",
        "institution_type": "university",
        "city": "Montreal",
        "province": "QC",
        "program_type": "academic",
        "level": "master",
        "duration_months": 24,
        "language": ["en", "fr"],
        "description": "Advanced business education for future leaders and entrepreneurs.",
        "field_of_study": "Business",
        "tuition_domestic": 8500.0,
        "employment_rate": 0.94
    },
    
    # Ontario Universities
    {
        "title": "Bachelor of Computer Science",
        "institution_name": "University of Toronto",
        "institution_type": "university",
        "city": "Toronto",
        "province": "ON",
        "program_type": "academic",
        "level": "bachelor",
        "duration_months": 48,
        "language": ["en"],
        "description": "World-renowned computer science program with cutting-edge research opportunities.",
        "field_of_study": "Computer Science",
        "tuition_domestic": 6100.0,
        "employment_rate": 0.97
    },
    {
        "title": "Bachelor of Engineering Science",
        "institution_name": "University of Waterloo",
        "institution_type": "university",
        "city": "Waterloo",
        "province": "ON",
        "program_type": "academic",
        "level": "bachelor",
        "duration_months": 48,
        "language": ["en"],
        "description": "Innovative engineering program with mandatory co-op experience.",
        "field_of_study": "Engineering",
        "tuition_domestic": 6200.0,
        "employment_rate": 0.96
    }
]

def get_database_url():
    """Get database URL from environment or use default"""
    import os
    return os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/orientor')

async def populate_sample_data():
    """Populate database with sample program data"""
    
    print("🎓 Starting sample program data population...")
    
    try:
        # This would need to be adapted to your actual database connection method
        print("Note: This script needs to be integrated with your actual database connection.")
        print("Sample programs prepared:")
        
        for i, program in enumerate(SAMPLE_PROGRAMS, 1):
            print(f"  {i}. {program['title']} at {program['institution_name']}")
        
        print(f"\nTotal programs prepared: {len(SAMPLE_PROGRAMS)}")
        print("\nTo actually populate your database, you'll need to:")
        print("1. Run the Alembic migration: `alembic upgrade head`")
        print("2. Use your database connection to insert these programs")
        print("3. Update the API endpoints to query real data instead of mock responses")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating sample data: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(populate_sample_data())
    if success:
        print("✅ Sample program data preparation completed!")
    else:
        print("❌ Sample program data preparation failed!")