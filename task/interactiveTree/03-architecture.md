# Interactive Tree Architecture - SPARC Phase 3: System Design

## Architecture Overview

### System Components Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │  Tree View   │  │   Space Tab     │  │  Career Goals    │   │
│  │  Component   │  │   Integration   │  │    Manager       │   │
│  └──────┬───────┘  └────────┬────────┘  └────────┬─────────┘   │
│         │                    │                     │             │
│  ┌──────┴────────────────────┴─────────────────────┴────────┐   │
│  │              Frontend Service Layer                       │   │
│  │  - TreeService  - JobService  - CareerService            │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────┼─────────────────────────────────────┐
│                           │    Backend (FastAPI)                 │
├───────────────────────────┼─────────────────────────────────────┤
│  ┌────────────────────────┴─────────────────────────────────┐   │
│  │                  API Gateway Layer                        │   │
│  │  /trees  /jobs  /career-goals  /programs  /descriptions  │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│  ┌──────────────┐  ┌─────┴──────┐  ┌─────────────────────┐    │
│  │ Tree Service │  │ Job Service │  │ Career Goal Service │    │
│  └──────┬───────┘  └─────┬──────┘  └──────────┬──────────┘    │
│         │                 │                      │               │
│  ┌──────┴─────────────────┴──────────────────────┴─────────┐   │
│  │              Business Logic Layer                        │   │
│  │  - ESCO Integration  - LLM Service  - Recommendation    │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                    Data Layer                                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ PostgreSQL  │  │    Redis     │  │   External APIs       │  │
│  │  - Users    │  │  - Tree Cache│  │   - ESCO API         │  │
│  │  - Jobs     │  │  - Sessions  │  │   - LLM API          │  │
│  │  - Goals    │  │              │  │   - Education API    │  │
│  └─────────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Component Architecture

### 1. Frontend Architecture

#### Tree View Component Structure
```typescript
// Component hierarchy
src/
  components/
    tree/
      EnhancedCompetenceTree/
        index.tsx                    // Main container
        TreeCanvas.tsx              // React Flow canvas
        TreeNode.tsx               // Custom node component
        NodeDetailModal.tsx        // Node interaction modal
        TreeControls.tsx          // Zoom, pan, filter controls
        hooks/
          useTreeGeneration.ts    // Tree generation logic
          useNodeInteraction.ts   // Node click handlers
          useTreePersistence.ts   // Cache management
        utils/
          layoutCalculator.ts     // React Flow layout
          nodeColorMapper.ts      // Color coding logic
          treeDataTransformer.ts  // Data transformation
```

#### Service Layer Architecture
```typescript
// Frontend services structure
interface TreeServiceArchitecture {
  // Core tree operations
  generateFromAnchors(skills: string[]): Promise<TreeData>;
  loadCachedTree(graphId: string): Promise<TreeData | null>;
  saveTreeState(graphId: string, state: TreeState): Promise<void>;
  
  // Node operations
  getNodeDescription(nodeId: string): Promise<NodeDescription>;
  saveJobFromNode(nodeId: string): Promise<SavedJob>;
  exploreRelatedNodes(nodeId: string): Promise<RelatedNodes>;
}

interface JobServiceArchitecture {
  // Job management
  saveJob(jobData: JobSaveRequest): Promise<SavedJob>;
  getSavedJobs(userId: number): Promise<SavedJob[]>;
  removeJob(jobId: number): Promise<void>;
  
  // Job details
  getJobDetails(escoId: string): Promise<JobDetails>;
  getJobSkillRequirements(escoId: string): Promise<Skill[]>;
}

interface CareerServiceArchitecture {
  // Career goal management
  setCareerGoal(jobId: number): Promise<CareerGoal>;
  getActiveGoal(userId: number): Promise<CareerGoal | null>;
  archiveGoal(goalId: number): Promise<void>;
  
  // Educational pathways
  getProgramRecommendations(goalId: number): Promise<Program[]>;
  exploreProgramDetails(programId: string): Promise<ProgramDetails>;
}
```

### 2. Backend Architecture

#### API Route Structure
```python
# FastAPI router organization
app/
  routers/
    trees.py                    # Tree generation and management
    jobs.py                     # Job saving and retrieval
    career_goals.py            # Career goal management
    programs.py                # Educational program recommendations
    descriptions.py            # LLM description generation
    
  services/
    tree/
      generator.py             # Tree generation logic
      esco_integration.py      # ESCO API wrapper
      cache_manager.py         # Tree caching service
    
    job/
      job_manager.py          # Job CRUD operations
      skill_mapper.py         # Skill requirement mapping
    
    career/
      goal_service.py         # Career goal logic
      program_matcher.py      # Program recommendation engine
      
    llm/
      description_generator.py # LLM integration
      prompt_templates.py      # Prompt management
      cache_service.py        # Description caching
```

