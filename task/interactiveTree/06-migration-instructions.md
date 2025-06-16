# Database Migration Instructions

## Overview
This document explains how to run the database migrations for the interactive tree enhancements.

## Prerequisites
- Ensure you have database backup before running migrations
- Alembic must be installed (`pip install alembic`)
- Database connection configured in backend/.env

## Migration Files Created
1. `add_interactive_tree_tables.py` - Creates new tables for:
   - `saved_jobs` - Store jobs saved from tree exploration
   - `career_goals` - Track user career objectives
   - `program_recommendations` - Educational pathway suggestions
   - `llm_descriptions` - Cache for generated node descriptions
   - `tree_generations` - Enhanced tree caching

## Running the Migration

### Step 1: Navigate to backend directory
```bash
cd backend
```

### Step 2: Check current migration status
```bash
alembic current
```

### Step 3: Review the migration
```bash
alembic show add_interactive_tree_tables
```

### Step 4: Run the migration
```bash
alembic upgrade add_interactive_tree_tables
```

### Step 5: Verify migration success
```bash
alembic current
```

## Rollback Instructions
If you need to rollback the migration:
```bash
alembic downgrade -1
```

## Database Schema Changes

### New Tables Created:

#### 1. saved_jobs
- Stores jobs saved from tree exploration
- Links to user and includes ESCO job ID
- Tracks discovery source (tree, search, etc.)
- Includes relevance score and metadata

#### 2. career_goals
- Manages user career objectives
- Links to saved jobs
- Tracks status (active, archived, achieved, paused)
- Supports goal history tracking

#### 3. program_recommendations
- Educational program suggestions
- Links to career goals
- Includes match scores and program details
- Stores location and intake information

#### 4. llm_descriptions
- Caches LLM-generated node descriptions
- User-specific descriptions
- Includes expiration for cache management
- Indexed for fast retrieval

#### 5. tree_generations
- Enhanced tree caching system
- Stores complete tree data with anchor skills
- Tracks access patterns
- Supports expiration for cache management

## Testing the Migration

After running the migration, verify tables exist:
```sql
-- Check if tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('saved_jobs', 'career_goals', 'program_recommendations', 'llm_descriptions', 'tree_generations');

-- Check indexes
SELECT indexname 
FROM pg_indexes 
WHERE tablename IN ('saved_jobs', 'career_goals', 'program_recommendations', 'llm_descriptions', 'tree_generations');
```

## Next Steps
After migration is complete:
1. Implement backend services for job saving
2. Create API endpoints for career goals
3. Build frontend components for tree interactions
4. Test end-to-end functionality