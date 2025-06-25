# Product Requirements Document (PRD): Orientator AI Feature

**Spawn a TDD Agents, iterate on unit test until complete.**

## 1. Executive Summary

The Orientator AI is an intelligent conversational assistant that transforms career exploration from passive browsing into an active, personalized journey-building experience. Unlike traditional chatbots, the Orientator autonomously invokes platform tools to provide contextual insights, recommendations, and actionable items directly within the conversation flow, creating a persistent, evolving career roadmap for each user.

## 2. Objectives

### 2.1 Primary Objectives
- **G1** Transform career exploration into a guided, conversational experience
- **G2** Integrate all platform tools seamlessly within chat interactions
- **G3** Enable persistent career journey building through conversation
- **G4** Provide actionable, saveable insights at every interaction point

### 2.2 Success Metrics
- User engagement: 70% of users save at least 3 items per session
- Session continuity: 60% of users return to previous conversations
- Tool utilization: Average 5+ tool invocations per conversation
- Journey completion: 40% of users complete a full career exploration path

## 3. Scope

### 3.1 In Scope
- Conversational AI with autonomous tool invocation
- Interactive message components for tool outputs
- Save functionality for all AI-generated insights
- Multi-session conversation persistence
- Integration with existing tools: ESCO Skills Tree, Career Tree, OaSIS explorer, peer matching, HEXACO/Holland tests
- Extension of existing ChatInterface component

### 3.2 Out of Scope
- Voice/audio interactions
- Real-time collaboration features
- External API integrations beyond existing tools
- Mobile-specific UI (responsive design only)
- Multilingual support (Phase 2)

## 4. User Stories

### 4.1 Core User Stories

**US1: Career Exploration Journey**
```
As a student exploring career options
I want to have a conversation about my interests and skills
So that I receive personalized career recommendations with actionable next steps
```

**US2: Skill Gap Analysis**
```
As a user interested in a specific career
I want the AI to analyze my current skills against job requirements
So that I understand what skills I need to develop
```

**US3: Peer Discovery**
```
As a user on a career journey
I want to discover peers with similar goals or complementary skills
So that I can learn from their experiences
```

**US4: Persistent Journey Building**
```
As a returning user
I want to continue previous conversations and see my saved insights
So that I can build upon my career exploration over time
```

**US5: Personality-Based Guidance**
```
As a user seeking self-understanding
I want to take personality assessments within the chat
So that I receive career guidance aligned with my traits
```

## 5. Functional Requirements

### 5.1 Conversational AI Engine

**FR1.1 Natural Language Understanding**
- Parse user intent from conversational input
- Identify triggers for tool invocation
- Maintain conversation context across messages
- Support follow-up questions and clarifications

**FR1.2 Tool Invocation Logic**
```python
# Trigger patterns for each tool
TOOL_TRIGGERS = {
    "esco_skills": ["skills for", "what skills", "skill requirements"],
    "career_tree": ["career path", "how to become", "steps to"],
    "oasis_explorer": ["jobs like", "similar roles", "explore careers"],
    "peer_matching": ["find peers", "connect with", "others like me"],
    "hexaco_test": ["personality test", "my traits", "hexaco"],
    "holland_test": ["holland code", "career interests", "riasec"],
    "xp_challenges": ["challenges", "practice", "improve skills"]
}
```

**FR1.3 Response Generation**
- Generate contextual responses incorporating tool outputs
- Provide explanations for tool invocations
- Suggest follow-up actions based on results

### 5.2 Tool Integration

**FR2.1 ESCO Skills Tree Integration**
- Input: Career/job title or description
- Output: Hierarchical skill requirements with proficiency levels
- Saveable: Individual skills or entire skill tree

**FR2.2 Career Tree Integration**
- Input: User profile + career goal
- Output: Visual career progression path
- Saveable: Complete path or individual milestones

**FR2.3 OaSIS Job Explorer**
- Input: Skills, interests, or job titles
- Output: Related job recommendations with match scores
- Saveable: Individual job cards with analysis

**FR2.4 Peer Matching**
- Input: User profile + current goals
- Output: Top 5 compatible peers with explanations
- Saveable: Peer profiles for future connection

**FR2.5 Personality Tests**
- Input: Test initiation request
- Output: Interactive test interface + results analysis
- Saveable: Complete results with career implications

**FR2.6 XP Challenges**
- Input: Skill to improve or career goal
- Output: Actionable challenges with XP rewards
- Saveable: Challenge cards for tracking

### 5.3 Message Components

