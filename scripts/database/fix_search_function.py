#!/usr/bin/env python3
"""
Fix the search function array operator issue
"""
import os
import psycopg2

def fix_search_function():
    """Fix the search function to handle array operations correctly"""
    
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/orientor_dev')
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("🔧 Fixing search function array operator...")
        
        # Drop existing function
        cursor.execute("DROP FUNCTION IF EXISTS search_programs(text,text[],text[],text[],text[],text[],integer,numeric,integer,integer)")
        
        # Create corrected search function
        search_function_sql = """
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
                p.title::TEXT,
                i.name::TEXT as institution_name,
                i.city::TEXT,
                i.province_state::TEXT,
                p.program_type::TEXT,
                p.level::TEXT,
                p.duration_months,
                p.employment_rate,
                CASE 
                    WHEN search_text = '' THEN 1.0::REAL
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
                AND (array_length(languages, 1) IS NULL OR (p.language::TEXT[] && languages))
                AND (max_duration IS NULL OR p.duration_months <= max_duration)
                AND (min_employment_rate IS NULL OR p.employment_rate >= min_employment_rate)
            ORDER BY search_rank DESC, p.title
            LIMIT limit_count OFFSET offset_count;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        cursor.execute(search_function_sql)
        conn.commit()
        
        print("✅ Search function updated successfully!")
        
        # Test the function
        cursor.execute("""
            SELECT COUNT(*) FROM search_programs(
                '', ARRAY[]::TEXT[], ARRAY[]::TEXT[], ARRAY[]::TEXT[], ARRAY[]::TEXT[], 
                ARRAY[]::TEXT[], NULL, NULL, 10, 0
            )
        """)
        
        count = cursor.fetchone()[0]
        print(f"🔍 Search test: {count} total programs found")
        
        # Test search with keyword
        cursor.execute("""
            SELECT title, institution_name FROM search_programs(
                'computer', ARRAY[]::TEXT[], ARRAY[]::TEXT[], ARRAY[]::TEXT[], ARRAY[]::TEXT[], 
                ARRAY[]::TEXT[], NULL, NULL, 5, 0
            )
        """)
        
        results = cursor.fetchall()
        print(f"💻 'Computer' search: {len(results)} programs found")
        for title, institution in results[:3]:
            print(f"   • {title} at {institution}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Search function is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing search function: {e}")
        return False

if __name__ == "__main__":
    fix_search_function()