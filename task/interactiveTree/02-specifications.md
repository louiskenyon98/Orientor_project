# Interactive Tree Specifications - SPARC Phase 2: Pseudocode & Specifications

## System Overview
Enhanced competency tree system with job saving, career planning, and educational pathway integration. This document defines the complete functional and technical specifications.

## 1. Tree Generation Enhancement (Priority 1)

### Functional Specifications
- **Input**: 5 anchor skills from user profile
- **Process**: Generate ESCO subgraph with skills and occupations
- **Output**: Hierarchical tree structure with proper relationships
- **Error Handling**: Graceful degradation with user feedback

### API Specification
```typescript
// Enhanced tree generation endpoint
POST /api/v1/trees/generate-from-anchors
Request: {
  anchor_skills: string[5], // Exactly 5 ESCO skill IDs
  max_depth: number = 3,
  max_nodes: number = 20,
  include_occupations: boolean = true
}
Response: {
  graph_id: string,
  status: 'success' | 'partial' | 'failed',
  nodes_generated: number,
  edges_generated: number,
  cache_duration: number // seconds
}
```

### Error Handling Pseudocode
```pseudocode
FUNCTION generateTreeFromAnchors(anchorSkills[5]):
  TRY:
    validateAnchorSkills(anchorSkills)
    escoData = fetchESCOSubgraph(anchorSkills)
    treeStructure = buildHierarchicalTree(escoData)
    graphId = cacheTreeData(treeStructure)
    RETURN success(graphId)
  CATCH ValidationError:
    RETURN error("Invalid anchor skills provided")
  CATCH ESCOApiError:
    RETURN error("ESCO service unavailable, try again later")
  CATCH TimeoutError:
    RETURN error("Tree generation timed out, please try with fewer skills")
  CATCH GeneralError:
    RETURN error("Unexpected error occurred")
END FUNCTION
```

## 2. Tree Persistence System (Priority 2)

### Caching Strategy
```typescript
interface TreeCache {
  graph_id: string;
  user_id: number;
  tree_data: CompetenceTreeData;
  created_at: Date;
  expires_at: Date;
  access_count: number;
}
```

### Cache Management Pseudocode
```pseudocode
FUNCTION loadOrGenerateTree(userId, anchorSkills):
  cacheKey = generateCacheKey(userId, anchorSkills)
  
  cachedTree = getCachedTree(cacheKey)
  IF cachedTree AND NOT isExpired(cachedTree):
    incrementAccessCount(cacheKey)
    RETURN cachedTree
  END IF
  
  newTree = generateTreeFromAnchors(anchorSkills)
  storeInCache(cacheKey, newTree, CACHE_DURATION)
  storeInDatabase(userId, newTree)
  RETURN newTree
END FUNCTION
```

### Job Saving Specifications
```typescript
interface SavedJob {
  id: number;
  user_id: number;
  esco_id: string;
  job_title: string;
  skills_required: string[];
  discovery_source: 'anchor_skill_tree' | 'search' | 'recommendation';
  relevance_score: number; // 0.0 to 1.0
  saved_at: Date;
  metadata: {
    tree_graph_id?: string;
    user_context?: string;
    llm_description?: string;
  };
}
```

## 3. Interactive Node System (Priority 3)

### Node Click Handler Specifications
```typescript
interface NodeInteraction {
  node_id: string;
  node_type: 'skill' | 'occupation' | 'skillgroup';
  action: 'view_details' | 'save_job' | 'explore_related';
  timestamp: Date;
  user_context: UserProfile;
}
```

### LLM Description Generation
```pseudocode
FUNCTION generateNodeDescription(node, userProfile):
  prompt = buildContextualPrompt(node, userProfile)
  
  contextTemplate = "
    Based on the user's profile:
    - Skills: {userProfile.skills}
    - Interests: {userProfile.interests}
    - Career goals: {userProfile.career_goals}
    - Personality type: {userProfile.personality_type}
    
    Explain how this {node.type} '{node.title}' relates to their profile.
    Focus on practical connections and career relevance.
    Keep response to 150-200 words.
  "
  
  llmResponse = callLLMService(prompt, contextTemplate)
  
  IF llmResponse.success:
    cacheDescription(node.id, userProfile.id, llmResponse.text)
    RETURN llmResponse.text
  ELSE:
    RETURN getGenericDescription(node.type)
  END IF
END FUNCTION
```

