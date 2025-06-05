-- Personality Assessment Session Management
CREATE TABLE personality_assessments (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  assessment_type VARCHAR(50) NOT NULL CHECK (assessment_type IN ('big_five', 'hexaco', 'social_emotional', 'cognitive_style', 'values')),
  assessment_version VARCHAR(20) NOT NULL, -- e.g., 'hexaco_60_en', 'hexaco_100_fr'
  session_id UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE,
  status VARCHAR(20) NOT NULL DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'abandoned')),
  started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  total_items INTEGER CHECK (total_items > 0),
  completed_items INTEGER DEFAULT 0,
  validity_flags JSONB DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Individual Assessment Responses
CREATE TABLE personality_responses (
  id SERIAL PRIMARY KEY,
  assessment_id INTEGER NOT NULL REFERENCES personality_assessments(id) ON DELETE CASCADE,
  item_id VARCHAR(100) NOT NULL,
  item_type VARCHAR(50) NOT NULL CHECK (item_type IN ('likert', 'scenario', 'ranking', 'open_ended')),
  response_value JSONB NOT NULL, -- e.g., {"value": 4}
  response_time_ms INTEGER CHECK (response_time_ms >= 0),
  revision_count INTEGER DEFAULT 0,
  confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 5),
  behavioral_metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
-- Computed Personality Profiles
CREATE TABLE personality_profiles (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  assessment_id INTEGER REFERENCES personality_assessments(id) ON DELETE SET NULL,
  profile_type VARCHAR(50) NOT NULL CHECK (profile_type IN ('big_five', 'hexaco', 'social_emotional', 'cognitive_style', 'values')),
  language VARCHAR(10) CHECK (language IN ('en', 'fr')),
  scores JSONB NOT NULL, -- {"Honesty-Humility": {"score": 3.9, "facets": {...}}, ...}
  confidence_intervals JSONB,
  reliability_estimates JSONB,
  percentile_ranks JSONB,
  narrative_description TEXT,
  assessment_version VARCHAR(20) NOT NULL,
  computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE (user_id, profile_type, assessment_version)
);
-- Personality Embeddings with Versioning
CREATE TABLE personality_embeddings (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  embedding_type VARCHAR(50) NOT NULL CHECK (embedding_type IN ('personality_384', 'big_five_384', 'hexaco_384', 'social_emotional_384')),
  embedding_vector FLOAT[] NOT NULL,
  generation_method VARCHAR(100) NOT NULL,
  model_version VARCHAR(50) NOT NULL,
  quality_score FLOAT CHECK (quality_score BETWEEN 0 AND 1),
  source_data_hash VARCHAR(64),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
-- Behavioral Signal Capture
CREATE TABLE behavioral_signals (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  signal_type VARCHAR(50) NOT NULL CHECK (signal_type IN ('response_timing', 'navigation_pattern', 'choice_pattern')),
  signal_data JSONB NOT NULL,
  confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
  context_metadata JSONB DEFAULT '{}',
  detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
-- Developmental Milestone Tracking
CREATE TABLE developmental_milestones (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  milestone_type VARCHAR(50) NOT NULL CHECK (milestone_type IN ('identity_exploration', 'value_clarification', 'commitment_formation')),
  milestone_description TEXT NOT NULL,
  achievement_date TIMESTAMP WITH TIME ZONE NOT NULL,
  confidence_level FLOAT CHECK (confidence_level BETWEEN 0 AND 1),
  supporting_evidence JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
-- Longitudinal Analysis Cache
CREATE TABLE personality_trends (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  trait_name VARCHAR(50) NOT NULL,
  trend_type VARCHAR(30) NOT NULL CHECK (trend_type IN ('linear', 'quadratic', 'change_point')),
  trend_parameters JSONB NOT NULL,
  trend_strength FLOAT,
  time_window_start TIMESTAMP WITH TIME ZONE NOT NULL,
  time_window_end TIMESTAMP WITH TIME ZONE NOT NULL,
  computed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
-- Create indexes for performance optimization
CREATE INDEX idx_assessments_user ON personality_assessments(user_id);
CREATE INDEX idx_assessments_session ON personality_assessments(session_id);

CREATE INDEX idx_responses_assessment ON personality_responses(assessment_id);

CREATE INDEX idx_profiles_user ON personality_profiles(user_id);
CREATE INDEX idx_profiles_type ON personality_profiles(profile_type);

CREATE INDEX idx_embeddings_user ON personality_embeddings(user_id);
CREATE INDEX idx_embeddings_type ON personality_embeddings(embedding_type);

CREATE INDEX idx_signals_user ON behavioral_signals(user_id);
CREATE INDEX idx_signals_type ON behavioral_signals(signal_type);

CREATE INDEX idx_milestones_user ON developmental_milestones(user_id);
CREATE INDEX idx_trends_user ON personality_trends(user_id);

ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS personality_embedding FLOAT[];
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS big_five_embedding FLOAT[];
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS social_emotional_embedding FLOAT[];
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS cognitive_style_embedding FLOAT[];
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS values_embedding FLOAT[];