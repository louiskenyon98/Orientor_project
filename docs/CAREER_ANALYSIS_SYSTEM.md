# Psychologically-Targeted Course Analysis System

## Overview

The Career Analysis System is a comprehensive solution that transforms course experiences into actionable career insights through AI-powered psychological profiling. This system implements the requirements from `task/classes/classesAnalysis.md` and provides a complete pipeline from course data collection to career recommendations.

## 🎯 System Objectives

1. **Extract Career Insights**: Transform course experiences into psychological insights that inform career guidance
2. **Targeted LLM Conversations**: Use AI to conduct meaningful conversations that reveal authentic career preferences
3. **ESCO Integration**: Connect insights to established career frameworks and skill categories
4. **Real-time Analysis**: Provide immediate feedback and insights during user interactions
5. **Comprehensive Profiling**: Build detailed psychological profiles that evolve with new data

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Backend API    │    │   AI Services   │
│                 │    │                  │    │                 │
│ • ClassesCard   │◄──►│ • Course Router  │◄──►│ • LLM Service   │
│ • AnalysisChat  │    │ • Analysis Svc   │    │ • ESCO Service  │
│ • Dashboard     │    │ • ESCO Service   │    │ • Embeddings    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  User Interface │    │    Database      │    │  External APIs  │
│                 │    │                  │    │                 │
│ • React/Next.js │    │ • PostgreSQL     │    │ • OpenAI GPT-4  │
│ • TypeScript    │    │ • Course Models  │    │ • ESCO Database │
│ • Tailwind CSS  │    │ • Insights       │    │ • Vector Store  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 Database Schema

### Core Tables

#### `courses`
Primary table for storing course information:
- `id`: Primary key
- `user_id`: Foreign key to users table
- `course_name`: Name of the course
- `course_code`: Course identifier (e.g., "CS 101")
- `semester`, `year`: Time information
- `professor`: Instructor name
- `subject_category`: Auto-categorized (STEM/business/humanities/arts)
- `grade`: Performance indicator
- `description`, `learning_outcomes`: Course details

#### `psychological_insights`
Stores extracted psychological insights from course analysis:
- `insight_type`: Type of insight (cognitive_preference/work_style/subject_affinity)
- `insight_value`: JSON data containing the specific insight
- `confidence_score`: AI confidence in the insight (0.0-1.0)
- `evidence_source`: What led to this insight
- `esco_mapping`: Links to ESCO skill categories

#### `career_signals`
Tracks specific career-relevant skills and aptitudes:
- `signal_type`: Type of signal (analytical_thinking/creative_problem_solving/etc.)
- `strength_score`: Measured strength (0.0-1.0)
- `evidence_source`: Supporting evidence
- `pattern_metadata`: Patterns across courses/time
- `esco_skill_mapping`: Connection to ESCO frameworks

#### `conversation_logs`
Records of AI-powered conversations:
- `session_id`: Groups related conversations
- `question_intent`: Purpose of the question
- `question_text`, `response`: Conversation data
- `extracted_insights`: Insights discovered from this exchange
- `sentiment_analysis`: Emotional indicators
- `career_implications`: Direct career guidance

#### `career_profile_aggregates`
Aggregated profiles for different time periods:
- `aggregate_type`: semester/yearly/overall
- `cognitive_preferences`: Thinking style patterns
- `work_style_preferences`: Collaboration and environment preferences
- `subject_affinities`: Authentic vs. forced interests
- `esco_path_suggestions`: Personalized career paths

## 🔌 API Endpoints

### Course Management
- `POST /api/v1/courses` - Create course with auto-categorization
- `GET /api/v1/courses` - List user courses with filtering
- `GET /api/v1/courses/{id}` - Get specific course
- `PUT /api/v1/courses/{id}` - Update course information
- `DELETE /api/v1/courses/{id}` - Remove course and related data

### Career Analysis
- `POST /api/v1/courses/{id}/targeted-analysis` - Start AI conversation
- `POST /api/v1/conversations/{session_id}/respond` - Process user responses
- `GET /api/v1/conversations/{session_id}/summary` - Get session summary

### Psychological Profiling
- `GET /api/v1/psychological-profile/{user_id}` - Complete psychological profile
- `GET /api/v1/career-signals/{user_id}` - Career signals and patterns
- `GET /api/v1/courses/{id}/insights` - Course-specific insights

## 🧠 AI Integration

### LLM Service Architecture

The `LLMCourseService` provides sophisticated conversation management:

1. **Question Generation**: Creates targeted questions based on:
   - Course performance data
   - User's academic history
   - Previous insights discovered
   - Specific psychological constructs

2. **Response Analysis**: Processes user responses to extract:
   - Cognitive preferences (analytical vs. creative thinking)
   - Work style preferences (collaborative vs. independent)
   - Authentic interests vs. external pressures
   - Career-relevant skills and aptitudes

3. **Insight Extraction**: Maps responses to:
   - Psychological constructs
   - ESCO skill categories
   - Career path indicators
   - Development opportunities

### Question Framework Examples

**Cognitive Style Assessment**:
```
"You struggled with calculus but excelled in statistics - what felt different 
about solving those problems compared to your other math courses?"
```

**Work Environment Preferences**:
```
"Your group project grade was lower than your individual assignments - 
do you prefer working independently or is there something specific about 
group dynamics that affects your performance?"
```

**Interest Authenticity**:
```
"Your marketing grade is high but you mentioned finding the subject boring - 
what specifically engages or disengages you about marketing concepts?"
```

## 🌐 Frontend Components

