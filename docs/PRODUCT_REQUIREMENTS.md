# Product Requirements Document (PRD) for Orientor

## 1. Introduction
Orientor is a career guidance platform that leverages machine learning and Holland Code assessments to provide personalized career recommendations, skill progression paths, and peer matching based on user profiles. The system integrates with external services for embeddings and database management, ensuring scalable and secure operations.

---

## 2. Core Functional Requirements

### 2.1 User Authentication
- [ ] Implement user registration and login via email/password or OAuth.
- [ ] Secure user data with encryption (e.g., bcrypt for passwords).
- [ ] Role-based access control (admin vs. regular user).

### 2.2 Holland Code Assessment
- [ ] Frontend component (`FindYourWay.tsx`) to collect user responses to Holland Code questions.
- [ ] Backend service (`LLMholland_service.py`) to analyze responses and generate Holland Code.
- [ ] Store Holland Code results in user profiles (`user_profile.py`).
- [ ] Validate assessment inputs to prevent invalid submissions.

### 2.3 Career Recommendations
- [ ] LLM service (`LLMcareerTree.py`) to generate career paths based on Holland Code and skills.
- [ ] API endpoint `/api/careers/recommendations` to fetch recommendations.
- [ ] Frontend display components (`SavedRecommendationsList.tsx`, `RecommendationDetail.tsx`).
- [ ] Allow users to save recommendations (`saved_recommendation.py` model).

### 2.4 Peer Matching
- [ ] Service (`peer_matching_service.py`) to find peers with similar Holland Code and cognitive traits.
- [ ] Use embeddings from `esco_embedding_service384.py` and `Oasisembedding_service.py`.
- [ ] Display peer matches via `/api/peers` endpoint and frontend components (`spaceService.ts`).
- [ ] Include peer profiles (name, skills, experience) in matching results.

### 2.5 Skill Tree Visualization
- [ ] Backend models (`user_skill_tree.py`, `user_skill.py`) to define skill hierarchies and proficiency levels.
- [ ] Frontend radar chart (`SkillRadarChart.tsx`) to visualize skill levels.
- [ ] Progress tracking via `user_progress.py` model (e.g., skill completion percentage).
- [ ] Allow users to update skill proficiencies via UI (`user_note.py` for notes).

### 2.6 Database & Migrations
- [ ] PostgreSQL database with tables for users, recommendations, and skills.
- [ ] Use Alembic for migration management (`alembic/versions/*.py`).
- [ ] Track user interactions (e.g., `message.py` for chat history).
- [ ] Backup database schema (`backend/orientor_db_backup.sql`).

### 2.7 Onboarding & Profile Management**
- Multi-signal profile collection** (`onboarding.ts`): Collect age, skills, education, story, RIASEC psychometrics, and interests via a questionnaire (`Profil/questions.tsx`).  
- User Avatar Generation** (`avatarService.py`): LLM-driven unique avatar based on psychological profiles.  

### 2.8. LLM-Driven Profile Building**
- ESCO/OaSIS Alignment**: Convert user data into structured formats via `esco_profile_builder.py` and `oasis_profile_builder.py`.  
- Holland Test**:  
    - 42-Question Assessment** (`HollandTest.tsx`): Store responses in `user_holland_responses` table.  
    - Detailed Results Page** (`HollandResultsView.tsx`): Hexagon visualization + LLM explanations.  

### 2.9. Career Recommendations**
- Swipe-Based Jobs** (`swipe_recommendations.py`): Tinder-like interface using OaSIS embeddings.  
  Database**: `user_recommendations` table tracks swiped jobs with `swiped_right` flag.  
- Vector Search** (`vector_search.py`): Free-text job queries via Pinecone.  

