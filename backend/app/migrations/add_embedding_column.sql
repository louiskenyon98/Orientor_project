-- Add embedding column to user_profiles table
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS embedding VECTOR(384);

-- Create an index on the embedding column for faster similarity searches
CREATE INDEX IF NOT EXISTS idx_user_profiles_embedding ON user_profiles USING ivfflat (embedding vector_cosine_ops);

-- Add indexing for recommendations
-- Add table to track user recommendations that were swiped
CREATE TABLE IF NOT EXISTS user_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    oasis_code VARCHAR NOT NULL,
    label VARCHAR NOT NULL,
    swiped_right BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, oasis_code)
);

-- Add index for faster lookup
CREATE INDEX IF NOT EXISTS idx_user_recommendations_user_id ON user_recommendations(user_id); 