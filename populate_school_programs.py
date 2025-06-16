#!/usr/bin/env python3
"""
School Programs Data Population Script

This script populates the database with realistic Quebec CEGEP and university program data.
It creates comprehensive sample data that represents the actual educational landscape in Quebec.
"""
import os
import random
import psycopg2
from psycopg2.extras import execute_values, Json
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any

# Quebec Educational Data
QUEBEC_CEGEPS = [
    {"name": "Dawson College", "city": "Montreal", "website": "https://www.dawsoncollege.qc.ca"},
    {"name": "John Abbott College", "city": "Sainte-Anne-de-Bellevue", "website": "https://www.johnabbott.qc.ca"},
    {"name": "Vanier College", "city": "Montreal", "website": "https://www.vaniercollege.qc.ca"},
    {"name": "Marianopolis College", "city": "Montreal", "website": "https://www.marianopolis.edu"},
    {"name": "Champlain College", "city": "Saint-Lambert", "website": "https://www.champlaincollege.qc.ca"},
    {"name": "Heritage College", "city": "Gatineau", "website": "https://www.cegep-heritage.qc.ca"},
    {"name": "Cégep de Saint-Laurent", "city": "Montreal", "name_fr": "Cégep de Saint-Laurent", "website": "https://www.cegepsl.qc.ca"},
    {"name": "Cégep du Vieux Montréal", "city": "Montreal", "name_fr": "Cégep du Vieux Montréal", "website": "https://www.cvm.qc.ca"},
    {"name": "Cégep de Maisonneuve", "city": "Montreal", "name_fr": "Cégep de Maisonneuve", "website": "https://www.cmaisonneuve.qc.ca"},
    {"name": "Collège de Bois-de-Boulogne", "city": "Montreal", "name_fr": "Collège de Bois-de-Boulogne", "website": "https://www.bdeb.qc.ca"},
    {"name": "Cégep André-Laurendeau", "city": "Lasalle", "name_fr": "Cégep André-Laurendeau", "website": "https://www.claurendeau.qc.ca"},
    {"name": "Cégep de l'Abitibi-Témiscamingue", "city": "Rouyn-Noranda", "name_fr": "Cégep de l'Abitibi-Témiscamingue", "website": "https://www.cegepat.qc.ca"},
    {"name": "Cégep de Sherbrooke", "city": "Sherbrooke", "name_fr": "Cégep de Sherbrooke", "website": "https://www.cegepsherbrooke.qc.ca"},
    {"name": "Cégep Limoilou", "city": "Quebec City", "name_fr": "Cégep Limoilou", "website": "https://www.cegeplimoilou.ca"},
    {"name": "Cégep de Sainte-Foy", "city": "Quebec City", "name_fr": "Cégep de Sainte-Foy", "website": "https://www.cegep-ste-foy.qc.ca"},
]

QUEBEC_UNIVERSITIES = [
    {"name": "McGill University", "city": "Montreal", "website": "https://www.mcgill.ca"},
    {"name": "Université de Montréal", "city": "Montreal", "name_fr": "Université de Montréal", "website": "https://www.umontreal.ca"},
    {"name": "Université du Québec à Montréal", "city": "Montreal", "name_fr": "Université du Québec à Montréal", "website": "https://uqam.ca"},
    {"name": "Concordia University", "city": "Montreal", "website": "https://www.concordia.ca"},
    {"name": "Université Laval", "city": "Quebec City", "name_fr": "Université Laval", "website": "https://www.ulaval.ca"},
    {"name": "Université de Sherbrooke", "city": "Sherbrooke", "name_fr": "Université de Sherbrooke", "website": "https://www.usherbrooke.ca"},
    {"name": "École Polytechnique Montréal", "city": "Montreal", "name_fr": "École Polytechnique Montréal", "website": "https://www.polymtl.ca"},
    {"name": "HEC Montréal", "city": "Montreal", "website": "https://www.hec.ca"},
    {"name": "École de technologie supérieure", "city": "Montreal", "name_fr": "École de technologie supérieure", "website": "https://www.etsmtl.ca"},
    {"name": "Université du Québec à Trois-Rivières", "city": "Trois-Rivières", "name_fr": "Université du Québec à Trois-Rivières", "website": "https://www.uqtr.ca"},
    {"name": "Université du Québec en Outaouais", "city": "Gatineau", "name_fr": "Université du Québec en Outaouais", "website": "https://uqo.ca"},
    {"name": "Université du Québec à Chicoutimi", "city": "Chicoutimi", "name_fr": "Université du Québec à Chicoutimi", "website": "https://www.uqac.ca"},
    {"name": "Université du Québec en Abitibi-Témiscamingue", "city": "Rouyn-Noranda", "name_fr": "Université du Québec en Abitibi-Témiscamingue", "website": "https://www.uqat.ca"},
]