### 2.10. Competence & Skills Tree**
- Emotion-First Exploration** (`gnn_explorer.py`): GNN-driven skill paths with hidden nodes.  
- Structured Progression** (`skill_tree_service.py`): Skill→job paths with XP system.  
  Database**:  
  - `user_skill_trees`: Stores personalized skill tree configurations (JSONB structure).  
  - `node_notes`: Captures user annotations on skill nodes (e.g., notes on "Python Basics").  
  - `tree_paths`: Tracks user-created skill path configurations.  

### 2.11. Peer Matching**
- Similarity Search** (`peer_matching_service.py`): Find top 5 peers via ESCO embeddings.  
- Peer Profiles** (`PeerCard.tsx`): Display skill overlap and activity.  

### 2.12. Social Features**
- Activity Feed** (`ActivityFeed.tsx`): Show user/peer achievements (e.g., "Completed Python Basics").  
- Challenges** (`ChallengeCard.tsx`): Propose skill-based challenges tracked in `challenge_progress` table.  

### 2.13. Gamification**
- XP System**:  
  - Leaderboard** (`Leaderboard.tsx`): Global rankings via `/api/xp` endpoint.  
  - Progress Bar** (`XPProgress.tsx`): Real-time XP tracking.  
  Database**: `user_progress` table tracks XP, level, and completed actions (JSON field).  

### 2.14. Socratic Chat**
- Motivational Bot** (`orientator_chat.py`): Reflective Q&A with chat history stored in `messages` table.  
  Schema**:  
  | Column         | Type       | Notes                          |  
  |----------------|------------|--------------------------------|  
  | message_id     | Integer    | PK                             |  
  | sender_id      | Integer    | FK to users.id                 |  
  | body           | Text       | Message content                |  
  | timestamp      | DateTime   | Indexed for chronological sort |  

### 2.15. Persistence**
- "My Space" Tab** (`spaceService.ts`): Save career paths, skill trees, and peer comparisons.  
  Database**:  
  - `saved_recommendations`: Stores detailed job analyses (e.g., `role_creativity` scores).  
  - `user_notes`: Captures free-text notes linked to saved recommendations.  

### 2.16 Holland Test Integration
- 42-Question Assessment** (`HollandTest.tsx`): Stores responses in `user_holland_responses` table.  
- Narrative Feedback** (`holland_analysis.py`): LLM explains results and links to user preferences.  

### 2.17 Social Features
- Activity Feed (`ActivityFeed.tsx`): Shows skill unlocks and challenge completions (tracked in `challenge_progress`).  

---

## 3. Non-Functional Requirements

### 3.1 Performance
- [ ] API response time under 2 seconds for recommendations.
- [ ] Embedding generation within 500ms for real-time feedback.
- [ ] Database queries optimized for 10k+ users.

### 3.2 Scalability
- [ ] Support 10k concurrent users via Railway's PostgreSQL and Redis scaling.
- [ ] ML models optimized for batch processing of user data (e.g., Pinecone vector storage).
- [ ] Horizontal scaling for backend services using Docker (`compose.yml`).

### 3.3 Security
- [ ] Encrypt sensitive user data (e.g., Holland Code, skill vectors) at rest and in transit.
- [ ] Use HTTPS for all API communications.
- [ ] Rate-limit API endpoints to prevent abuse.

### 3.4 Maintainability
- [ ] Clear separation of concerns in code (e.g., services, routers, models).
- [ ] Automated tests for critical components (e.g., `test/check_db.py`).
- [ ] Logging via `app/utils/logging_config.py` for debugging and monitoring.

---

## 4. Technical Architecture

### 4.1 Backend (Python/Flask)
- **Framework**: Flask/Python
- **Key Components**:
  - **Services**: 
    - `LLMcareerTree.py` (career path generation)
    - `peer_matching_service.py` (peer matching logic)
    - `esco_embedding_service384.py` (ESCO embedding generation)
    - `Oasisembedding_service.py` (OASIS embedding generation)
  - **API Routers**: 
    - `/careers` (recommendations)
    - `/users` (profile management)
    - `/space` (notes and saved recommendations)
    - `/api/messages` (chat history)
  - **Database**: PostgreSQL with SQLAlchemy ORM (`app/models/*.py`).
  - **ML Integration**: 
    - Pinecone (vector database)
    - HuggingFace (pre-trained embeddings)
    - PyTorch Geometric (GNN models in `data_n_notebook/gnn_experiment/`).

