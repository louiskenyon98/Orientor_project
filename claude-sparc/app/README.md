# Orientor Platform Guide

## 1. Project Context  
**Mission & Purpose**  
Orientor empowers users with AI-driven career guidance: personalized skill trees, psychometric assessments, peer matching, and job recommendations. It combines proven psychological frameworks (Holland RIASEC, HEXACO personality) with state-of-the-art ML (GNNs, LLMs, vector embeddings) to translate user profiles into actionable insights.

**Key Architectural Decisions**  
- **FastAPI + Next.js 13**:  
  - FastAPI for lightweight, async-ready APIs with automatic OpenAPI schemas. Enables rapid evolution of API surface without sacrificing performance.  
  - Next.js App Router for server-rendered pages, incremental static regeneration, seamless routing and shared layout. Ensures fast initial load and smooth UX.

- **Vector Databases (Pinecone)**:  
  - Decouples semantic search from relational data. Embeddings stored in Pinecone accelerate similarity queries (peer matching, skill suggestions) while PostgreSQL holds canonical records.

- **ML Approach**:  
  - **LLMs** for narrative generation (career paths, personality descriptions) because of flexibility in prompt-driven text generation.  
  - **Graph Neural Networks** for skill dependency modeling—captures non-Euclidean relationships in competence trees.  
  - **Sentence Transformers** for embedding similarity—essential for peer matching and semantic search.

**Integration Philosophy**  
- Treat psychological models as **pluggable modules**—tests expose scores via consistent schema; downstream services (recommendations, embeddings) consume normalized outputs.  
- Maintain clear boundaries: psychometric scoring ≠ skill embedding ≠ career recommendation. Each service focuses on single responsibility and communicates over well-defined interfaces.

---

## 2. Coding Standards & Preferences  

### Backend Patterns  
- **Service Layer Organization**  
  - Business logic (ML calls, embeddings, graph computations) lives in `services/`.  
  - Routers (`app/routers/…`) remain thin: validate input, call service, wrap output in Pydantic schema.

- **Dependency Injection**  
  - Use `Depends(get_db)` for database sessions.  
  - Inject current user via `Depends(get_current_user)`—avoid global state, enable testing by swapping dependencies.

- **Error Handling**  
  - Wrap domain errors in custom exceptions, map to FastAPI HTTPException with consistent error schema.  
  - Centralized exception handlers for 4xx/5xx classes ensure uniform JSON error responses.

- **Logging**  
  - Configure per-module `logger = logging.getLogger(__name__)`.  
  - Use rotating file handler for persistence; include correlation IDs (e.g., request UUID) in log context.

### Frontend Patterns  
- **Component Organization**  
  - Group by feature: each route folder under `src/app/` has page, layout, loading components.  
  - Shared UI primitives (buttons, modals) in `components/ui/`.  
  - Domain widgets (skill tree, peer list) in `components/feature-name/`.

- **State Management**  
  - Leverage React Contexts for global state (theme, user session).  
  - Local state via hooks inside feature components; avoid Redux for small to medium state surface.

- **API Service Patterns**  
  - Central `api.ts` exports axios instance with interceptors for auth header and error logging.  
  - Feature services (e.g., `hollandTestService.ts`) wrap endpoint calls, handle retries, surface typed data.

### Database Patterns  
- **Relationship Modeling**  
  - Explicit `relationship(..., cascade="all, delete-orphan", lazy="selectin")` for parent-child lifecycles (user → notes, skill_trees).  
  - Prefer `selectinload` over `joinedload` in queries to balance eager loading with pagination.

- **Migration Strategy**  
  - Alembic migrations organized by feature.  
  - Name revisions with feature prefixes (e.g., `2025_05_add_holland_fields.py`) to trace domain evolution.

### ML Integration Patterns  
- **LLM Services**  
  - Each LLM interaction encapsulated in a service class (e.g., `HollandLLMService`).  
  - Centralize prompt templates and temperature/config settings in dedicated module, separate from API calls.

- **Embedding Services**  
  - Provide uniform `embed_items(items: List[str]) → List[Vector]` interface.  
  - Cache embedding calls in Redis when possible to avoid repeated OpenAI/Pinecone usage.

---

## 3. Framework Preferences  

### FastAPI  
- **Router Philosophy**  
  - One router per domain (auth, profiles, tests, recommendations).  
  - Use path prefixes (`/api/v1/…`) for versioning.  
