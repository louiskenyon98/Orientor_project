# Interactive Tree Analysis - SPARC Phase 1: Specification

## Overview
Analysis of the competency tree enhancement requirements based on DynamicTree.md specifications. This document provides a comprehensive breakdown of the existing system and required enhancements.

## Current System Analysis

### Existing Implementation
- **Frontend**: React-based tree visualization using SVG and radial layout
- **Backend**: FastAPI with SQLAlchemy for tree data management
- **Database**: PostgreSQL with existing tree-related tables
- **Tree Generation**: Uses competence tree service with anchor skills
- **Visualization**: Custom SVG rendering with hierarchical layout

### Current Components
1. **CompetenceTreeView.tsx** - Main tree visualization component
2. **competenceTreeService.ts** - API service for tree operations
3. **tree_paths.py** - Backend router for tree path management
4. **TreePath model** - Database model for storing tree data

### Key Issues Identified
1. **404 Error**: Tree generation from anchor skills failing
2. **No Persistence**: Trees not cached properly in user sessions
3. **Limited Interactivity**: No job saving or detailed node interactions
4. **Missing Integration**: No connection to /space tab for saved jobs
5. **Static Visualization**: No dynamic descriptions or modal interactions

## Requirements Analysis by Priority

### PRIORITY 1: Fix Tree Generation
**Critical Issues:**
- Debug 404 error when generating trees from anchor skills
- API endpoint not correctly receiving 5 anchor skills
- Missing error handling and loading states

**Technical Requirements:**
- Fix API endpoint `/competence-tree/generate`
- Implement proper error handling for ESCO subgraph generation
- Add loading states for tree generation process
- Validate anchor skill input (exactly 5 skills required)

### PRIORITY 2: Tree Persistence and Job Saving
**Storage Requirements:**
- Cache generated trees in user session/database
- Display existing tree when user revisits tab
- Implement job saving functionality

**API Requirements:**
- Job saving endpoint: `POST /jobs/save`
- Job retrieval: `GET /jobs/user/{user_id}`
- Tree caching mechanism

**Database Schema Additions:**
```sql
-- New table for saved jobs
CREATE TABLE saved_jobs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  job_title VARCHAR NOT NULL,
  esco_id VARCHAR NOT NULL,
  skills_required JSONB,
  discovery_source VARCHAR DEFAULT 'anchor_skill_tree',
  saved_at TIMESTAMP DEFAULT NOW()
);
```

### PRIORITY 3: Interactive Node Functionality
**UI Requirements:**
- Clickable skills/occupation nodes
- Dynamic description generation using LLM
- Modal/sidebar display without disrupting tree layout
- "Save to Space" action buttons

**LLM Integration:**
- Generate contextual descriptions: "This skill/job relates to your profile because..."
- Use existing personality and skill profile data
- Implement caching for generated descriptions

### PRIORITY 4: Enhanced /space Tab Integration
**Features Required:**
- Display saved jobs from tree exploration
- Detailed job view with expanded descriptions
- "Set as Career Goal" functionality
- Career goal management

**API Endpoints:**
- `POST /career-goals` - Set career goal
- `GET /career-goals/{user_id}` - Get user career goals
- `PUT /career-goals/{goal_id}` - Update career goal
- `DELETE /career-goals/{goal_id}` - Remove career goal

### PRIORITY 5: Educational Pathway Integration
**Features:**
- Trigger CEGEP/university program search when career goal is set
- Display program recommendations with details
- Link to CEGEP Quebec data
- "Explore Programs" functionality

**Data Requirements:**
- Program name, institution, duration, admission requirements
- Match score algorithm for program relevance
- Integration with existing education data sources

### PRIORITY 6: Tree Visualization Improvements
**Technical Requirements:**
- Replace custom SVG with React Flow
- Implement proper node spacing (minimum 150px separation)
- Color-coded nodes by type (skills=blue, occupations=green, saved_jobs=gold)
- Force-directed layout to prevent edge overlapping
- Visual indicators for already-saved jobs

## Database Schema Requirements

### New Tables Needed:
1. **saved_jobs**: Store user-saved job opportunities
2. **career_goals**: Track user career goal selections
3. **program_recommendations**: Store education pathway suggestions

### Schema Definitions:
```sql
-- Saved jobs from tree exploration
CREATE TABLE saved_jobs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  job_title VARCHAR NOT NULL,
  esco_id VARCHAR UNIQUE NOT NULL,
  saved_from VARCHAR CHECK (saved_from IN ('tree', 'search')) DEFAULT 'tree',
  saved_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'
);

-- Career goals management
CREATE TABLE career_goals (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  job_id INTEGER REFERENCES saved_jobs(id),
  set_at TIMESTAMP DEFAULT NOW(),
  status VARCHAR CHECK (status IN ('active', 'archived')) DEFAULT 'active',
  notes TEXT
);

-- Program recommendations for career goals
CREATE TABLE program_recommendations (
  id SERIAL PRIMARY KEY,
  goal_id INTEGER REFERENCES career_goals(id),
  program_name VARCHAR NOT NULL,
  institution VARCHAR NOT NULL,
  match_score DECIMAL(3,2) CHECK (match_score >= 0 AND match_score <= 1),
  duration VARCHAR,
  admission_requirements TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Technical Architecture Requirements

### Frontend Components:
1. Enhanced CompetenceTreeView with React Flow
2. JobNodeModal for detailed job descriptions
3. SpaceTabIntegration for saved jobs display
4. ProgramRecommendations component
5. CareerGoalManager component

### Backend Services:
1. JobSavingService for managing saved opportunities
2. CareerGoalService for goal management
3. EducationPathwayService for program recommendations
4. LLMDescriptionService for dynamic content generation
5. ESCOTreeService (enhanced) for improved tree generation

### API Endpoints Required:
- `POST /trees/generate-from-anchors` - Fixed tree generation
- `POST /jobs/save` - Save job from tree
- `GET /jobs/saved/{user_id}` - Get saved jobs
- `POST /career-goals` - Set career goal
- `GET /career-goals/{user_id}` - Get career goals
- `GET /programs/recommend/{goal_id}` - Get program recommendations
- `POST /descriptions/generate` - Generate LLM descriptions

## Success Criteria
1. Tree generation from anchor skills works without 404 errors
2. Trees persist across user sessions
3. Users can save jobs directly from tree nodes
4. Saved jobs appear in /space tab with full details
5. Career goals can be set and managed
6. Educational pathways are recommended based on career goals
7. Tree visualization uses React Flow with proper spacing and colors
8. All interactions are smooth and responsive

## Risk Assessment
- **High Risk**: API integration with ESCO data sources
- **Medium Risk**: React Flow integration complexity
- **Low Risk**: Database schema changes and basic CRUD operations

## Estimated Timeline
- **Priority 1-2**: 2-3 days (Critical path)
- **Priority 3-4**: 3-4 days (Major features)
- **Priority 5-6**: 2-3 days (Enhancements)
- **Total**: 7-10 days for complete implementation

## Next Steps
Proceed to SPARC Phase 2: Architecture design based on this analysis.