### 4.2 Frontend (React/TypeScript)
- **Framework**: Next.js with TypeScript.
- **Key Components**:
  - **SkillRadarChart.tsx**: Visualizes skill proficiency levels.
  - **Recommendation List**: 
    - `SavedRecommendationsList.tsx` (displays saved paths)
    - `RecommendationDetail.tsx` (detailed view of recommendations).
  - **Holland Assessment UI**: 
    - `FindYourWay.tsx` (assessment form)
    - `HealthCheck.tsx` (user progress overview).

### 4.3 Deployment
- **Backend**: Hosted on Railway (PostgreSQL, Redis) via `backend/railway.toml`.
- **Frontend**: Deployed on Vercel via `deploy/vercel.json`.
- **Docker**: Uses `compose.yml` for local development environments.

---

## 5. Data Flow Diagram

```mermaid
graph TD
    A[User Interface] --> B{API Calls}
    B --> C[Flask Backend]
    C --> D[Database (PostgreSQL)]
    C --> E[ML Services (Pinecone, HuggingFace)]
    C --> F[LLM Services]
    D --> G[User Profiles]
    D --> H[Recommendations]
    E --> I[Embeddings]
    F --> J[Career Path Generation]
    G --> K[Holland Code Analysis]
    K --> L[Skill Tree Visualization]
```

---

## 6. Dependencies & Integrations
- **External Services**:
  - Pinecone (vector database for embeddings)
  - Railway (cloud hosting for PostgreSQL/Redis)
  - HuggingFace (pre-trained transformer models)
  - MLflow (experiment tracking in `data_n_notebook/MLflow_HuggingFace/`).
- **Libraries**:
  - Alembic (database migrations)
  - PyTorch Geometric (GNN models)
  - spaCy (NLP preprocessing)
  - Axios (frontend API requests)

---

## 7. Future Enhancements
- **GNN-Based Recommendations**: 
  - Use GraphSage (`backend/app/services/GNN/GraphSage.py`) to predict career paths.
  - Train models with `data_n_notebook/gnn_experiment/train_edge_regressor.py`.
- **Real-Time Chat**: 
  - Implement WebSocket integration for instant feedback.
  - Store chat messages in `message.py` model.
- **Peer Matching Improvements**: 
  - Add cosine similarity calculations for embeddings.
  - Integrate with `generate_pairs.py` for better data pairing.

---

## 8. GNN Model Pipeline Diagram