# Program Data Templates
CEGEP_PROGRAMS = [
    # Pre-University Programs
    {"title": "Science Program", "title_fr": "Programme Sciences", "program_type": "pre-university", "level": "diploma", "duration_months": 24, "cip_code": "30.0000"},
    {"title": "Social Science", "title_fr": "Sciences humaines", "program_type": "pre-university", "level": "diploma", "duration_months": 24, "cip_code": "45.0000"},
    {"title": "Liberal Arts", "title_fr": "Arts, lettres et communication", "program_type": "pre-university", "level": "diploma", "duration_months": 24, "cip_code": "23.0101"},
    {"title": "Creative Arts", "title_fr": "Arts visuels", "program_type": "pre-university", "level": "diploma", "duration_months": 24, "cip_code": "50.0000"},
    {"title": "Music", "title_fr": "Musique", "program_type": "pre-university", "level": "diploma", "duration_months": 24, "cip_code": "50.0901"},
    
    # Technical Programs
    {"title": "Computer Science Technology", "title_fr": "Techniques de l'informatique", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "11.0201"},
    {"title": "Nursing", "title_fr": "Soins infirmiers", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "51.3801"},
    {"title": "Business Administration", "title_fr": "Techniques de comptabilité et de gestion", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "52.0301"},
    {"title": "Early Childhood Education", "title_fr": "Techniques d'éducation à l'enfance", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "19.0709"},
    {"title": "Mechanical Engineering Technology", "title_fr": "Technologie du génie mécanique", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "15.0805"},
    {"title": "Electrical Engineering Technology", "title_fr": "Technologie de l'électronique industrielle", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "15.0303"},
    {"title": "Civil Engineering Technology", "title_fr": "Technologie du génie civil", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "15.0201"},
    {"title": "Architectural Technology", "title_fr": "Technologie de l'architecture", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "15.0101"},
    {"title": "Graphic Design", "title_fr": "Techniques de design graphique", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "50.0409"},
    {"title": "Social Service Technology", "title_fr": "Techniques de travail social", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "44.0000"},
    {"title": "Police Technology", "title_fr": "Techniques policières", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "43.0107"},
    {"title": "Biomedical Laboratory Technology", "title_fr": "Techniques de laboratoire médical", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "51.1004"},
    {"title": "Hotel Management", "title_fr": "Gestion hôtelière", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "52.0901"},
    {"title": "Tourism", "title_fr": "Techniques du tourisme", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "52.0901"},
    {"title": "Photography", "title_fr": "Techniques de photographie", "program_type": "technical", "level": "diploma", "duration_months": 36, "cip_code": "50.0605"},
]

