-- Create saved_jobs table for storing jobs from tree exploration
CREATE TABLE IF NOT EXISTS saved_jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    esco_id VARCHAR(255) NOT NULL,
    job_title VARCHAR(500) NOT NULL,
    skills_required JSONB,
    discovery_source VARCHAR(50) DEFAULT 'tree',
    tree_graph_id UUID,
    relevance_score NUMERIC(3,2),
    saved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    CONSTRAINT uq_user_job UNIQUE(user_id, esco_id)
);

CREATE INDEX IF NOT EXISTS ix_saved_jobs_user_id ON saved_jobs(user_id);
CREATE INDEX IF NOT EXISTS ix_saved_jobs_esco_id ON saved_jobs(esco_id);
CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_source ON saved_jobs(user_id, discovery_source);

-- Create career_goals table for managing user career objectives
CREATE TABLE IF NOT EXISTS career_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    job_id INTEGER NOT NULL REFERENCES saved_jobs(id),
    set_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    previous_goal_id INTEGER REFERENCES career_goals(id),
    notes TEXT,
    target_date DATE,
    progress_metrics JSONB DEFAULT '{}',
    CONSTRAINT check_goal_status CHECK(status IN ('active', 'archived', 'achieved', 'paused'))
);

CREATE INDEX IF NOT EXISTS ix_career_goals_user_id ON career_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_career_goals_user_status ON career_goals(user_id, status);

-- Create program_recommendations table for educational pathways
CREATE TABLE IF NOT EXISTS program_recommendations (
    id SERIAL PRIMARY KEY,
    goal_id INTEGER NOT NULL REFERENCES career_goals(id),
    program_name VARCHAR(500) NOT NULL,
    institution VARCHAR(500) NOT NULL,
    institution_type VARCHAR(50),
    program_code VARCHAR(100),
    duration VARCHAR(100),
    admission_requirements JSONB,
    match_score NUMERIC(3,2),
    cost_estimate NUMERIC(10,2),
    location JSONB,
    intake_dates JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_match_score_range CHECK(match_score >= 0 AND match_score <= 1)
);

CREATE INDEX IF NOT EXISTS ix_program_recommendations_goal_id ON program_recommendations(goal_id);

-- Create llm_descriptions table for caching generated descriptions
CREATE TABLE IF NOT EXISTS llm_descriptions (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    node_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    prompt_template VARCHAR(100),
    model_version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT check_node_type CHECK(node_type IN ('skill', 'occupation', 'skillgroup')),
    CONSTRAINT uq_node_user_description UNIQUE(node_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_llm_descriptions_node_user ON llm_descriptions(node_id, user_id);

-- Create tree_generations table for enhanced tree caching
CREATE TABLE IF NOT EXISTS tree_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id),
    anchor_skills JSONB NOT NULL,
    graph_data JSONB NOT NULL,
    generation_options JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_tree_generations_user_created ON tree_generations(user_id, created_at);