- **Dependency Patterns**  
  - Inject minimal dependencies; group related dependencies in provider functions.

### Next.js  
- **App Router Usage**  
  - Leverage nested layouts to share header/navigation across features.  
  - Use `loading.tsx` for suspenseful data fetching; `error.tsx` for error boundaries.

### SQLAlchemy  
- **Relationship Approach**  
  - Model one-to-many as simple lists; many-to-many via association tables with explicit model to track metadata.  
- **Query Patterns**  
  - Favor ORM queries for simple CRUD; use raw SQL or text queries for complex analytics only when performance demands.

### Tailwind  
- **Theme Organization**  
  - Define semantic colors (e.g., `primary`, `secondary`, `accent`) in `tailwind.config.js`.  
  - Use CSS variables (`var(--background)`) for runtime theming; avoid arbitrary hexes in components.

---

## 4. File Structure Philosophy  
- **Separation of Concerns**  
  - Keep API, business logic, and data access in distinct layers.  
  - Frontend: separate page-level data fetching from presentational components.

- **Service Layer Boundaries**  
  - Each service module owns its own dependencies and does not import routers or Pydantic schemas. Services return pure Python dicts or domain objects.

- **Component Organization Logic**  
  - Feature directories under `src/app/`; shared components under `components/`.  
  - Maintain consistent naming: `FeatureNameList`, `FeatureNameDetail`, `FeatureNameService`.

---

## 5. Testing Philosophy  
- **Layered Strategy**  
  - **Unit**: Test pure functions in services (e.g., score calculation, prompt template generation) without DB or network.  
  - **Integration**: Spin up a test database container; run selected endpoints via FastAPI TestClient. Mock external ML calls.  
  - **E2E**: Lightweight smoke tests using headless browser to verify critical user flows (onboarding → test → recommendations).

- **What to Test vs Mock**  
  - Test data mapping, business rules, error scenarios in unit tests.  
  - Mock LLM and embedding APIs; focus integration tests on database transactions and router wiring.

- **Test Data Management**  
  - Use fixtures to seed minimal dataset for isolation.  
  - Version test schema migrations alongside production migrations.

---

## 6. Deployment Philosophy  
- **Environment Management**  
  - Centralize config via Pydantic Settings; override via environment variables.  
  - Keep secrets out of code; inject via CI/CD pipeline.

- **Configuration Strategy**  
  - Use feature flags or env flags (`FEATURE_X_ENABLED`) for gradual rollout.  
  - Version API with path prefixes to allow backward-compatible changes.

- **Monitoring & Logging**  
  - Expose `/health` and custom `/metrics` endpoints.  
  - Aggregate structured logs (JSON) to external service (e.g., ELK or cloud logging).  
  - Capture error traces with correlation IDs; instrument key ML calls with timing metrics. 

