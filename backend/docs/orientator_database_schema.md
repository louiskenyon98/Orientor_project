# Orientator AI Database Schema Documentation

## Overview
This document describes the database schema additions for the Orientator AI feature, which introduces conversational AI capabilities with autonomous tool invocation and persistent career journey building.

## New Tables

### 1. message_components
Stores rich interactive components associated with chat messages. These components represent tool outputs that can be rendered in the UI.

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Unique identifier
- `message_id` (INTEGER, FOREIGN KEY): References chat_messages.id
- `component_type` (VARCHAR(50)): Type of component (skill_tree, career_path, job_card, etc.)
- `component_data` (JSONB): Component-specific data structure
- `tool_source` (VARCHAR(50)): Name of the tool that generated this component
- `created_at` (TIMESTAMP): When the component was created
- `actions` (JSONB): Available user actions for this component
- `saved` (JSONB): Whether the component has been saved
- `metadata` (JSONB): Additional metadata for rendering

**Indexes:**
- Primary key on `id`
- Foreign key index on `message_id`
- Index on `component_type` for filtering by type
- Index on `tool_source` for analytics
- Index on `created_at` for time-based queries
- GIN index on `component_data` for JSONB search

**Relationships:**
- Many-to-One with `chat_messages` (cascade delete)

### 2. tool_invocations
Tracks all tool invocations made by the Orientator AI during conversations. Essential for analytics, debugging, and understanding AI behavior.

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Unique identifier
- `conversation_id` (INTEGER, FOREIGN KEY): References conversations.id
- `tool_name` (VARCHAR(50)): Name of the invoked tool
- `input_params` (JSONB): Parameters passed to the tool
- `output_data` (JSONB): Data returned by the tool
- `execution_time_ms` (INTEGER): Tool execution time in milliseconds
- `success` (VARCHAR(20)): Status (success, failed, timeout)
- `error_message` (VARCHAR(500)): Error details if failed
- `relevance_score` (FLOAT): AI confidence in tool choice (0-1)
- `user_id` (INTEGER, FOREIGN KEY): References users.id
- `created_at` (TIMESTAMP): When the invocation occurred

**Indexes:**
- Primary key on `id`
- Foreign key indexes on `conversation_id` and `user_id`
- Index on `tool_name` for tool usage analytics
- Index on `execution_time_ms` for performance monitoring
- Index on `created_at` for time-based queries
- Composite index on `(conversation_id, tool_name)`
- Composite index on `(user_id, tool_name)`
- GIN index on `input_params` for parameter search

**Relationships:**
- Many-to-One with `conversations` (cascade delete)
- Many-to-One with `users`

### 3. user_journey_milestones
Tracks significant milestones in a user's career exploration journey. These milestones are automatically extracted from conversations and saved items.

**Columns:**
- `id` (INTEGER, PRIMARY KEY): Unique identifier
- `user_id` (INTEGER, FOREIGN KEY): References users.id
- `milestone_type` (VARCHAR(50)): Type of milestone
- `milestone_data` (JSONB): Milestone-specific data
- `title` (VARCHAR(255)): Human-readable milestone title
- `description` (TEXT): Detailed description
- `category` (VARCHAR(50)): Category (career, skill, assessment, peer, challenge)
- `progress_percentage` (FLOAT): Progress towards completion (0-100)
- `status` (VARCHAR(20)): Status (active, completed, abandoned)
- `source_type` (VARCHAR(50)): Where milestone originated
- `source_id` (INTEGER): ID of the source
- `conversation_id` (INTEGER, FOREIGN KEY): References conversations.id
- `achieved_at` (TIMESTAMP): When milestone was completed
- `created_at` (TIMESTAMP): When milestone was created
- `updated_at` (TIMESTAMP): Last update time
- `ai_insights` (JSONB): AI-generated insights about the milestone
- `next_steps` (JSONB): Suggested next actions

**Indexes:**
- Primary key on `id`
- Foreign key indexes on `user_id` and `conversation_id`
- Index on `milestone_type` for filtering
- Index on `category` for category-based queries
- Index on `status` for progress tracking
- Index on `created_at` for timeline views
- Composite index on `(user_id, status)`
- Composite index on `(user_id, category)`
- GIN index on `milestone_data` for data search

**Relationships:**
- Many-to-One with `users` (cascade delete)
- Many-to-One with `conversations` (set null on delete)

## Updated Tables

### saved_recommendations
Added columns to support Orientator AI integration:

**New Columns:**
- `source_tool` (VARCHAR(50)): Tool that generated the recommendation
- `conversation_id` (INTEGER, FOREIGN KEY): References conversations.id
- `component_type` (VARCHAR(50)): Type of component saved
- `component_data` (JSON): Component-specific data
- `interaction_metadata` (JSON): How the user interacted with the component

**New Indexes:**
- Index on `source_tool` for tool analytics
- Index on `conversation_id` for conversation-based queries

## Performance Considerations

### Indexes Strategy
1. **Primary Indexes**: All tables have primary key indexes for fast lookups
2. **Foreign Key Indexes**: All foreign keys are indexed for join performance
3. **Query Optimization**: Indexes on commonly filtered columns (type, status, category)
4. **Time-based Queries**: Indexes on created_at for chronological queries
5. **JSONB Search**: GIN indexes on JSONB columns for efficient JSON queries
6. **Composite Indexes**: Multi-column indexes for common query patterns

### Expected Query Patterns
1. Get all components for a message
2. Get all tool invocations for a conversation
3. Get user's journey milestones by status/category
4. Track tool usage statistics by user
5. Analyze tool performance (execution times)
6. Search within JSONB data structures

### Data Growth Estimates
- **message_components**: 2-5 components per AI message
- **tool_invocations**: 1-3 invocations per AI response
- **user_journey_milestones**: 10-50 milestones per active user
- **saved_recommendations**: Additional metadata per save

## Migration Notes

### Migration File
- Location: `/backend/alembic/versions/2025_06_24_202407_add_orientator_ai_tables.py`
- Revision ID: `add_orientator_ai_tables`
- Depends on: `7085dfa9bba2`

### Running the Migration
```bash
cd backend
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

## Data Integrity

### Cascade Rules
1. Deleting a message deletes all its components
2. Deleting a conversation deletes all tool invocations
3. Deleting a user deletes all journey milestones
4. Deleting a conversation sets milestone conversation_id to NULL

### Constraints
1. message_components.message_id cannot be NULL
2. tool_invocations.conversation_id cannot be NULL
3. user_journey_milestones.user_id cannot be NULL
4. All timestamps default to current time

## Security Considerations

1. **JSONB Data**: Validate all JSON data before insertion
2. **Tool Names**: Whitelist allowed tool names
3. **User Access**: Ensure users can only access their own data
4. **Sensitive Data**: Avoid storing sensitive information in JSONB fields

## Monitoring and Maintenance

### Key Metrics to Monitor
1. Average tool execution time by tool type
2. Tool success/failure rates
3. Component save rates by type
4. Milestone completion rates
5. Storage growth rate of JSONB columns

### Maintenance Tasks
1. Regular VACUUM on tables with high update frequency
2. Monitor index usage and remove unused indexes
3. Archive old tool invocation data
4. Analyze query performance regularly