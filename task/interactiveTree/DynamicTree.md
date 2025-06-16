Enhance the competency tree with job saving functionality and complete career planning flow:

PRIORITY 1 - Fix tree generation:
- Debug the 404 error when generating trees from anchor skills
- Ensure API endpoint correctly receives 5 anchor skills and returns valid ESCO subgraph
- Add error handling and loading states

PRIORITY 2 - Tree persistence and job saving:
- Cache generated trees in user session/database
- Display existing tree when user revisits tab
- Add "Save Job" button on occupation nodes that saves to existing /space tab
- Implement job saving API endpoint that stores: job_title, esco_id, skills_required, discovery_source (anchor_skill_tree)

PRIORITY 3 - Interactive node functionality:
- Make skills/occupation nodes clickable
- Generate dynamic descriptions using LLM: "This skill/job relates to your profile because..."
- Display descriptions in modal/sidebar without disrupting tree layout
- Add "Save to Space" action button in job description modals

PRIORITY 4 - Enhanced /space tab integration:
- Display saved jobs from tree exploration in /space tab
- Add detailed job view with expanded LLM-generated descriptions
- Implement "Set as Career Goal" functionality for saved jobs
- Create career goal API endpoints: POST /career-goals, GET /career-goals/{user_id}

PRIORITY 5 - Educational pathway integration:
- When user sets career goal, trigger search for relevant CEGEP/university programs
- Display program recommendations with: program_name, institution, duration, admission_requirements
- Link to scraped CEGEP Quebec data for program details
- Add "Explore Programs" button that shows education-to-career pathway

PRIORITY 6 - Tree visualization improvements:
- Use React Flow with proper spacing (minimum 150px node separation)
- Color-code nodes by type (skills=blue, occupations=green, saved_jobs=gold)
- Implement force-directed layout to prevent edge overlapping
- Add visual indicators for already-saved jobs in tree

DATABASE ADDITIONS:
- saved_jobs table: user_id, job_title, esco_id, saved_from (tree/search), saved_at
- career_goals table: user_id, job_id, set_at, status (active/archived)
- program_recommendations table: goal_id, program_name, institution, match_score