UNIVERSITY_PROGRAMS = [
    # Bachelor's Programs
    {"title": "Computer Science", "title_fr": "Informatique", "program_type": "academic", "level": "bachelor", "duration_months": 48, "cip_code": "11.0701"},
    {"title": "Engineering", "title_fr": "Génie", "program_type": "academic", "level": "bachelor", "duration_months": 48, "cip_code": "14.0000"},
    {"title": "Medicine", "title_fr": "Médecine", "program_type": "professional", "level": "professional", "duration_months": 60, "cip_code": "51.1201"},
    {"title": "Law", "title_fr": "Droit", "program_type": "professional", "level": "professional", "duration_months": 36, "cip_code": "22.0101"},
    {"title": "Business Administration", "title_fr": "Administration des affaires", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "52.0201"},
    {"title": "Psychology", "title_fr": "Psychologie", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "42.0101"},
    {"title": "Biology", "title_fr": "Biologie", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "26.0101"},
    {"title": "Chemistry", "title_fr": "Chimie", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "40.0501"},
    {"title": "Physics", "title_fr": "Physique", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "40.0801"},
    {"title": "Mathematics", "title_fr": "Mathématiques", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "27.0101"},
    {"title": "Economics", "title_fr": "Économique", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "45.0601"},
    {"title": "Political Science", "title_fr": "Science politique", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "45.1001"},
    {"title": "Sociology", "title_fr": "Sociologie", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "45.1101"},
    {"title": "History", "title_fr": "Histoire", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "54.0101"},
    {"title": "Literature", "title_fr": "Littérature", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "23.0000"},
    {"title": "Philosophy", "title_fr": "Philosophie", "program_type": "academic", "level": "bachelor", "duration_months": 36, "cip_code": "38.0101"},
    {"title": "Education", "title_fr": "Éducation", "program_type": "academic", "level": "bachelor", "duration_months": 48, "cip_code": "13.0000"},
    {"title": "Nursing", "title_fr": "Sciences infirmières", "program_type": "professional", "level": "bachelor", "duration_months": 36, "cip_code": "51.3818"},
    {"title": "Social Work", "title_fr": "Travail social", "program_type": "professional", "level": "bachelor", "duration_months": 48, "cip_code": "44.0701"},
    {"title": "Architecture", "title_fr": "Architecture", "program_type": "professional", "level": "bachelor", "duration_months": 60, "cip_code": "04.0201"},
    
    # Master's Programs
    {"title": "Master of Business Administration", "title_fr": "Maîtrise en administration des affaires", "program_type": "academic", "level": "master", "duration_months": 24, "cip_code": "52.0201"},
    {"title": "Master of Engineering", "title_fr": "Maîtrise en génie", "program_type": "academic", "level": "master", "duration_months": 24, "cip_code": "14.0000"},
    {"title": "Master of Science", "title_fr": "Maîtrise en sciences", "program_type": "academic", "level": "master", "duration_months": 24, "cip_code": "30.0000"},
    {"title": "Master of Arts", "title_fr": "Maîtrise en arts", "program_type": "academic", "level": "master", "duration_months": 24, "cip_code": "50.0000"},
    {"title": "Master of Education", "title_fr": "Maîtrise en éducation", "program_type": "academic", "level": "master", "duration_months": 24, "cip_code": "13.0000"},
    
    # PhD Programs
    {"title": "Doctor of Philosophy in Computer Science", "title_fr": "Doctorat en informatique", "program_type": "academic", "level": "phd", "duration_months": 60, "cip_code": "11.0701"},
    {"title": "Doctor of Philosophy in Biology", "title_fr": "Doctorat en biologie", "program_type": "academic", "level": "phd", "duration_months": 60, "cip_code": "26.0101"},
    {"title": "Doctor of Philosophy in Physics", "title_fr": "Doctorat en physique", "program_type": "academic", "level": "phd", "duration_months": 60, "cip_code": "40.0801"},
    {"title": "Doctor of Philosophy in Psychology", "title_fr": "Doctorat en psychologie", "program_type": "academic", "level": "phd", "duration_months": 60, "cip_code": "42.0101"},
]

