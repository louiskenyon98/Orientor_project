-- Career Fit Analyzer Schema Updates
-- These updates enhance user_profiles to enable symmetric career fit comparisons

-- Add Academic Requirements Fields
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS completed_courses TEXT[], -- Array of completed course codes/names
ADD COLUMN IF NOT EXISTS certifications JSONB DEFAULT '[]', -- [{name, issuer, date, expiry}]
ADD COLUMN IF NOT EXISTS portfolio_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS research_experience BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS internship_experience JSONB DEFAULT '[]'; -- [{company, role, duration, industry}]

-- Add Financial Planning Fields
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS expected_graduation_date DATE,
ADD COLUMN IF NOT EXISTS current_debt DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS financial_support JSONB DEFAULT '{}', -- {scholarships: [], family_support: amount, loans: []}
ADD COLUMN IF NOT EXISTS minimum_salary_requirement DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS relocation_willingness BOOLEAN DEFAULT false;

-- Add Timeline & Commitment Fields
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS available_study_years INTEGER DEFAULT 4, -- How many years they can dedicate to study
ADD COLUMN IF NOT EXISTS part_time_work_needed BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS family_obligations JSONB DEFAULT '{}', -- {dependents: 0, care_responsibilities: []}
ADD COLUMN IF NOT EXISTS career_urgency INTEGER CHECK (career_urgency BETWEEN 1 AND 5); -- 1=relaxed, 5=urgent need for income

-- Add Skills Gap Analysis Fields
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS skill_learning_rate JSONB DEFAULT '{}', -- {skill_name: rate_1_to_5}
ADD COLUMN IF NOT EXISTS preferred_learning_methods TEXT[] DEFAULT ARRAY['online', 'classroom'], 
ADD COLUMN IF NOT EXISTS skill_confidence_levels JSONB DEFAULT '{}'; -- {skill_name: confidence_1_to_5}

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_education_level ON user_profiles(education_level);
CREATE INDEX IF NOT EXISTS idx_user_profiles_gpa ON user_profiles(gpa) WHERE gpa IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_profiles_career_urgency ON user_profiles(career_urgency) WHERE career_urgency IS NOT NULL;

-- Create ESCO job requirements table for better field mapping
CREATE TABLE IF NOT EXISTS esco_job_requirements (
    id SERIAL PRIMARY KEY,
    oasis_code VARCHAR(255) UNIQUE NOT NULL,
    
    -- Entry Conditions
    entry_level_education VARCHAR(100), -- 'high_school', 'bachelor', 'master', 'phd'
    entry_experience_years INTEGER DEFAULT 0,
    entry_certifications JSONB DEFAULT '[]',
    entry_portfolio_required BOOLEAN DEFAULT false,
    
    -- Education Pathways
    typical_education_level VARCHAR(100),
    alternative_pathways JSONB DEFAULT '[]', -- Array of alternative routes
    continuing_education TEXT,
    specialization_options JSONB DEFAULT '[]',
    
    -- Skills Taxonomy
    essential_skills JSONB DEFAULT '[]', -- Array of must-have skills
    optional_skills JSONB DEFAULT '[]', -- Array of nice-to-have skills
    transferable_skills JSONB DEFAULT '[]', -- Skills from other fields that apply
    emerging_skills JSONB DEFAULT '[]', -- Future-relevant skills
    
    -- Career Trajectory
    entry_level_titles JSONB DEFAULT '[]',
    mid_career_titles JSONB DEFAULT '[]', -- 5-10 year positions
    senior_titles JSONB DEFAULT '[]', -- Leadership roles
    lateral_moves JSONB DEFAULT '[]', -- Related career pivots
    
    -- Industry Context
    sector_classification VARCHAR(100),
    isco_code VARCHAR(10),
    growth_rate DECIMAL(5,2), -- Percentage growth rate
    automation_risk DECIMAL(3,2), -- 0-1 probability
    remote_work_percentage DECIMAL(3,2), -- 0-1 percentage
    
    -- Time and Cost Estimates
    typical_years_to_entry INTEGER, -- Years from start of education to first job
    education_cost_estimate DECIMAL(10,2), -- Total education cost
    average_starting_salary DECIMAL(10,2),
    salary_growth_curve JSONB, -- {years: salary} mapping
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for ESCO requirements
CREATE INDEX IF NOT EXISTS idx_esco_requirements_code ON esco_job_requirements(oasis_code);
CREATE INDEX IF NOT EXISTS idx_esco_requirements_education ON esco_job_requirements(entry_level_education);
CREATE INDEX IF NOT EXISTS idx_esco_requirements_sector ON esco_job_requirements(sector_classification);

-- Add missing fields to saved_recommendations for better analysis
ALTER TABLE saved_recommendations
ADD COLUMN IF NOT EXISTS source_type VARCHAR(20) DEFAULT 'esco', -- 'esco' or 'oasis'
ADD COLUMN IF NOT EXISTS graphsage_top_skills JSONB, -- For OaSIS jobs: [{skill: name, relevance: score}]
ADD COLUMN IF NOT EXISTS feasibility_analysis JSONB, -- LLM-generated feasibility assessment
ADD COLUMN IF NOT EXISTS time_to_qualification INTEGER, -- Estimated months to qualify
ADD COLUMN IF NOT EXISTS education_required VARCHAR(100), -- Simplified education requirement
ADD COLUMN IF NOT EXISTS match_score DECIMAL(3,2); -- Overall match percentage 0-1

-- Create career fit analysis results table
CREATE TABLE IF NOT EXISTS career_fit_analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    saved_recommendation_id INTEGER REFERENCES saved_recommendations(id) ON DELETE CASCADE,
    
    -- Fit Scores
    skill_match_score DECIMAL(3,2), -- 0-1
    education_match_score DECIMAL(3,2), -- 0-1
    experience_match_score DECIMAL(3,2), -- 0-1
    personality_match_score DECIMAL(3,2), -- 0-1
    overall_fit_score DECIMAL(3,2), -- 0-1
    
    -- Gap Analysis
    skill_gaps JSONB DEFAULT '[]', -- [{skill: name, current: level, required: level, gap: difference}]
    education_gap TEXT,
    experience_gap_years INTEGER,
    certification_gaps JSONB DEFAULT '[]',
    
    -- Timeline Analysis
    estimated_preparation_months INTEGER,
    recommended_pathway TEXT,
    milestone_timeline JSONB DEFAULT '[]', -- [{milestone: text, months: number}]
    
    -- Financial Analysis
    total_education_cost DECIMAL(10,2),
    opportunity_cost DECIMAL(10,2), -- Lost income during education
    break_even_years DECIMAL(3,1), -- Years to recover investment
    roi_10_year DECIMAL(10,2), -- 10-year return on investment
    
    -- LLM Insights
    barriers_analysis TEXT,
    strengths_alignment TEXT,
    recommendation_rationale TEXT,
    alternative_paths TEXT,
    
    -- Metadata
    analysis_version VARCHAR(20) DEFAULT '1.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, saved_recommendation_id)
);

