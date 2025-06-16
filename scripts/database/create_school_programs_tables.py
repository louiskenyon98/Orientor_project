#!/usr/bin/env python3
"""
Script to create school programs database tables
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_school_programs_tables():
    """Create school programs tables in the database"""
    
    # Database connection
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/orientor_dev')
    
    try:
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔗 Connected to database")
        
        # Enable extensions
        print("📝 Enabling PostgreSQL extensions...")
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
        
        # Create institutions table
        print("🏫 Creating institutions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS institutions (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name VARCHAR(255) NOT NULL,
                name_fr VARCHAR(255),
                institution_type VARCHAR(50) NOT NULL CHECK (institution_type IN ('cegep', 'university', 'college')),
                country VARCHAR(2) NOT NULL DEFAULT 'CA',
                province_state VARCHAR(50),
                city VARCHAR(100),
                postal_code VARCHAR(20),
                website_url TEXT,
                accreditation_status VARCHAR(100),
                student_count INTEGER,
                established_year INTEGER,
                languages_offered VARCHAR(10)[] DEFAULT ARRAY['en'],
                contact_info JSONB DEFAULT '{}',
                geographic_coordinates POINT,
                
                -- Source tracking
                source_system VARCHAR(50) NOT NULL,
                source_id VARCHAR(100) NOT NULL,
                source_url TEXT,
                
                -- Metadata
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_synced TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                active BOOLEAN DEFAULT true,
                
                -- Constraints
                UNIQUE(source_system, source_id)
            )
        """)
        
        # Create programs table
        print("📚 Creating programs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS programs (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                title VARCHAR(255) NOT NULL,
                title_fr VARCHAR(255),
                description TEXT,
                description_fr TEXT,
                
                -- Institution reference
                institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
                
                -- Program classification
                program_type VARCHAR(50) NOT NULL,
                level VARCHAR(50) NOT NULL CHECK (level IN ('certificate', 'diploma', 'associate', 'bachelor', 'master', 'phd', 'professional')),
                field_of_study VARCHAR(100),
                field_of_study_fr VARCHAR(100),
                
                -- Program details
                duration_months INTEGER,
                credits DECIMAL(5,2),
                semester_count INTEGER,
                language VARCHAR(10)[] DEFAULT ARRAY['en'],
                delivery_mode VARCHAR(50) DEFAULT 'in-person',
                
                -- Classification codes
                cip_code VARCHAR(10),
                isced_code VARCHAR(10),
                noc_code VARCHAR(10),
                program_code VARCHAR(20),
                
                -- Academic requirements
                admission_requirements JSONB DEFAULT '[]',
                prerequisite_courses JSONB DEFAULT '[]',
                min_gpa DECIMAL(3,2),
                language_requirements JSONB DEFAULT '{}',
                
                -- Program structure
                curriculum_outline JSONB DEFAULT '{}',
                internship_required BOOLEAN DEFAULT false,
                coop_available BOOLEAN DEFAULT false,
                thesis_required BOOLEAN DEFAULT false,
                
                -- Career outcomes
                career_outcomes JSONB DEFAULT '[]',
                employment_rate DECIMAL(3,2),
                average_salary_range JSONB DEFAULT '{}',
                top_employers JSONB DEFAULT '[]',
                
                -- Financial information
                tuition_domestic DECIMAL(10,2),
                tuition_international DECIMAL(10,2),
                fees_additional JSONB DEFAULT '{}',
                financial_aid_available BOOLEAN DEFAULT false,
                scholarships_available JSONB DEFAULT '[]',
                
                -- Application information
                application_deadline DATE,
                application_method VARCHAR(100),
                application_fee DECIMAL(8,2),
                application_requirements JSONB DEFAULT '[]',
                
                -- Source tracking
                source_system VARCHAR(50) NOT NULL,
                source_id VARCHAR(100) NOT NULL,
                source_url TEXT,
                
                -- Metadata
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_synced TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                active BOOLEAN DEFAULT true,
                
                -- Constraints
                UNIQUE(source_system, source_id),
                CHECK (duration_months > 0),
                CHECK (employment_rate >= 0 AND employment_rate <= 1)
            )
        """)
        
        # Add search vector column
        print("🔍 Adding search vector column...")
        cursor.execute("""
            ALTER TABLE programs ADD COLUMN IF NOT EXISTS search_vector tsvector 
            GENERATED ALWAYS AS (
                setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(description, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(field_of_study, '')), 'C')
            ) STORED
        """)
        
        # Create user preferences table
        print("👤 Creating user program preferences table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_program_preferences (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                
                -- Location preferences
                preferred_countries VARCHAR(2)[] DEFAULT ARRAY['CA'],
                preferred_provinces VARCHAR(50)[] DEFAULT ARRAY[]::VARCHAR[],
                preferred_cities VARCHAR(100)[] DEFAULT ARRAY[]::VARCHAR[],
                max_distance_km INTEGER,
                willing_to_relocate BOOLEAN DEFAULT false,
                
                -- Program preferences
                preferred_languages VARCHAR(10)[] DEFAULT ARRAY['en'],
                program_types VARCHAR(50)[] DEFAULT ARRAY[]::VARCHAR[],
                program_levels VARCHAR(50)[] DEFAULT ARRAY[]::VARCHAR[],
                fields_of_interest VARCHAR(100)[] DEFAULT ARRAY[]::VARCHAR[],
                delivery_modes VARCHAR(50)[] DEFAULT ARRAY['in-person'],
                
                -- Duration and timing
                max_duration_months INTEGER,
                min_duration_months INTEGER,
                preferred_start_terms VARCHAR(20)[] DEFAULT ARRAY['fall'],
                part_time_acceptable BOOLEAN DEFAULT false,
                
                -- Financial constraints
                max_budget DECIMAL(10,2),
                budget_currency VARCHAR(3) DEFAULT 'CAD',
                financial_aid_required BOOLEAN DEFAULT false,
                scholarship_priority BOOLEAN DEFAULT false,
                
                -- Academic preferences
                min_employment_rate DECIMAL(3,2),
                internship_preference VARCHAR(20) DEFAULT 'optional',
                coop_preference VARCHAR(20) DEFAULT 'optional',
                
                -- Career alignment
                target_career_fields VARCHAR(100)[] DEFAULT ARRAY[]::VARCHAR[],
                salary_expectations JSONB DEFAULT '{}',
                work_environment_preferences JSONB DEFAULT '{}',
                
                -- Metadata
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                UNIQUE(user_id)
            )
        """)
        
        # Create indexes
        print("📊 Creating database indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_institutions_type ON institutions(institution_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_institutions_location ON institutions(country, province_state, city)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_institutions_active ON institutions(active) WHERE active = true")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_institutions_source ON institutions(source_system, source_id)")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_programs_institution ON programs(institution_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_programs_type_level ON programs(program_type, level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_programs_cip ON programs(cip_code) WHERE cip_code IS NOT NULL")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_programs_active ON programs(active) WHERE active = true")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_programs_source ON programs(source_system, source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_programs_search ON programs USING gin(search_vector)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_programs_title_trgm ON programs USING gin(title gin_trgm_ops)")
        
        # Create search function
        print("🔍 Creating search function...")
        cursor.execute("""
        CREATE OR REPLACE FUNCTION search_programs(
            search_text TEXT DEFAULT '',
            program_types TEXT[] DEFAULT ARRAY[]::TEXT[],
            levels TEXT[] DEFAULT ARRAY[]::TEXT[],
            countries TEXT[] DEFAULT ARRAY[]::TEXT[],
            provinces TEXT[] DEFAULT ARRAY[]::TEXT[],
            languages TEXT[] DEFAULT ARRAY[]::TEXT[],
            max_duration INTEGER DEFAULT NULL,
            min_employment_rate DECIMAL DEFAULT NULL,
            limit_count INTEGER DEFAULT 20,
            offset_count INTEGER DEFAULT 0
        )
        RETURNS TABLE (
            id UUID,
            title TEXT,
            institution_name TEXT,
            city TEXT,
            province_state TEXT,
            program_type TEXT,
            level TEXT,
            duration_months INTEGER,
            employment_rate DECIMAL,
            search_rank REAL
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                p.id,
                p.title,
                i.name as institution_name,
                i.city,
                i.province_state,
                p.program_type,
                p.level,
                p.duration_months,
                p.employment_rate,
                CASE 
                    WHEN search_text = '' THEN 1.0
                    ELSE ts_rank(p.search_vector, plainto_tsquery('english', search_text))
                END as search_rank
            FROM programs p
            JOIN institutions i ON p.institution_id = i.id
            WHERE 
                p.active = true AND i.active = true
                AND (search_text = '' OR p.search_vector @@ plainto_tsquery('english', search_text))
                AND (array_length(program_types, 1) IS NULL OR p.program_type = ANY(program_types))
                AND (array_length(levels, 1) IS NULL OR p.level = ANY(levels))
                AND (array_length(countries, 1) IS NULL OR i.country = ANY(countries))
                AND (array_length(provinces, 1) IS NULL OR i.province_state = ANY(provinces))
                AND (array_length(languages, 1) IS NULL OR p.language && languages)
                AND (max_duration IS NULL OR p.duration_months <= max_duration)
                AND (min_employment_rate IS NULL OR p.employment_rate >= min_employment_rate)
            ORDER BY search_rank DESC, p.title
            LIMIT limit_count OFFSET offset_count;
        END;
        $$ LANGUAGE plpgsql;
        """)
        
        # Create update trigger function
        print("⏱️ Creating update triggers...")
        cursor.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """)
        
        # Create triggers
        cursor.execute("DROP TRIGGER IF EXISTS update_institutions_updated_at ON institutions")
        cursor.execute("CREATE TRIGGER update_institutions_updated_at BEFORE UPDATE ON institutions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")
        
        cursor.execute("DROP TRIGGER IF EXISTS update_programs_updated_at ON programs")
        cursor.execute("CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")
        
        cursor.execute("DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_program_preferences")
        cursor.execute("CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_program_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")
        
        # Verify creation
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('institutions', 'programs', 'user_program_preferences')
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Created tables: {', '.join(tables)}")
        
        cursor.close()
        conn.close()
        
        print("🎉 School programs database schema created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating school programs tables: {e}")
        return False

if __name__ == "__main__":
    create_school_programs_tables()