def generate_program_data(institution: Dict, program_template: Dict, source_system: str) -> Dict:
    """Generate comprehensive program data"""
    
    # Create unique identifiers
    source_id = f"{institution['name'].replace(' ', '_').lower()}_{program_template['title'].replace(' ', '_').lower()}"
    
    # Generate employment rate (higher for professional programs)
    if program_template.get('program_type') == 'professional':
        employment_rate = random.uniform(0.85, 0.95)
    elif program_template.get('program_type') == 'technical':
        employment_rate = random.uniform(0.75, 0.90)
    else:
        employment_rate = random.uniform(0.65, 0.85)
    
    # Generate tuition costs (Quebec has lower tuition)
    if source_system == 'cegep':
        tuition_domestic = random.uniform(200, 500)  # CEGEP is very affordable
        tuition_international = random.uniform(8000, 15000)
    else:
        if institution.get('name_fr'):  # French university
            tuition_domestic = random.uniform(2500, 4000)
            tuition_international = random.uniform(15000, 25000)
        else:  # English university
            tuition_domestic = random.uniform(3500, 6000)
            tuition_international = random.uniform(20000, 35000)
    
    # Generate realistic descriptions
    if program_template.get('title_fr'):
        description_fr = f"Ce programme de {program_template['title_fr'].lower()} offre une formation complète dans le domaine."
    else:
        description_fr = None
        
    description = f"The {program_template['title']} program provides comprehensive training in the field."
    
    # Determine language based on institution
    if institution.get('name_fr'):
        languages = ['fr', 'en'] if random.random() > 0.3 else ['fr']
    else:
        languages = ['en', 'fr'] if random.random() > 0.7 else ['en']
    
    program_data = {
        'title': program_template['title'],
        'title_fr': program_template.get('title_fr'),
        'description': description,
        'description_fr': description_fr,
        'program_type': program_template['program_type'],
        'level': program_template['level'],
        'field_of_study': program_template['title'].split()[0],  # First word as field
        'duration_months': program_template['duration_months'],
        'credits': program_template['duration_months'] * 2.5,  # Rough estimate
        'language': languages,
        'delivery_mode': random.choice(['in-person', 'hybrid']) if random.random() > 0.8 else 'in-person',
        'cip_code': program_template.get('cip_code'),
        'program_code': f"{program_template['cip_code'][:2]}-{random.randint(100, 999)}" if program_template.get('cip_code') else None,
        'admission_requirements': Json(['High school diploma', 'Application form']),
        'prerequisite_courses': Json([]),
        'min_gpa': random.uniform(2.5, 3.5) if random.random() > 0.5 else None,
        'language_requirements': Json({}),
        'curriculum_outline': Json({}),
        'internship_required': random.random() > 0.7 if program_template['program_type'] == 'technical' else False,
        'coop_available': random.random() > 0.6,
        'thesis_required': program_template['level'] in ['master', 'phd'],
        'career_outcomes': Json([f"{program_template['title']} Specialist", "Consultant", "Researcher"]),
        'employment_rate': employment_rate,
        'average_salary_range': Json({'min': 35000, 'max': 65000, 'currency': 'CAD'}),
        'top_employers': Json(["Government", "Private Sector", "Non-Profit"]),
        'tuition_domestic': tuition_domestic,
        'tuition_international': tuition_international,
        'fees_additional': Json({'registration': 100, 'technology': 50}),
        'financial_aid_available': True,
        'scholarships_available': Json(['Merit Scholarship', 'Need-based Aid']),
        'application_deadline': '2024-03-01',
        'application_method': 'Online',
        'application_fee': 85 if source_system == 'university' else 30,
        'application_requirements': Json(['Transcripts', 'Personal Statement']),
        'source_system': source_system,
        'source_id': source_id,
        'source_url': f"{institution['website']}/programs/{source_id}",
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'last_synced': datetime.now(),
        'active': True
    }
    
    return program_data