-- Create indexes for career fit analyses
CREATE INDEX IF NOT EXISTS idx_fit_analyses_user ON career_fit_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_fit_analyses_recommendation ON career_fit_analyses(saved_recommendation_id);
CREATE INDEX IF NOT EXISTS idx_fit_analyses_scores ON career_fit_analyses(overall_fit_score DESC);

-- Create function to calculate skill match score
CREATE OR REPLACE FUNCTION calculate_skill_match_score(
    user_skills JSONB,
    role_skills JSONB
) RETURNS DECIMAL AS $$
DECLARE
    match_score DECIMAL := 0;
    skill_count INTEGER := 0;
    user_level DECIMAL;
    role_level DECIMAL;
    skill_name TEXT;
BEGIN
    -- Compare each skill
    FOR skill_name IN SELECT jsonb_object_keys(role_skills)
    LOOP
        role_level := (role_skills->>skill_name)::DECIMAL;
        user_level := COALESCE((user_skills->>skill_name)::DECIMAL, 0);
        
        -- Calculate match (penalize gaps more than surplus)
        IF user_level >= role_level THEN
            match_score := match_score + 1;
        ELSE
            match_score := match_score + (user_level / NULLIF(role_level, 0));
        END IF;
        
        skill_count := skill_count + 1;
    END LOOP;
    
    -- Return average match score
    RETURN CASE 
        WHEN skill_count > 0 THEN match_score / skill_count
        ELSE 0
    END;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_esco_requirements_updated_at BEFORE UPDATE
    ON esco_job_requirements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_career_fit_analyses_updated_at BEFORE UPDATE
    ON career_fit_analyses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE esco_job_requirements IS 'Extended ESCO job requirements for career fit analysis';
COMMENT ON TABLE career_fit_analyses IS 'Detailed career fit analysis results comparing users to saved jobs';
COMMENT ON COLUMN saved_recommendations.source_type IS 'Job data source: esco or oasis';
COMMENT ON COLUMN saved_recommendations.graphsage_top_skills IS 'Top skills extracted via GraphSAGE for OaSIS jobs';
COMMENT ON COLUMN user_profiles.career_urgency IS 'How urgently user needs income: 1=relaxed, 5=urgent';
COMMENT ON COLUMN user_profiles.skill_learning_rate IS 'Self-assessed learning speed per skill (1-5 scale)';