# Database Schema
"alembic_version"	"version_num"	"character varying"	"NO"	
"behavioral_signals"	"id"	"integer"	"NO"	"nextval('behavioral_signals_id_seq'::regclass)"
"behavioral_signals"	"user_id"	"integer"	"NO"	
"behavioral_signals"	"signal_type"	"character varying"	"NO"	
"behavioral_signals"	"signal_data"	"jsonb"	"NO"	
"behavioral_signals"	"confidence_score"	"double precision"	"YES"	
"behavioral_signals"	"context_metadata"	"jsonb"	"YES"	"'{}'::jsonb"
"behavioral_signals"	"detected_at"	"timestamp with time zone"	"NO"	"now()"
"behavioral_signals"	"created_at"	"timestamp with time zone"	"NO"	"now()"
"developmental_milestones"	"id"	"integer"	"NO"	"nextval('developmental_milestones_id_seq'::regclass)"
"developmental_milestones"	"user_id"	"integer"	"NO"	
"developmental_milestones"	"milestone_type"	"character varying"	"NO"	
"developmental_milestones"	"milestone_description"	"text"	"NO"	
"developmental_milestones"	"achievement_date"	"timestamp with time zone"	"NO"	
"developmental_milestones"	"confidence_level"	"double precision"	"YES"	
"developmental_milestones"	"supporting_evidence"	"jsonb"	"YES"	
"developmental_milestones"	"created_at"	"timestamp with time zone"	"NO"	"now()"
"developmental_milestones"	"updated_at"	"timestamp with time zone"	"NO"	"now()"
"gca_choices"	"id"	"integer"	"NO"	
"gca_choices"	"title"	"character varying"	"NO"	
"gca_choices"	"question_id"	"integer"	"NO"	
"gca_choices"	"sort_idx"	"integer"	"NO"	
"gca_choices"	"active"	"integer"	"NO"	
"gca_choices"	"r"	"numeric"	"NO"	
"gca_choices"	"i"	"numeric"	"NO"	
"gca_choices"	"a"	"numeric"	"NO"	
"gca_choices"	"s"	"numeric"	"NO"	
"gca_choices"	"e"	"numeric"	"NO"	
"gca_choices"	"c"	"numeric"	"NO"	
"gca_holland_questions"	"id"	"integer"	"NO"	"nextval('gca_holland_questions_id_seq'::regclass)"
"gca_holland_questions"	"question"	"text"	"NO"	
"gca_holland_questions"	"personality_code"	"character"	"NO"	
"gca_personalities"	"id"	"character varying"	"NO"	
"gca_personalities"	"initial"	"character varying"	"NO"	
"gca_personalities"	"title"	"character varying"	"NO"	
"gca_personalities"	"alias"	"character varying"	"NO"	
"gca_personalities"	"description"	"text"	"NO"	
"gca_questions"	"id"	"integer"	"NO"	
"gca_questions"	"title"	"character varying"	"NO"	
"gca_questions"	"test_id"	"integer"	"NO"	
"gca_questions"	"chapter_number"	"integer"	"NO"	
"gca_questions"	"sort_idx"	"integer"	"NO"	
"gca_questions"	"active"	"integer"	"NO"	
"gca_results"	"id"	"uuid"	"NO"	"gen_random_uuid()"
"gca_results"	"attempt_id"	"uuid"	"NO"	
"gca_results"	"test_id"	"integer"	"NO"	
"gca_results"	"r_score"	"numeric"	"NO"	
"gca_results"	"i_score"	"numeric"	"NO"	
"gca_results"	"a_score"	"numeric"	"NO"	
"gca_results"	"s_score"	"numeric"	"NO"	
"gca_results"	"e_score"	"numeric"	"NO"	
"gca_results"	"c_score"	"numeric"	"NO"	
"gca_results"	"top_3_code"	"character"	"NO"	
"gca_results"	"created_at"	"timestamp with time zone"	"YES"	"CURRENT_TIMESTAMP"
"gca_results"	"user_id"	"integer"	"YES"	
"gca_tests"	"id"	"integer"	"NO"	
"gca_tests"	"title"	"character varying"	"NO"	
"gca_tests"	"description"	"text"	"NO"	
"gca_tests"	"seo_code"	"character varying"	"NO"	
"gca_tests"	"video_url"	"text"	"NO"	
"gca_tests"	"image_url"	"text"	"NO"	
"gca_tests"	"chapter_count"	"integer"	"NO"	
"gca_tests"	"question_count"	"integer"	"NO"	
"gca_tests"	"active"	"integer"	"NO"	
"gca_users_answers"	"id"	"character varying"	"NO"	
"gca_users_answers"	"attempt_id"	"character varying"	"NO"	
"gca_users_answers"	"user_id"	"character varying"	"YES"	
"gca_users_answers"	"test_id"	"integer"	"NO"	
"gca_users_answers"	"question_id"	"integer"	"NO"	
"gca_users_answers"	"choice_id"	"integer"	"NO"	
"gca_users_answers"	"created_at"	"timestamp with time zone"	"NO"	"(CURRENT_TIMESTAMP AT TIME ZONE 'America/Montreal'::text)"
"messages"	"message_id"	"integer"	"NO"	"nextval('message_id_seq'::regclass)"
"messages"	"sender_id"	"integer"	"NO"	
"messages"	"recipient_id"	"integer"	"NO"	
"messages"	"body"	"text"	"NO"	
"messages"	"timestamp"	"timestamp with time zone"	"NO"	"now()"
"node_notes"	"id"	"character varying"	"NO"	
"node_notes"	"user_id"	"integer"	"YES"	
"node_notes"	"node_id"	"character varying"	"YES"	
"node_notes"	"action_index"	"integer"	"YES"	
"node_notes"	"note_text"	"text"	"YES"	
"node_notes"	"created_at"	"timestamp without time zone"	"YES"	"now()"
"node_notes"	"updated_at"	"timestamp without time zone"	"YES"	"now()"
"personality_assessments"	"id"	"integer"	"NO"	"nextval('personality_assessments_id_seq'::regclass)"
"personality_assessments"	"user_id"	"integer"	"NO"	
"personality_assessments"	"assessment_type"	"character varying"	"NO"	
"personality_assessments"	"assessment_version"	"character varying"	"NO"	
"personality_assessments"	"session_id"	"uuid"	"NO"	"gen_random_uuid()"
"personality_assessments"	"status"	"character varying"	"NO"	"'in_progress'::character varying"
"personality_assessments"	"started_at"	"timestamp with time zone"	"NO"	"now()"
"personality_assessments"	"completed_at"	"timestamp with time zone"	"YES"	
"personality_assessments"	"total_items"	"integer"	"YES"	
"personality_assessments"	"completed_items"	"integer"	"YES"	"0"
"personality_assessments"	"validity_flags"	"jsonb"	"YES"	"'{}'::jsonb"
"personality_assessments"	"metadata"	"jsonb"	"YES"	"'{}'::jsonb"
"personality_assessments"	"created_at"	"timestamp with time zone"	"NO"	"now()"
"personality_assessments"	"updated_at"	"timestamp with time zone"	"NO"	"now()"
"personality_embeddings"	"id"	"integer"	"NO"	"nextval('personality_embeddings_id_seq'::regclass)"
"personality_embeddings"	"user_id"	"integer"	"NO"	
"personality_embeddings"	"embedding_type"	"character varying"	"NO"	
"personality_embeddings"	"embedding_vector"	"ARRAY"	"NO"	
"personality_embeddings"	"generation_method"	"character varying"	"NO"	
"personality_embeddings"	"model_version"	"character varying"	"NO"	
"personality_embeddings"	"quality_score"	"double precision"	"YES"	
"personality_embeddings"	"source_data_hash"	"character varying"	"YES"	
"personality_embeddings"	"created_at"	"timestamp with time zone"	"NO"	"now()"
"personality_embeddings"	"updated_at"	"timestamp with time zone"	"NO"	"now()"
"personality_profiles"	"id"	"integer"	"NO"	"nextval('personality_profiles_id_seq'::regclass)"
"personality_profiles"	"user_id"	"integer"	"NO"	
"personality_profiles"	"assessment_id"	"integer"	"YES"	
"personality_profiles"	"profile_type"	"character varying"	"NO"	
"personality_profiles"	"language"	"character varying"	"YES"	
"personality_profiles"	"scores"	"jsonb"	"NO"	
"personality_profiles"	"confidence_intervals"	"jsonb"	"YES"	
"personality_profiles"	"reliability_estimates"	"jsonb"	"YES"	
"personality_profiles"	"percentile_ranks"	"jsonb"	"YES"	
"personality_profiles"	"narrative_description"	"text"	"YES"	
"personality_profiles"	"assessment_version"	"character varying"	"NO"	
"personality_profiles"	"computed_at"	"timestamp with time zone"	"NO"	"now()"
"personality_profiles"	"expires_at"	"timestamp with time zone"	"YES"	
"personality_profiles"	"created_at"	"timestamp with time zone"	"NO"	"now()"
"personality_profiles"	"updated_at"	"timestamp with time zone"	"NO"	"now()"
"personality_responses"	"id"	"integer"	"NO"	"nextval('personality_responses_id_seq'::regclass)"
"personality_responses"	"assessment_id"	"integer"	"NO"	
"personality_responses"	"item_id"	"character varying"	"NO"	
"personality_responses"	"item_type"	"character varying"	"NO"	
"personality_responses"	"response_value"	"jsonb"	"NO"	
"personality_responses"	"response_time_ms"	"integer"	"YES"	
"personality_responses"	"revision_count"	"integer"	"YES"	"0"
"personality_responses"	"confidence_level"	"integer"	"YES"	
"personality_responses"	"behavioral_metadata"	"jsonb"	"YES"	"'{}'::jsonb"
"personality_responses"	"created_at"	"timestamp with time zone"	"NO"	"now()"
"personality_responses"	"updated_at"	"timestamp with time zone"	"NO"	"now()"
"personality_trends"	"id"	"integer"	"NO"	"nextval('personality_trends_id_seq'::regclass)"
"personality_trends"	"user_id"	"integer"	"NO"	
"personality_trends"	"trait_name"	"character varying"	"NO"	
"personality_trends"	"trend_type"	"character varying"	"NO"	
"personality_trends"	"trend_parameters"	"jsonb"	"NO"	
"personality_trends"	"trend_strength"	"double precision"	"YES"	
"personality_trends"	"time_window_start"	"timestamp with time zone"	"NO"	
"personality_trends"	"time_window_end"	"timestamp with time zone"	"NO"	
"personality_trends"	"computed_at"	"timestamp with time zone"	"NO"	"now()"
"personality_trends"	"created_at"	"timestamp with time zone"	"NO"	"now()"
"public_feed"	"id"	"integer"	"NO"	"nextval('public_feed_id_seq'::regclass)"
"public_feed"	"event_type"	"character varying"	"NO"	
"public_feed"	"domain"	"character varying"	"YES"	
"public_feed"	"timestamp"	"timestamp without time zone"	"YES"	"now()"
"saved_recommendations"	"id"	"integer"	"NO"	"nextval('saved_recommendations_id_seq'::regclass)"
"saved_recommendations"	"user_id"	"integer"	"NO"	
"saved_recommendations"	"oasis_code"	"character varying"	"NO"	
"saved_recommendations"	"label"	"character varying"	"NO"	
"saved_recommendations"	"description"	"text"	"YES"	
"saved_recommendations"	"main_duties"	"text"	"YES"	
"saved_recommendations"	"role_creativity"	"double precision"	"YES"	
"saved_recommendations"	"role_leadership"	"double precision"	"YES"	
"saved_recommendations"	"role_digital_literacy"	"double precision"	"YES"	
"saved_recommendations"	"role_critical_thinking"	"double precision"	"YES"	
"saved_recommendations"	"role_problem_solving"	"double precision"	"YES"	
"saved_recommendations"	"saved_at"	"timestamp with time zone"	"NO"	"now()"
"saved_recommendations"	"analytical_thinking"	"double precision"	"YES"	
"saved_recommendations"	"attention_to_detail"	"double precision"	"YES"	
"saved_recommendations"	"collaboration"	"double precision"	"YES"	
"saved_recommendations"	"adaptability"	"double precision"	"YES"	
"saved_recommendations"	"independence"	"double precision"	"YES"	
"saved_recommendations"	"evaluation"	"double precision"	"YES"	
"saved_recommendations"	"decision_making"	"double precision"	"YES"	
"saved_recommendations"	"stress_tolerance"	"double precision"	"YES"	
"saved_recommendations"	"all_fields"	"json"	"YES"	
"saved_recommendations"	"personal_analysis"	"text"	"YES"	
"saved_recommendations"	"entry_qualifications"	"text"	"YES"	
"saved_recommendations"	"suggested_improvements"	"text"	"YES"	
"skills_to_domains"	"skill_id"	"character varying"	"NO"	
"skills_to_domains"	"domain"	"character varying"	"YES"	
"strengths_reflection_responses"	"id"	"integer"	"NO"	"nextval('strengths_reflection_responses_id_seq'::regclass)"
"strengths_reflection_responses"	"user_id"	"integer"	"NO"	
"strengths_reflection_responses"	"question_id"	"integer"	"NO"	
"strengths_reflection_responses"	"prompt_text"	"text"	"NO"	
"strengths_reflection_responses"	"response"	"text"	"YES"	
"strengths_reflection_responses"	"response_time_ms"	"integer"	"YES"	
"strengths_reflection_responses"	"created_at"	"timestamp with time zone"	"NO"	"now()"
"strengths_reflection_responses"	"updated_at"	"timestamp with time zone"	"NO"	"now()"
"suggested_peers"	"user_id"	"integer"	"NO"	
"suggested_peers"	"suggested_id"	"integer"	"NO"	
"suggested_peers"	"similarity"	"double precision"	"YES"	
"suggested_peers"	"created_at"	"timestamp with time zone"	"YES"	"now()"
"suggested_peers"	"updated_at"	"timestamp with time zone"	"YES"	
"tree_paths"	"id"	"uuid"	"NO"	
"tree_paths"	"user_id"	"integer"	"YES"	
"tree_paths"	"tree_type"	"character varying"	"YES"	
"tree_paths"	"tree_json"	"json"	"YES"	
"tree_paths"	"name"	"character varying"	"YES"	
"tree_paths"	"created_at"	"timestamp without time zone"	"YES"	"now()"
"user_notes"	"id"	"integer"	"NO"	"nextval('user_notes_id_seq'::regclass)"
"user_notes"	"user_id"	"integer"	"NO"	
"user_notes"	"saved_recommendation_id"	"integer"	"YES"	
"user_notes"	"content"	"text"	"NO"	
"user_notes"	"created_at"	"timestamp with time zone"	"NO"	"now()"
"user_notes"	"updated_at"	"timestamp with time zone"	"NO"	"now()"
"user_profiles"	"id"	"integer"	"NO"	"nextval('user_profiles_id_seq'::regclass)"
"user_profiles"	"user_id"	"integer"	"YES"	
"user_profiles"	"favorite_movie"	"character varying"	"YES"	
"user_profiles"	"favorite_book"	"character varying"	"YES"	
"user_profiles"	"favorite_celebrities"	"text"	"YES"	
"user_profiles"	"learning_style"	"character varying"	"YES"	
"user_profiles"	"interests"	"text"	"YES"	
"user_profiles"	"created_at"	"timestamp with time zone"	"YES"	"now()"
"user_profiles"	"updated_at"	"timestamp with time zone"	"YES"	
"user_profiles"	"name"	"character varying"	"YES"	
"user_profiles"	"age"	"integer"	"YES"	
"user_profiles"	"sex"	"character varying"	"YES"	
"user_profiles"	"major"	"character varying"	"YES"	
"user_profiles"	"year"	"integer"	"YES"	
"user_profiles"	"gpa"	"double precision"	"YES"	
"user_profiles"	"hobbies"	"text"	"YES"	
"user_profiles"	"country"	"character varying"	"YES"	
"user_profiles"	"state_province"	"character varying"	"YES"	
"user_profiles"	"unique_quality"	"text"	"YES"	
"user_profiles"	"story"	"text"	"YES"	
"user_profiles"	"job_title"	"character varying"	"YES"	
"user_profiles"	"industry"	"character varying"	"YES"	
"user_profiles"	"years_experience"	"integer"	"YES"	
"user_profiles"	"education_level"	"character varying"	"YES"	
"user_profiles"	"career_goals"	"text"	"YES"	
"user_profiles"	"skills"	"ARRAY"	"YES"	
"user_profiles"	"embedding"	"USER-DEFINED"	"YES"	
"user_profiles"	"personal_analysis"	"text"	"YES"	
"user_profiles"	"oasis_profile"	"text"	"YES"	
"user_profiles"	"oasis_embedding"	"USER-DEFINED"	"YES"	
"user_profiles"	"esco_occupation_profile"	"text"	"YES"	
"user_profiles"	"esco_skillsgroup_profile"	"text"	"YES"	
"user_profiles"	"esco_skill_profile"	"text"	"YES"	
"user_profiles"	"esco_full_profile"	"text"	"YES"	
"user_profiles"	"esco_embedding_occupation"	"USER-DEFINED"	"YES"	
"user_profiles"	"esco_embedding_skillsgroup"	"USER-DEFINED"	"YES"	
"user_profiles"	"esco_embedding_skill"	"USER-DEFINED"	"YES"	
"user_profiles"	"esco_embedding"	"USER-DEFINED"	"YES"	
"user_profiles"	"top3_recommendedjobs"	"character varying"	"YES"	
"user_profiles"	"philosophical_description"	"character varying"	"YES"	
"user_profiles"	"personality_embedding"	"ARRAY"	"YES"	
"user_profiles"	"big_five_embedding"	"ARRAY"	"YES"	
"user_profiles"	"social_emotional_embedding"	"ARRAY"	"YES"	
"user_profiles"	"cognitive_style_embedding"	"ARRAY"	"YES"	
"user_profiles"	"values_embedding"	"ARRAY"	"YES"	
"user_progress"	"id"	"character varying"	"NO"	"gen_random_uuid()"
"user_progress"	"user_id"	"integer"	"YES"	
"user_progress"	"total_xp"	"integer"	"YES"	
"user_progress"	"level"	"integer"	"YES"	
"user_progress"	"last_completed_node"	"character varying"	"YES"	
"user_progress"	"completed_actions"	"json"	"YES"	
"user_progress"	"last_updated"	"timestamp without time zone"	"YES"	"now()"
"user_recommendations"	"id"	"integer"	"NO"	"nextval('user_recommendations_id_seq'::regclass)"
"user_recommendations"	"user_id"	"integer"	"YES"	
"user_recommendations"	"oasis_code"	"character varying"	"NO"	
"user_recommendations"	"label"	"character varying"	"NO"	
"user_recommendations"	"swiped_right"	"boolean"	"YES"	"false"
"user_recommendations"	"created_at"	"timestamp with time zone"	"YES"	"now()"
"user_representation"	"id"	"integer"	"NO"	"nextval('user_representation_id_seq'::regclass)"
"user_representation"	"user_id"	"integer"	"NO"	
"user_representation"	"generated_at"	"timestamp with time zone"	"NO"	"now()"
"user_representation"	"source"	"character varying"	"NO"	
"user_representation"	"format_version"	"character varying"	"NO"	"'v1'::character varying"
"user_representation"	"data"	"jsonb"	"NO"	
"user_representation"	"summary"	"text"	"YES"	
"user_representation"	"notes"	"text"	"YES"	
"user_representation"	"avatar_description"	"text"	"YES"	
"user_representation"	"avatar_image_url"	"text"	"YES"	
"user_representation"	"avatar_name"	"text"	"YES"	
"user_skill_graphs"	"id"	"uuid"	"NO"	"gen_random_uuid()"
"user_skill_graphs"	"user_id"	"integer"	"YES"	
"user_skill_graphs"	"root_skill_id"	"character varying"	"NO"	
"user_skill_graphs"	"graph_name"	"text"	"YES"	
"user_skill_graphs"	"created_at"	"timestamp without time zone"	"YES"	"now()"
"user_skill_nodes"	"id"	"integer"	"NO"	"nextval('user_skill_nodes_id_seq'::regclass)"
"user_skill_nodes"	"graph_id"	"uuid"	"YES"	
"user_skill_nodes"	"skill_id"	"character varying"	"NO"	
"user_skill_nodes"	"skill_label"	"text"	"NO"	
"user_skill_nodes"	"challenge"	"text"	"YES"	
"user_skill_nodes"	"xp_reward"	"integer"	"YES"	"10"
"user_skill_nodes"	"visible"	"boolean"	"YES"	"true"
"user_skill_nodes"	"revealed"	"boolean"	"YES"	"false"
"user_skill_nodes"	"state"	"character varying"	"YES"	"'locked'::character varying"
"user_skill_nodes"	"notes"	"text"	"YES"	
"user_skill_nodes"	"unlocked_at"	"timestamp without time zone"	"YES"	
"user_skill_trees"	"id"	"integer"	"NO"	"nextval('user_skill_trees_id_seq'::regclass)"
"user_skill_trees"	"user_id"	"integer"	"YES"	
"user_skill_trees"	"graph_id"	"uuid"	"NO"	
"user_skill_trees"	"tree_data"	"jsonb"	"NO"	
"user_skill_trees"	"created_at"	"timestamp without time zone"	"YES"	"now()"
"user_skills"	"id"	"integer"	"NO"	"nextval('user_skills_id_seq'::regclass)"
"user_skills"	"user_id"	"integer"	"YES"	
"user_skills"	"creativity"	"double precision"	"YES"	
"user_skills"	"leadership"	"double precision"	"YES"	
"user_skills"	"digital_literacy"	"double precision"	"YES"	
"user_skills"	"critical_thinking"	"double precision"	"YES"	
"user_skills"	"problem_solving"	"double precision"	"YES"	
"user_skills"	"last_updated"	"timestamp with time zone"	"YES"	"now()"
"user_skills"	"analytical_thinking"	"double precision"	"YES"	
"user_skills"	"attention_to_detail"	"double precision"	"YES"	
"user_skills"	"collaboration"	"double precision"	"YES"	
"user_skills"	"adaptability"	"double precision"	"YES"	
"user_skills"	"independence"	"double precision"	"YES"	
"user_skills"	"evaluation"	"double precision"	"YES"	
"user_skills"	"decision_making"	"double precision"	"YES"	
"user_skills"	"stress_tolerance"	"double precision"	"YES"	
"users"	"id"	"integer"	"NO"	"nextval('users_id_seq'::regclass)"
"users"	"email"	"character varying"	"NO"	
"users"	"hashed_password"	"character varying"	"NO"	
"users"	"created_at"	"timestamp with time zone"	"YES"	"now()"

_End of Documentation_