```mermaid
graph TD
    A[User Data] --> B[Data Preprocessing]
    B --> C[Graph Construction]
    C --> D[GraphSAGE Model Training]
    D --> E[Trained Model (GraphSage.pt)]
    E --> F[Inference Endpoint]
    F --> G[Career Recommendations Service]
    G --> H[API Response to Frontend]
    D --> I[Model Evaluation]
    I --> J[MLflow Tracking]
    C --> K[Node/Edge Features (Embeddings)]
    K --> C
## 9. Database Schema Documentation

### 1. users
**Table**: users  
**Description**: Stores user account information.  
**Columns**:  
| Column Name       | Data Type       | Constraints/Notes                          |  
|-------------------|-----------------|--------------------------------------------|  
| id                | Integer         | Primary Key                                |  
| username          | String          | Nullable                                   |  
| email             | String          | Unique, Nullable                           |  
| hashed_password   | String          | Nullable                                   |  
| created_at        | DateTime        | Default: `now()`, Not Null                 |  

**Indices**:  
- `ix_users_email` (Unique)  
- `ix_users_username` (Unique)  

---

### 2. user_skills
**Table**: user_skills  
**Description**: Tracks user skill proficiencies and cognitive traits.  
**Columns**:  
| Column Name         | Data Type   | Constraints/Notes                          |  
|---------------------|-------------|--------------------------------------------|  
| id                  | Integer     | Primary Key                                |  
| user_id             | Integer     | Foreign Key (`users.id`), Not Null         |  
| creativity          | Float       | Nullable                                   |  
| leadership          | Float       | Nullable                                   |  
| digital_literacy    | Float       | Nullable                                   |  
| critical_thinking   | Float       | Nullable                                   |  
| problem_solving     | Float       | Nullable                                   |  
| last_updated        | DateTime    | Default: `now()`, Not Null                 |  

**Constraints**:  
- Unique constraint on `user_id`  

**Indices**:  
- `ix_user_skills_id`  

**Relationships**:  
- Foreign Key: `user_id` → `users.id`  

---

### 3. suggested_peers
**Table**: suggested_peers  
**Description**: Stores peer matching suggestions and similarity scores.  
**Columns**:  
| Column Name     | Data Type       | Constraints/Notes                          |  
|-----------------|-----------------|--------------------------------------------|  
| user_id         | Integer         | Primary Key (composite), FK to `users.id`  |  
| suggested_id    | Integer         | Primary Key (composite), FK to `users.id`  |  
| similarity      | Float           | Nullable                                   |  
| created_at      | DateTime        | Default: `now()`, Not Null                 |  
| updated_at      | DateTime        | OnUpdate: `now()`, Nullable                |  

**Indices**:  
- `ix_suggested_peers_user_id`  
- `ix_suggested_peers_suggested_id`  

**Relationships**:  
- Composite Primary Key: `user_id`, `suggested_id`  
- Foreign Keys: Both columns reference `users.id`  

---

### 4. user_profiles
**Table**: user_profiles  
**Description**: Contains detailed user profile information and embeddings.  
**Columns**:  
| Column Name             | Data Type         | Constraints/Notes                          |  
|-------------------------|-------------------|--------------------------------------------|  
| embedding               | float[]           | Added via `add_vector_embeddings`          |  
| favorite_movie          | VARCHAR(255)      | Added via `update_profile_fields`          |  
| favorite_book           | VARCHAR(255)      | Added via `update_profile_fields`          |  
| favorite_celebrities    | TEXT              | Added via `update_profile_fields`          |  
| learning_style          | VARCHAR(50)       | Added via `update_profile_fields`          |  
| interests               | TEXT              | Added via `update_profile_fields`          |  
| (OASIS-related fields)  |                   | Inferred from `add_oasis_columns` migration |  

**Note**: The `add_oasis_columns` migration may include additional columns for OASIS embeddings or traits. These should be reviewed for completeness.  

---

### 5. saved_recommendations
**Table**: saved_recommendations  
**Description**: Stores user-saved career recommendations with cognitive trait analysis.  
**Columns**:  
| Column Name             | Data Type       | Constraints/Notes                          |  
|-------------------------|-----------------|--------------------------------------------|  
| analytical_thinking     | Float           | Nullable                                   |  
| attention_to_detail     | Float           | Nullable                                   |  
| collaboration           | Float           | Nullable                                   |  
| adaptability            | Float           | Nullable                                   |  
| independence            | Float           | Nullable                                   |  
| evaluation              | Float           | Nullable                                   |  
| decision_making         | Float           | Nullable                                   |  
| stress_tolerance        | Float           | Nullable                                   |  
| all_fields              | JSONB           | Nullable                                   |  

**Note**: This table is linked to user profiles for storing recommendation analysis results.  

---

**Relationships Summary**:  
- `user_skills.user_id` → `users.id`  
- `suggested_peers.user_id` and `suggested_id` → `users.id`  
- `saved_recommendations` likely references `users.id` (not explicitly shown in migrations but inferred from context).
### 6. messages
**Table**: messages  
**Description**: Stores user chat messages and interactions.  
**Columns**:  
| Column Name         | Data Type         | Constraints/Notes                          |  
|---------------------|-------------------|--------------------------------------------|  
| message_id          | Integer           | Primary Key, Sequence-generated            |  
| sender_id           | Integer           | FK to `users.id`, Not Null, Indexed         |  
| recipient_id        | Integer           | FK to `users.id`, Not Null, Indexed         |  
| body                | Text              | Not Null                                   |  
| timestamp           | DateTime          | Default: `now()`, Not Null, Indexed         |  

**Indices**:  
- `ix_messages_sender_id`  
- `ix_messages_recipient_id`  
- `ix_messages_timestamp`  

**Relationships**:  
- `sender_id` → `users.id` (User who sent the message)  
- `recipient_id` → `users.id` (User who received the message)  

---

### 7. user_notes
**Table**: user_notes  
**Description**: Stores user-created notes linked to saved recommendations.  
**Columns**:  
| Column Name             | Data Type   | Constraints/Notes                          |  
|-------------------------|-------------|--------------------------------------------|  
| id                      | Integer     | Primary Key                                |  
| user_id                 | Integer     | FK to `users.id`, Not Null                 |  
| saved_recommendation_id | Integer     | FK to `saved_recommendations.id`, Nullable |  
| content                 | Text        | Not Null                                   |  
| created_at              | DateTime    | Default: `now()`, Not Null                 |  
| updated_at              | DateTime    | Default: `now()`, Not Null                 |  

**Relationships**:  
- `user_id` → `users.id`  
- `saved_recommendation_id` → `saved_recommendations.id`  

---

### 8. user_progress
**Table**: user_progress  
**Description**: Tracks user gamification progress (XP, levels, completed actions).  
**Columns**:  
| Column Name             | Data Type         | Constraints/Notes                          |  
|-------------------------|-------------------|--------------------------------------------|  
| id                      | UUID              | Primary Key (UUIDv4)                       |  
| user_id                 | Integer           | FK to `users.id`, Unique, Not Null         |  
| total_xp                | Integer           | Default: 0, Not Null                       |  
| level                   | Integer           | Default: 1, Not Null                       |  
| last_completed_node     | String(100)       | Nullable                                   |  
| completed_actions       | JSON              | Default: empty dict, Nullable              |  
| last_updated            | DateTime          | OnUpdate: `now()`, Not Null                |  

**Constraints**:  
- Unique constraint on `user_id`  

**Relationships**:  
- `user_id` → `users.id` (One-to-One relationship)  

---

**Additional Notes**:  
- The `saved_recommendations` table likely contains a `user_id` FK (not explicitly shown in migrations but implied by context).  
- The `finetuned_model` directory contains ML model files, not database tables.  
- Relationships like `UserProgress.user` and `UserNote.recommendation` should be implemented via SQLAlchemy ORM.
### 9. node_notes
**Table**: node_notes  
**Description**: Stores user annotations for specific nodes in skill trees.  
**Columns**:  
| Column Name     | Data Type   | Constraints/Notes                          |  
|-----------------|-------------|--------------------------------------------|  
| id              | Integer     | Primary Key                                |  
| user_id         | Integer     | FK to `users.id`, Not Null                 |  
| node_id         | String(100) | Not Null                                   |  
| action_index    | Integer     | Not Null                                   |  
| note_text       | Text        | Not Null                                   |  
| updated_at      | DateTime    | Default: `now()`, Not Null                 |  

**Relationships**:  
- `user_id` → `users.id`  

---

### 10. tree_paths
**Table**: tree_paths  
**Description**: Stores user-created skill tree configurations.  
**Columns**:  
| Column Name     | Data Type         | Constraints/Notes                          |  
|-----------------|-------------------|--------------------------------------------|  
| id              | UUID              | Primary Key (UUIDv4)                       |  
| user_id         | Integer           | FK to `users.id`, Not Null                 |  
| tree_type       | String            | Not Null                                   |  
| tree_json       | JSONB             | Not Null (Stores tree structure)           |  
| name            | String            | Optional                                   |  
| created_at      | DateTime          | Default: `now()`, Not Null                 |  

**Relationships**:  
- `user_id` → `users.id`  

---

**Final Notes**:  
- All tables now documented except potential `user_recommendation` and `user_skill_tree` tables which require further code analysis.  
- Relationships like `TreePath.user` and `NodeNote.user` should be implemented via SQLAlchemy ORM.
### 11. user_recommendations
**Table**: user_recommendations  
**Description**: Stores skill recommendations shown to users.  
**Columns**:  
| Column Name         | Data Type   | Constraints/Notes                          |  
|---------------------|-------------|--------------------------------------------|  
| id                  | Integer     | Primary Key                                |  
| user_id             | Integer     | FK to `users.id`, Not Null                 |  
| oasis_code          | String      | Not Null                                   |  
| label               | String      | Not Null                                   |  
| swiped_right        | Boolean     | Default: False                             |  
| created_at          | DateTime    | Default: `now()`, Not Null                 |  

**Relationships**:  
- `user_id` → `users.id`  

---

### 12. user_skill_trees
**Table**: user_skill_trees  
**Description**: Stores personalized skill tree configurations for users.  
**Columns**:  
| Column Name         | Data Type         | Constraints/Notes                          |  
|---------------------|-------------------|--------------------------------------------|  
| id                  | Integer           | Primary Key                                |  
| user_id             | Integer           | FK to `users.id`, Not Null                 |  
| graph_id            | String            | Unique, Default: UUIDv4                    |  
| tree_data           | JSONB             | Not Null (Stores tree structure)           |  
| created_at          | DateTime          | Default: `now()`, Not Null                 |  

**Constraints**:  
- Unique constraint on `graph_id`  

**Relationships**:  
- `user_id` → `users.id`  

---

**Final Notes**:  
- All database tables from `backend/app/models` are now fully documented.  
- Relationships like `UserSkillTree.user` and `UserRecommendation.user` should be implemented via SQLAlchemy ORM.  
- The `saved_recommendations` table still needs verification for its `user_id` foreign key.
### 13. saved_recommendations
**Table**: saved_recommendations  
**Description**: Stores user-saved career recommendations with detailed analysis.  
**Columns**:  
| Column Name               | Data Type   | Constraints/Notes                          |  
|---------------------------|-------------|--------------------------------------------|  
| id                        | Integer     | Primary Key                                |  
| user_id                   | Integer     | FK to `users.id`, Not Null, Indexed         |  
| oasis_code                | String      | Not Null                                   |  
| label                     | String      | Not Null                                   |  
| description               | Text        | Nullable                                   |  
| main_duties               | Text        | Nullable                                   |  
| role_creativity           | Float       | Nullable                                   |  
| role_leadership           | Float       | Nullable                                   |  
| role_digital_literacy     | Float       | Nullable                                   |  
| role_critical_thinking    | Float       | Nullable                                   |  
| role_problem_solving      | Float       | Nullable                                   |  
| analytical_thinking       | Float       | Nullable                                   |  
| attention_to_detail       | Float       | Nullable                                   |  
| collaboration             | Float       | Nullable                                   |  
| adaptability              | Float       | Nullable                                   |  
| independence              | Float       | Nullable                                   |  
| evaluation                | Float       | Nullable                                   |  
| decision_making           | Float       | Nullable                                   |  
| stress_tolerance          | Float       | Nullable                                   |  
| all_fields                | JSON        | Nullable                                   |  
| saved_at                  | DateTime    | Default: `now()`, Not Null                 |  

**Constraints**:  
- Unique constraint on `user_id` + `oasis_code`  

**Relationships**:  
- `user_id` → `users.id`  
- One-to-Many with `user_notes` (via `UserNote.saved_recommendation_id`)  