**FR3.1 Component Types**
```typescript
enum MessageComponentType {
  TEXT = "text",
  SKILL_TREE = "skill_tree",
  CAREER_PATH = "career_path",
  JOB_CARD = "job_card",
  PEER_CARD = "peer_card",
  TEST_RESULT = "test_result",
  CHALLENGE_CARD = "challenge_card",
  SAVE_CONFIRMATION = "save_confirmation"
}

interface MessageComponent {
  type: MessageComponentType;
  data: any;
  actions: MessageAction[];
  metadata: {
    tool_source: string;
    generated_at: string;
    relevance_score?: number;
  };
}
```

**FR3.2 Interactive Actions**
- Save to My Space
- Expand/Collapse details
- Request more information
- Share with peers
- Start related action (e.g., take test, accept challenge)

### 5.4 Data Persistence

**FR4.1 Conversation Persistence**
- Store all conversations with full context
- Maintain tool invocation history
- Track saved items per conversation
- Support conversation search and filtering

**FR4.2 Saved Items Management**
```sql
-- Extended saved_recommendations table
ALTER TABLE saved_recommendations ADD COLUMN IF NOT EXISTS (
  source_tool VARCHAR(50),
  conversation_id INTEGER REFERENCES conversations(id),
  component_type VARCHAR(50),
  component_data JSONB,
  interaction_metadata JSONB
);
```

**FR4.3 User Journey Tracking**
- Aggregate saved items into coherent journey
- Track progress on challenges and goals
- Generate journey summaries and insights

## 6. UI/UX Guidelines

### 6.1 Chat Interface Extension

**Reuse Existing Components:**
- Base: `ChatInterface.tsx` structure and styling
- Messages: Extend `ChatMessage.tsx` for rich content
- Sidebar: Maintain conversation list functionality

**New Components Required:**
```typescript
// Component structure
components/
  chat/
    ChatInterface.tsx          // Extended
    MessageComponent.tsx       // New: Renders tool outputs
    ToolInvocationLoader.tsx   // New: Shows tool processing
    SaveActionButton.tsx       // New: Unified save action
    
  orientator/
    SkillTreeMessage.tsx      // Tool-specific renderers
    CareerPathMessage.tsx
    JobCardMessage.tsx
    PeerCardMessage.tsx
    TestResultMessage.tsx
    ChallengeCardMessage.tsx
```

### 6.2 Visual Design Patterns

**Message Flow:**
```
User: "I want to become a data scientist"
  |
  v
[AI Thinking Indicator - Invoking Career Tree...]
  |
  v
AI: "I'll help you explore the path to becoming a data scientist. 
    Let me analyze the typical journey:"
  |
  v
[Interactive Career Path Component]
  - Visual timeline with milestones
  - Required skills at each stage
  - Estimated timeframes
  - [Save Path] [Explore Skills] [Find Mentors]
```

**Component Styling:**
- Maintain existing chat aesthetic
- Tool outputs in subtle bordered containers
- Clear visual hierarchy with proper spacing
- Consistent action button placement
- Loading states for tool invocations

### 6.3 Interaction Patterns

**Tool Invocation Flow:**
1. User message triggers tool need
2. AI explains what it's doing
3. Loading indicator during processing
4. Results presented with context
5. Clear next actions offered

**Save Flow:**
1. One-click save from any component
2. Visual confirmation in chat
3. Optional: Add note during save
4. Link to view in My Space

## 7. Technical Architecture

### 7.1 Backend Architecture

**Service Layer Extension:**
```python
# backend/app/services/orientator_ai_service.py
class OrientatorAIService:
    def __init__(self):
        self.llm_client = OpenAI()
        self.tool_registry = ToolRegistry()
        
    async def process_message(
        self, 
        user_id: int, 
        message: str, 
        conversation_id: int,
        db: Session
    ) -> OrientatorResponse:
        # 1. Analyze intent
        intent = await self.analyze_intent(message)
        
        # 2. Determine tool invocations
        tools_to_invoke = self.determine_tools(intent)
        
        # 3. Execute tools
        tool_results = await self.execute_tools(tools_to_invoke, user_id, db)
        
        # 4. Generate response with components
        response = await self.generate_response(
            message, intent, tool_results
        )
        
        # 5. Store in database
        await self.store_message_with_components(
            conversation_id, response, db
        )
        
        return response
```

**Tool Registry Pattern:**
```python
# backend/app/services/tool_registry.py
class ToolRegistry:
    def __init__(self):
        self.tools = {
            "esco_skills": ESCOSkillsTool(),
            "career_tree": CareerTreeTool(),
            "oasis_explorer": OASISExplorerTool(),
            "peer_matching": PeerMatchingTool(),
            "hexaco_test": HEXACOTestTool(),
            "holland_test": HollandTestTool(),
            "xp_challenges": XPChallengesTool()
        }
    
    async def invoke(
        self, 
        tool_name: str, 
        params: Dict[str, Any],
        user_id: int,
        db: Session
    ) -> ToolResult:
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await tool.execute(params, user_id, db)
```