### Modal/Sidebar UI Specifications
```typescript
interface NodeDetailModal {
  isOpen: boolean;
  node: CompetenceNode;
  description: string;
  actions: {
    save_job: boolean;
    explore_related: boolean;
    set_as_goal: boolean;
  };
  position: 'sidebar' | 'modal' | 'overlay';
}
```

## 4. Space Tab Integration (Priority 4)

### Saved Jobs Display Specifications
```typescript
interface SpaceTabData {
  saved_jobs: SavedJob[];
  career_goals: CareerGoal[];
  recommendations: JobRecommendation[];
  progress_tracking: {
    jobs_explored: number;
    skills_mapped: number;
    goals_set: number;
  };
}
```

### Career Goal Management
```pseudocode
FUNCTION setCareerGoal(userId, jobId):
  // Check if user already has active career goal
  existingGoal = getActiveCareerGoal(userId)
  
  IF existingGoal:
    archiveCareerGoal(existingGoal.id)
  END IF
  
  newGoal = createCareerGoal({
    user_id: userId,
    job_id: jobId,
    status: 'active',
    set_at: NOW()
  })
  
  // Trigger educational pathway search
  triggerProgramRecommendations(newGoal.id)
  
  RETURN newGoal
END FUNCTION
```

### API Endpoints Specification
```typescript
// Career Goals Management
POST /api/v1/career-goals
Request: { job_id: number, notes?: string }
Response: { goal_id: number, status: string }

GET /api/v1/career-goals/user/{user_id}
Response: { goals: CareerGoal[], active_goal?: CareerGoal }

PUT /api/v1/career-goals/{goal_id}
Request: { status: 'active' | 'archived', notes?: string }
Response: { success: boolean }

// Job Saving
POST /api/v1/jobs/save
Request: { 
  esco_id: string, 
  source: string, 
  tree_graph_id?: string 
}
Response: { saved_job: SavedJob, already_saved: boolean }
```

## 5. Educational Pathway Integration (Priority 5)

### Program Search Algorithm
```pseudocode
FUNCTION findRelevantPrograms(careerGoal):
  job = getJobDetails(careerGoal.job_id)
  requiredSkills = job.skills_required
  
  // Search CEGEP Quebec database
  programs = searchCEGEPPrograms({
    keywords: [job.title, ...requiredSkills.slice(0, 5)],
    level: ['diploma', 'certificate', 'degree'],
    region: user.location.province
  })
  
  // Calculate match scores
  scoredPrograms = []
  FOR EACH program IN programs:
    matchScore = calculateProgramMatch(program, job)
    IF matchScore > 0.3:
      scoredPrograms.add({
        program: program,
        match_score: matchScore,
        relevance_reasons: explainMatch(program, job)
      })
    END IF
  END FOR
  
  RETURN sortByScore(scoredPrograms).slice(0, 10)
END FUNCTION
```

### Program Recommendation Specifications
```typescript
interface ProgramRecommendation {
  id: number;
  goal_id: number;
  program_name: string;
  institution: string;
  institution_type: 'cegep' | 'university' | 'college';
  duration: string; // e.g., "2 years", "18 months"
  admission_requirements: string[];
  match_score: number; // 0.0 to 1.0
  relevance_explanation: string;
  cost_estimate?: number;
  location: {
    city: string;
    province: string;
    campus_type: 'on_campus' | 'online' | 'hybrid';
  };
  next_intake_date?: Date;
  application_deadline?: Date;
}
```

## 6. Visualization Enhancements (Priority 6)

### React Flow Integration Specifications
```typescript
interface EnhancedTreeNode {
  id: string;
  type: 'skill' | 'occupation' | 'skillgroup';
  position: { x: number; y: number };
  data: {
    label: string;
    description?: string;
    is_anchor: boolean;
    is_saved: boolean;
    relevance_score?: number;
    actions: NodeAction[];
  };
  style: {
    background: string;
    border: string;
    borderRadius: number;
    color: string;
  };
}
```