#### Service Layer Design
```python
# Tree Generation Service
class TreeGenerationService:
    def __init__(self, esco_client: ESCOClient, cache: RedisCache):
        self.esco = esco_client
        self.cache = cache
    
    async def generate_from_anchors(
        self, 
        anchor_skills: List[str],
        user_id: int,
        options: TreeGenerationOptions
    ) -> TreeGenerationResult:
        # Implementation details
        pass
    
    async def _build_hierarchical_structure(
        self,
        esco_data: ESCOGraphData
    ) -> HierarchicalTree:
        # Tree building logic
        pass
    
    async def _apply_user_context(
        self,
        tree: HierarchicalTree,
        user_profile: UserProfile
    ) -> ContextualizedTree:
        # User-specific customization
        pass

# Job Management Service
class JobManagementService:
    def __init__(self, db: Database, events: EventBus):
        self.db = db
        self.events = events
    
    async def save_job_from_tree(
        self,
        job_data: JobSaveRequest,
        user_id: int
    ) -> SavedJob:
        # Save job with validation
        pass
    
    async def notify_space_tab(
        self,
        job: SavedJob
    ) -> None:
        # Event-driven notification
        pass

# Career Goal Service
class CareerGoalService:
    def __init__(
        self,
        db: Database,
        program_matcher: ProgramMatcher,
        notification_service: NotificationService
    ):
        self.db = db
        self.program_matcher = program_matcher
        self.notifier = notification_service
    
    async def set_career_goal(
        self,
        user_id: int,
        job_id: int
    ) -> CareerGoal:
        # Goal setting with side effects
        pass
    
    async def trigger_program_search(
        self,
        goal: CareerGoal
    ) -> List[ProgramRecommendation]:
        # Async program matching
        pass
```

### 3. Database Architecture

#### Enhanced Schema Design
```sql
-- Core tree storage
CREATE TABLE tree_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    anchor_skills JSONB NOT NULL,
    graph_data JSONB NOT NULL,
    generation_options JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP
);

-- Job saving with enhanced metadata
CREATE TABLE saved_jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    esco_id VARCHAR(255) NOT NULL,
    job_title VARCHAR(500) NOT NULL,
    skills_required JSONB,
    discovery_source VARCHAR(50),
    tree_graph_id UUID REFERENCES tree_generations(id),
    relevance_score DECIMAL(3,2),
    saved_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    UNIQUE(user_id, esco_id)
);

-- Career goals with history
CREATE TABLE career_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES saved_jobs(id),
    set_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    previous_goal_id INTEGER REFERENCES career_goals(id),
    notes TEXT,
    target_date DATE,
    progress_metrics JSONB DEFAULT '{}'
);

-- Program recommendations
CREATE TABLE program_recommendations (
    id SERIAL PRIMARY KEY,
    goal_id INTEGER REFERENCES career_goals(id),
    program_name VARCHAR(500) NOT NULL,
    institution VARCHAR(500) NOT NULL,
    institution_type VARCHAR(50),
    program_code VARCHAR(100),
    duration VARCHAR(100),
    admission_requirements JSONB,
    match_score DECIMAL(3,2),
    cost_estimate DECIMAL(10,2),
    location JSONB,
    intake_dates JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- LLM description cache
CREATE TABLE llm_descriptions (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(255) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    node_type VARCHAR(50),
    description TEXT NOT NULL,
    prompt_template VARCHAR(100),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    UNIQUE(node_id, user_id)
);

-- Indexes for performance
CREATE INDEX idx_saved_jobs_user_source ON saved_jobs(user_id, discovery_source);
CREATE INDEX idx_career_goals_user_status ON career_goals(user_id, status);
CREATE INDEX idx_program_recommendations_goal ON program_recommendations(goal_id);
CREATE INDEX idx_llm_descriptions_node_user ON llm_descriptions(node_id, user_id);
CREATE INDEX idx_tree_generations_user_created ON tree_generations(user_id, created_at);
```

### 4. Integration Architecture