def populate_database():
    """Populate the database with realistic Quebec educational data"""
    
    # Database connection
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/orientor_dev')
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("🔗 Connected to database")
        
        # Step 1: Insert institutions
        print("🏫 Inserting institutions...")
        
        institution_data = []
        institution_ids = {}
        
        # Insert CEGEPs
        for cegep in QUEBEC_CEGEPS:
            institution_id = str(uuid.uuid4())
            institution_ids[cegep['name']] = institution_id
            
            institution_data.append((
                institution_id,
                cegep['name'],
                cegep.get('name_fr'),
                'cegep',
                'CA',
                'QC',
                cegep['city'],
                None,  # postal_code
                cegep.get('website'),
                'Accredited',  # accreditation_status
                random.randint(2000, 8000),  # student_count
                random.randint(1960, 1990),  # established_year
                ['en', 'fr'] if cegep.get('name_fr') else ['en'],  # languages_offered
                Json({}),  # contact_info
                None,  # geographic_coordinates
                'quebec_data',  # source_system
                cegep['name'].replace(' ', '_').lower(),  # source_id
                cegep.get('website'),  # source_url
                datetime.now(),  # created_at
                datetime.now(),  # updated_at
                datetime.now(),  # last_synced
                True  # active
            ))
        
        # Insert Universities
        for university in QUEBEC_UNIVERSITIES:
            institution_id = str(uuid.uuid4())
            institution_ids[university['name']] = institution_id
            
            institution_data.append((
                institution_id,
                university['name'],
                university.get('name_fr'),
                'university',
                'CA',
                'QC',
                university['city'],
                None,  # postal_code
                university.get('website'),
                'Accredited',  # accreditation_status
                random.randint(8000, 40000),  # student_count
                random.randint(1850, 1970),  # established_year
                ['en', 'fr'] if university.get('name_fr') else ['en'],  # languages_offered
                Json({}),  # contact_info
                None,  # geographic_coordinates
                'quebec_data',  # source_system
                university['name'].replace(' ', '_').lower(),  # source_id
                university.get('website'),  # source_url
                datetime.now(),  # created_at
                datetime.now(),  # updated_at
                datetime.now(),  # last_synced
                True  # active
            ))
        
        # Insert institutions
        execute_values(
            cursor,
            """
            INSERT INTO institutions (
                id, name, name_fr, institution_type, country, province_state, city,
                postal_code, website_url, accreditation_status, student_count, established_year,
                languages_offered, contact_info, geographic_coordinates, source_system, source_id,
                source_url, created_at, updated_at, last_synced, active
            ) VALUES %s
            """,
            institution_data,
            template=None,
            page_size=100
        )
        
        print(f"✅ Inserted {len(institution_data)} institutions")
        
        # Step 2: Insert programs
        print("📚 Generating and inserting programs...")
        
        program_data = []
        program_count = 0
        
        # Generate CEGEP programs
        for cegep in QUEBEC_CEGEPS:
            institution_id = institution_ids[cegep['name']]
            
            # Each CEGEP offers a subset of programs
            num_programs = random.randint(8, 15)
            selected_programs = random.sample(CEGEP_PROGRAMS, min(num_programs, len(CEGEP_PROGRAMS)))
            
            for program_template in selected_programs:
                program_info = generate_program_data(cegep, program_template, 'cegep')
                
                program_data.append((
                    str(uuid.uuid4()),  # id
                    program_info['title'],
                    program_info['title_fr'],
                    program_info['description'],
                    program_info['description_fr'],
                    institution_id,  # institution_id
                    program_info['program_type'],
                    program_info['level'],
                    program_info['field_of_study'],
                    program_info.get('field_of_study'),  # field_of_study_fr (using same for now)
                    program_info['duration_months'],
                    program_info['credits'],
                    None,  # semester_count
                    program_info['language'],
                    program_info['delivery_mode'],
                    program_info['cip_code'],
                    None,  # isced_code
                    None,  # noc_code
                    program_info['program_code'],
                    program_info['admission_requirements'],
                    program_info['prerequisite_courses'],
                    program_info['min_gpa'],
                    program_info['language_requirements'],
                    program_info['curriculum_outline'],
                    program_info['internship_required'],
                    program_info['coop_available'],
                    program_info['thesis_required'],
                    program_info['career_outcomes'],
                    program_info['employment_rate'],
                    program_info['average_salary_range'],
                    program_info['top_employers'],
                    program_info['tuition_domestic'],
                    program_info['tuition_international'],
                    program_info['fees_additional'],
                    program_info['financial_aid_available'],
                    program_info['scholarships_available'],
                    program_info['application_deadline'],
                    program_info['application_method'],
                    program_info['application_fee'],
                    program_info['application_requirements'],
                    program_info['source_system'],
                    program_info['source_id'],
                    program_info['source_url'],
                    program_info['created_at'],
                    program_info['updated_at'],
                    program_info['last_synced'],
                    program_info['active']
                ))
                program_count += 1
        
        # Generate University programs
        for university in QUEBEC_UNIVERSITIES:
            institution_id = institution_ids[university['name']]
            
            # Each university offers more programs
            num_programs = random.randint(15, 25)
            selected_programs = random.sample(UNIVERSITY_PROGRAMS, min(num_programs, len(UNIVERSITY_PROGRAMS)))
            
            for program_template in selected_programs:
                program_info = generate_program_data(university, program_template, 'university')
                
                program_data.append((
                    str(uuid.uuid4()),  # id
                    program_info['title'],
                    program_info['title_fr'],
                    program_info['description'],
                    program_info['description_fr'],
                    institution_id,  # institution_id
                    program_info['program_type'],
                    program_info['level'],
                    program_info['field_of_study'],
                    program_info.get('field_of_study'),  # field_of_study_fr
                    program_info['duration_months'],
                    program_info['credits'],
                    None,  # semester_count
                    program_info['language'],
                    program_info['delivery_mode'],
                    program_info['cip_code'],
                    None,  # isced_code
                    None,  # noc_code
                    program_info['program_code'],
                    program_info['admission_requirements'],
                    program_info['prerequisite_courses'],
                    program_info['min_gpa'],
                    program_info['language_requirements'],
                    program_info['curriculum_outline'],
                    program_info['internship_required'],
                    program_info['coop_available'],
                    program_info['thesis_required'],
                    program_info['career_outcomes'],
                    program_info['employment_rate'],
                    program_info['average_salary_range'],
                    program_info['top_employers'],
                    program_info['tuition_domestic'],
                    program_info['tuition_international'],
                    program_info['fees_additional'],
                    program_info['financial_aid_available'],
                    program_info['scholarships_available'],
                    program_info['application_deadline'],
                    program_info['application_method'],
                    program_info['application_fee'],
                    program_info['application_requirements'],
                    program_info['source_system'],
                    program_info['source_id'],
                    program_info['source_url'],
                    program_info['created_at'],
                    program_info['updated_at'],
                    program_info['last_synced'],
                    program_info['active']
                ))
                program_count += 1
        
        # Insert programs in batches
        batch_size = 100
        for i in range(0, len(program_data), batch_size):
            batch = program_data[i:i + batch_size]
            execute_values(
                cursor,
                """
                INSERT INTO programs (
                    id, title, title_fr, description, description_fr, institution_id,
                    program_type, level, field_of_study, field_of_study_fr, duration_months,
                    credits, semester_count, language, delivery_mode, cip_code, isced_code,
                    noc_code, program_code, admission_requirements, prerequisite_courses,
                    min_gpa, language_requirements, curriculum_outline, internship_required,
                    coop_available, thesis_required, career_outcomes, employment_rate,
                    average_salary_range, top_employers, tuition_domestic, tuition_international,
                    fees_additional, financial_aid_available, scholarships_available,
                    application_deadline, application_method, application_fee,
                    application_requirements, source_system, source_id, source_url,
                    created_at, updated_at, last_synced, active
                ) VALUES %s
                """,
                batch,
                template=None,
                page_size=100
            )
        
        print(f"✅ Inserted {program_count} programs")
        
        # Commit all changes
        conn.commit()
        
        # Verify the data
        cursor.execute("SELECT COUNT(*) FROM institutions")
        institution_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM programs")
        program_count_final = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM programs WHERE active = true")
        active_programs = cursor.fetchone()[0]
        
        print(f"\n📊 Database Population Results:")
        print(f"   🏫 Institutions: {institution_count}")
        print(f"   📚 Programs: {program_count_final}")
        print(f"   ✅ Active Programs: {active_programs}")
        
        # Show some sample data
        cursor.execute("""
            SELECT p.title, i.name as institution_name, p.level, p.program_type
            FROM programs p
            JOIN institutions i ON p.institution_id = i.id
            ORDER BY RANDOM()
            LIMIT 5
        """)
        
        print(f"\n🔍 Sample Programs:")
        for row in cursor.fetchall():
            print(f"   • {row[0]} at {row[1]} ({row[2]}, {row[3]})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 School programs database populated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        return False

if __name__ == "__main__":
    populate_database()