### Layout Algorithm Specifications
```pseudocode
FUNCTION calculateReactFlowLayout(nodes, edges):
  // Use dagre for hierarchical layout
  graph = new Dagre.Graph()
  graph.setDefaultEdgeLabel(() => ({}))
  graph.setGraph({ 
    rankdir: 'TB',
    nodesep: 150,
    ranksep: 200,
    marginx: 50,
    marginy: 50
  })
  
  // Add nodes with size information
  FOR EACH node IN nodes:
    graph.setNode(node.id, {
      width: node.is_anchor ? 120 : 80,
      height: node.is_anchor ? 120 : 80
    })
  END FOR
  
  // Add edges
  FOR EACH edge IN edges:
    graph.setEdge(edge.source, edge.target)
  END FOR
  
  Dagre.layout(graph)
  
  // Apply positions to nodes
  layoutedNodes = nodes.map(node => ({
    ...node,
    position: graph.node(node.id)
  }))
  
  RETURN { nodes: layoutedNodes, edges: edges }
END FUNCTION
```

### Color Coding Specifications
```typescript
const NODE_COLORS = {
  skill: {
    default: '#3B82F6', // Blue
    saved: '#10B981',   // Green
    anchor: '#8B5CF6'   // Purple
  },
  occupation: {
    default: '#10B981', // Green
    saved: '#F59E0B',   // Amber
    goal: '#DC2626'     // Red
  },
  skillgroup: {
    default: '#6B7280', // Gray
    expanded: '#4F46E5' // Indigo
  }
};
```

## 7. Performance Requirements

### Response Time Specifications
- Tree generation: < 5 seconds for standard requests
- Node interactions: < 200ms response time
- LLM description generation: < 3 seconds
- Job saving operations: < 500ms
- Program recommendations: < 2 seconds

### Caching Strategy
```typescript
interface CacheStrategy {
  tree_data: {
    ttl: 24 * 60 * 60, // 24 hours
    storage: 'redis' | 'localStorage',
    invalidation: 'user_profile_change' | 'manual'
  };
  llm_descriptions: {
    ttl: 7 * 24 * 60 * 60, // 7 days
    storage: 'database',
    key_format: 'llm_desc_{node_id}_{user_id_hash}'
  };
  program_data: {
    ttl: 30 * 24 * 60 * 60, // 30 days
    storage: 'database',
    refresh_strategy: 'background_update'
  };
}
```

## 8. Error Handling & Edge Cases

### Error Scenarios
1. **Network failures** during tree generation
2. **ESCO API unavailability** 
3. **Invalid anchor skills** provided
4. **Insufficient user profile data** for LLM descriptions
5. **Program database unavailability**
6. **Concurrent job saving** attempts

### Graceful Degradation
```pseudocode
FUNCTION handleTreeGenerationFailure(error):
  SWITCH error.type:
    CASE 'network_timeout':
      showUserMessage("Generation taking longer than expected...")
      offerRetryOption()
    CASE 'esco_unavailable':
      fallbackToLocalData()
      showLimitedFunctionality()
    CASE 'invalid_skills':
      suggestAlternativeSkills()
      allowManualSelection()
    DEFAULT:
      logError(error)
      showGenericErrorMessage()
  END SWITCH
END FUNCTION
```

## 9. Security Considerations

### Data Protection
- User profile data encryption in transit and at rest
- Career goal data access restricted to user and authorized admins
- LLM API keys secured in environment variables
- Input validation for all user-provided data

### Access Control
```typescript
interface SecurityPolicy {
  tree_access: 'authenticated_users_only';
  job_saving: 'owner_only';
  career_goals: 'owner_and_advisors';
  program_data: 'public_with_rate_limiting';
}
```

## 10. Testing Strategy

### Unit Tests Required
- Tree generation logic
- Job saving/retrieval operations
- Career goal management
- LLM description caching
- Program matching algorithms

### Integration Tests
- End-to-end tree generation flow
- Job saving to space tab integration
- Career goal to program recommendation flow
- React Flow visualization rendering

### Performance Tests
- Tree generation under load
- Concurrent user interactions
- Database query optimization
- Cache hit/miss ratios

## Next Steps
Proceed to SPARC Phase 3: Architecture design to implement these specifications.