#### External Service Integration
```python
# ESCO API Integration
class ESCOIntegration:
    base_url: str = "https://esco.ec.europa.eu/api"
    
    async def get_skill_hierarchy(
        self,
        skill_ids: List[str],
        depth: int = 3
    ) -> ESCOGraphData:
        # API integration with retry logic
        pass
    
    async def get_occupation_details(
        self,
        occupation_id: str
    ) -> OccupationDetails:
        # Occupation data fetching
        pass

# LLM Service Integration
class LLMIntegration:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    async def generate_description(
        self,
        node: TreeNode,
        user_context: UserContext,
        template: PromptTemplate
    ) -> str:
        # LLM API call with context
        pass

# Education Database Integration
class EducationAPIIntegration:
    async def search_programs(
        self,
        keywords: List[str],
        location: str,
        level: str
    ) -> List[EducationProgram]:
        # CEGEP Quebec API integration
        pass
```

#### Caching Architecture
```python
# Redis cache configuration
class CacheArchitecture:
    tree_cache: RedisCache = {
        "namespace": "tree:",
        "ttl": 86400,  # 24 hours
        "serializer": "json"
    }
    
    description_cache: RedisCache = {
        "namespace": "desc:",
        "ttl": 604800,  # 7 days
        "serializer": "text"
    }
    
    session_cache: RedisCache = {
        "namespace": "session:",
        "ttl": 3600,  # 1 hour
        "serializer": "pickle"
    }
```

### 5. Event-Driven Architecture

#### Event Bus Design
```python
# Event definitions
class TreeEvents:
    TREE_GENERATED = "tree.generated"
    NODE_CLICKED = "tree.node.clicked"
    JOB_SAVED = "tree.job.saved"

class CareerEvents:
    GOAL_SET = "career.goal.set"
    GOAL_ACHIEVED = "career.goal.achieved"
    PROGRAM_RECOMMENDED = "career.program.recommended"

# Event handlers
class EventHandlers:
    async def on_job_saved(self, event: JobSavedEvent):
        # Update space tab
        # Track analytics
        # Send notification
        pass
    
    async def on_career_goal_set(self, event: CareerGoalSetEvent):
        # Trigger program search
        # Update user profile
        # Send recommendations
        pass
```

### 6. Security Architecture

#### Authentication & Authorization
```python
# Security middleware
class SecurityArchitecture:
    # JWT token validation
    async def verify_token(token: str) -> TokenPayload:
        pass
    
    # Resource access control
    async def check_tree_access(user_id: int, tree_id: str) -> bool:
        pass
    
    # Rate limiting
    rate_limits = {
        "tree_generation": "5/hour",
        "llm_descriptions": "50/hour",
        "job_saving": "100/day"
    }
```

### 7. Performance Architecture

#### Optimization Strategies
```python
# Performance optimizations
class PerformanceArchitecture:
    # Database query optimization
    query_optimizations = {
        "batch_loading": True,
        "connection_pooling": {
            "min_size": 10,
            "max_size": 50
        },
        "query_timeout": 5000  # ms
    }
    
    # Async processing
    async_tasks = {
        "tree_generation": {
            "queue": "high_priority",
            "timeout": 30000  # ms
        },
        "program_matching": {
            "queue": "low_priority",
            "timeout": 60000  # ms
        }
    }
    
    # Frontend optimizations
    frontend_optimizations = {
        "react_flow": {
            "virtualization": True,
            "lazy_loading": True,
            "max_render_nodes": 100
        },
        "data_fetching": {
            "prefetch": True,
            "cache_first": True,
            "stale_while_revalidate": True
        }
    }
```

### 8. Monitoring & Observability

#### Logging Architecture
```python
# Structured logging
class LoggingArchitecture:
    loggers = {
        "tree_generation": {
            "level": "INFO",
            "format": "json",
            "fields": ["user_id", "duration", "node_count"]
        },
        "api_requests": {
            "level": "INFO",
            "format": "json",
            "fields": ["endpoint", "method", "status", "duration"]
        }
    }
    
    # Metrics collection
    metrics = {
        "tree_generation_time": Histogram(),
        "job_save_count": Counter(),
        "active_career_goals": Gauge(),
        "api_response_time": Histogram()
    }
```

## Deployment Architecture

### Container Structure
```yaml
# Docker composition
services:
  frontend:
    build: ./frontend
    environment:
      - NEXT_PUBLIC_API_URL=${API_URL}
    
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - ESCO_API_KEY=${ESCO_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    
  redis:
    image: redis:alpine
    
  postgres:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
```

## Next Steps
Proceed to SPARC Phase 4: Implementation with TDD approach starting with Priority 1 features.