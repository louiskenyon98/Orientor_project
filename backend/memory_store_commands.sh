#!/bin/bash
# Commands to store Orientator AI database components in Memory

# Store MessageComponent model
/Users/philippebeliveau/.npm/_npx/314032b4cf2cd736/node_modules/.bin/claude-flow memory store "swarm-auto-centralized-1750807806052/db-architect/message_component_model" "$(cat /Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/backend/app/models/message_component.py)"

# Store ToolInvocation model
/Users/philippebeliveau/.npm/_npx/314032b4cf2cd736/node_modules/.bin/claude-flow memory store "swarm-auto-centralized-1750807806052/db-architect/tool_invocation_model" "$(cat /Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/backend/app/models/tool_invocation.py)"

# Store UserJourneyMilestone model
/Users/philippebeliveau/.npm/_npx/314032b4cf2cd736/node_modules/.bin/claude-flow memory store "swarm-auto-centralized-1750807806052/db-architect/user_journey_milestone_model" "$(cat /Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/backend/app/models/user_journey_milestone.py)"

# Store updated SavedRecommendation model
/Users/philippebeliveau/.npm/_npx/314032b4cf2cd736/node_modules/.bin/claude-flow memory store "swarm-auto-centralized-1750807806052/db-architect/saved_recommendation_updates" "$(grep -A 20 'Orientator AI integration fields' /Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/backend/app/models/saved_recommendation.py)"

# Store Alembic migration
/Users/philippebeliveau/.npm/_npx/314032b4cf2cd736/node_modules/.bin/claude-flow memory store "swarm-auto-centralized-1750807806052/db-architect/alembic_migration" "$(cat /Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/backend/alembic/versions/2025_06_24_202407_add_orientator_ai_tables.py)"

# Store unit tests
/Users/philippebeliveau/.npm/_npx/314032b4cf2cd736/node_modules/.bin/claude-flow memory store "swarm-auto-centralized-1750807806052/db-architect/unit_tests" "$(cat /Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/backend/tests/test_orientator_models.py)"

# Store database schema documentation
/Users/philippebeliveau/.npm/_npx/314032b4cf2cd736/node_modules/.bin/claude-flow memory store "swarm-auto-centralized-1750807806052/db-architect/schema_documentation" "$(cat /Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/backend/docs/orientator_database_schema.md)"

echo "All Orientator AI database components have been stored in Memory"