### Enhanced Classes Card
Replaces the basic ClassesCard with career-focused features:
- Shows course performance with career readiness scores
- Displays analysis status and insight counts
- Prompts for career analysis on unanalyzed courses
- Integrates with conversation interface

### Career Analysis Chat
Interactive conversation interface featuring:
- Real-time AI question generation
- Insight discovery notifications
- Progress tracking and session management
- Summary and recommendations display

### Career Insights Dashboard
Comprehensive view of psychological profile:
- Cognitive preferences visualization
- Work style indicators
- Subject affinity patterns
- Career readiness metrics
- ESCO career path recommendations
- Timeline of insight evolution

## 🔗 ESCO Integration

### Skill Mapping
The system maps psychological insights to ESCO categories:

```javascript
const SIGNAL_TO_ESCO_MAPPING = {
  "analytical_thinking": {
    "esco_categories": ["S1.1.1", "S1.2.1", "S1.3.1"],
    "skill_groups": ["analytical skills", "critical thinking"],
    "related_occupations": ["data analyst", "research scientist"]
  },
  // ... more mappings
}
```

### Career Path Generation
- **Entry Points**: Personalized starting points in ESCO tree
- **Traversal Paths**: Guided exploration based on psychological profile
- **Skill Development**: Targeted recommendations for career advancement
- **Market Alignment**: Connect personal insights to industry demands

## 💡 Key Features

### Psychological Constructs Measured
1. **Cognitive Preferences**
   - Analytical vs. creative thinking
   - Concrete vs. abstract processing
   - Detail-oriented vs. big-picture thinking
   - Problem-solving approaches

2. **Work Style Preferences**
   - Individual vs. collaborative work
   - Structured vs. flexible environments
   - Autonomous vs. guided work
   - Fast-paced vs. methodical approaches

3. **Authentic Interests**
   - Genuine engagement vs. external pressure
   - Intrinsic vs. extrinsic motivation
   - Natural aptitudes vs. learned skills
   - Subject-specific affinities

### Career Signal Types
- `analytical_thinking`: Data analysis and logical reasoning
- `creative_problem_solving`: Innovation and design thinking
- `interpersonal_skills`: Communication and relationship building
- `leadership_potential`: Team management and strategic thinking
- `attention_to_detail`: Precision and quality focus
- `stress_tolerance`: Resilience and adaptability

## 🚀 Implementation Workflow

### 1. Course Registration
User adds courses to their profile, triggering automatic subject categorization

### 2. Analysis Invitation
System identifies courses that could benefit from career analysis

### 3. Targeted Conversation
AI conducts structured conversation to extract insights:
- Generates contextual questions
- Processes responses in real-time
- Discovers psychological patterns
- Maps to career frameworks

### 4. Profile Building
System aggregates insights across courses to build comprehensive profile

### 5. Career Guidance
Provides personalized recommendations:
- Career path suggestions
- Skill development areas
- ESCO tree exploration points
- Industry alignment analysis

## 🛡️ Security & Privacy

### Data Protection
- All psychological insights are user-owned and private
- Conversations are encrypted and stored securely
- GDPR-compliant data handling and deletion
- No sharing of personal insights without explicit consent

### AI Safety
- Multiple validation layers for AI-generated insights
- Confidence scoring for all psychological assessments
- Human oversight capabilities for sensitive insights
- Bias detection and mitigation strategies

## 📈 Performance Considerations

### Scalability
- Modular service architecture for independent scaling
- Caching strategies for frequently accessed insights
- Asynchronous processing for AI operations
- Database optimization for complex queries

### AI Efficiency
- Prompt optimization for consistent results
- Response caching for similar conversation patterns
- Batch processing for insight aggregation
- Fallback mechanisms when AI services are unavailable

## 🔮 Future Enhancements

### Advanced Analytics
- Longitudinal studies of career development
- Predictive modeling for career success
- Peer comparison and benchmarking
- Industry trend integration

### Enhanced AI Capabilities
- Multi-modal analysis (text, voice, behavior)
- Real-time emotion detection
- Personalized learning path optimization
- Automated career coaching

### Extended Integrations
- Job market data integration
- Salary and compensation analysis
- Skills gap identification
- Professional network recommendations

## 📋 Testing Strategy

### Unit Testing
- Service layer business logic
- AI prompt generation and parsing
- Database model relationships
- ESCO mapping algorithms

### Integration Testing
- API endpoint functionality
- Database transaction integrity
- AI service interactions
- Frontend-backend communication

### End-to-End Testing
- Complete conversation flows
- Insight discovery workflows
- Profile building processes
- Career recommendation generation

## 🚀 Deployment

### Database Migrations
Run the Alembic migration to create new tables:
```bash
alembic upgrade head
```

### Environment Variables
Required configuration:
```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_postgres_connection_string
```

### Frontend Dependencies
The frontend components require:
- React 18+
- Next.js 13+ (App Router)
- TypeScript
- Tailwind CSS
- Lucide React (icons)

### Backend Dependencies
- FastAPI
- SQLAlchemy
- Alembic
- OpenAI Python client
- Pydantic v2

## 📞 Support & Maintenance

### Monitoring
- Track conversation completion rates
- Monitor AI service performance
- Analyze insight accuracy and user satisfaction
- Database performance optimization

### Maintenance Tasks
- Regular model retraining based on user feedback
- ESCO database updates and mapping refinements
- Performance optimization and caching improvements
- Security audits and compliance reviews

---

**Created**: June 16, 2024  
**Version**: 1.0  
**Authors**: SPARC Development Team  
**Status**: Production Ready

For technical support or questions, please refer to the API documentation at `/docs` when the system is running.