### 7.2 API Endpoints

**New Endpoints:**
```python
# backend/app/routers/orientator.py

@router.post("/orientator/message")
async def send_orientator_message(
    request: OrientatorMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrientatorMessageResponse:
    """Process a message with Orientator AI"""
    
@router.post("/orientator/save-component")
async def save_component(
    request: SaveComponentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SaveComponentResponse:
    """Save a component from chat to My Space"""
    
@router.get("/orientator/journey/{user_id}")
async def get_user_journey(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserJourneyResponse:
    """Get aggregated user journey from all conversations"""
```

### 7.3 Database Schema Updates

```sql
-- Message components storage
CREATE TABLE message_components (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES chat_messages(id),
    component_type VARCHAR(50) NOT NULL,
    component_data JSONB NOT NULL,
    tool_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tool invocation tracking
CREATE TABLE tool_invocations (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    tool_name VARCHAR(50) NOT NULL,
    input_params JSONB,
    output_data JSONB,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Journey milestones
CREATE TABLE user_journey_milestones (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    milestone_type VARCHAR(50),
    milestone_data JSONB,
    achieved_at TIMESTAMP,
    conversation_id INTEGER REFERENCES conversations(id)
);
```

### 7.4 Message Format Design

```typescript
// Extended message format
interface OrientatorMessage {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  components?: MessageComponent[];
  metadata?: {
    tools_invoked?: string[];
    processing_time_ms?: number;
    confidence_score?: number;
  };
  created_at: string;
}

// Component rendering
interface MessageComponent {
  id: string;
  type: MessageComponentType;
  data: ComponentData;
  actions: ComponentAction[];
  saved?: boolean;
}

interface ComponentAction {
  type: 'save' | 'expand' | 'explore' | 'share' | 'start';
  label: string;
  endpoint?: string;
  params?: Record<string, any>;
}
```

## 8. Implementation Plan

### 8.1 Phase 1: Foundation (Week 1-2)
- Extend ChatInterface component for rich messages
- Implement tool registry and base tool interface
- Create message component rendering system
- Set up database schema updates

### 8.2 Phase 2: Tool Integration (Week 3-4)
- Integrate ESCO Skills Tree tool
- Integrate Career Tree tool
- Integrate OaSIS Explorer tool
- Implement save functionality

### 8.3 Phase 3: Advanced Tools (Week 5-6)
- Integrate peer matching
- Integrate personality tests
- Implement XP challenges
- Add journey aggregation

### 8.4 Phase 4: Polish & Testing (Week 7-8)
- Optimize tool invocation logic
- Enhance UI/UX based on feedback
- Performance optimization
- Comprehensive testing

## 9. Security & Privacy Considerations

### 9.1 Data Security
- All tool invocations logged for audit
- User data isolation in multi-tenant setup
- Encrypted storage for sensitive test results

### 9.2 Privacy Controls
- User consent for personality test data usage
- Opt-in for peer matching visibility
- Data retention policies for conversations

## 10. Performance Requirements

### 10.1 Response Times
- Initial message response: < 500ms
- Tool invocation: < 2s per tool
- Component rendering: < 100ms
- Save action: < 300ms

### 10.2 Scalability
- Support 1000+ concurrent conversations
- Handle 50+ tool invocations per minute
- Message history pagination for long conversations

## 11. Success Criteria

### 11.1 Launch Criteria
- All tools integrated and functional
- Save functionality working across all components
- Multi-session persistence verified
- Performance benchmarks met

### 11.2 Post-Launch Metrics
- User engagement rate > 70%
- Average session duration > 15 minutes
- Tool invocation accuracy > 85%
- Save action usage > 5 per session

## 12. Open Questions & Risks

### 12.1 Open Questions
- Should tool invocations require user confirmation?
- How to handle multiple tool invocations in one response?
- Optimal context window for conversation history?

### 12.2 Risks
- **R1** LLM hallucination in tool selection - Mitigation: Strict intent matching
- **R2** Performance degradation with many components - Mitigation: Lazy loading
- **R3** User overwhelm with too many options - Mitigation: Progressive disclosure

## 13. References

### 13.1 Codebase References
- `frontend/src/components/chat/ChatInterface.tsx:1-600` - Base chat implementation
- `backend/app/services/enhanced_chat_service.py:1-150` - GraphSAGE integration pattern
- `