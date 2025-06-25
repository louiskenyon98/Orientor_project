# Orientator AI API Documentation

## Overview

The Orientator AI API provides endpoints for interacting with an intelligent conversational assistant that helps users explore careers, discover skills, find peers, and navigate their professional journey. The API integrates multiple tools and provides rich, interactive responses.

## Base URL

```
https://api.yourplatform.com/api/orientator
```

## Authentication

All endpoints require authentication using Bearer tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Endpoints

### 1. Send Message to Orientator

**POST** `/message`

Send a message to the Orientator AI and receive an intelligent response with tool-generated components.

#### Request Body

```json
{
  "message": "I want to become a data scientist",
  "conversation_id": 123
}
```

#### Response

```json
{
  "message_id": 456,
  "role": "assistant",
  "content": "I'll help you explore the path to becoming a data scientist. Let me analyze the typical journey and required skills.",
  "components": [
    {
      "id": "comp_123",
      "type": "skill_tree",
      "data": {
        "skills": [
          {"name": "Python", "level": "advanced", "importance": "high"},
          {"name": "Machine Learning", "level": "intermediate", "importance": "high"}
        ],
        "role": "Data Scientist"
      },
      "actions": [
        {
          "type": "save",
          "label": "Save Skills",
          "endpoint": "/api/orientator/save-component",
          "params": {"component_id": "comp_123"}
        }
      ],
      "saved": false,
      "metadata": {
        "tool_source": "esco_skills",
        "generated_at": "2024-01-20T10:30:00Z"
      }
    }
  ],
  "metadata": {
    "tools_invoked": ["esco_skills", "career_tree"],
    "intent": "career_exploration",
    "confidence": 0.95,
    "processing_time_ms": 1250
  },
  "created_at": "2024-01-20T10:30:00Z"
}
```

#### Component Types

- `skill_tree`: Hierarchical skill requirements
- `career_path`: Career progression milestones
- `job_card`: Job recommendations and details
- `peer_card`: Peer matching results
- `test_result`: Personality/interest test results
- `challenge_card`: Skill development challenges
- `save_confirmation`: Confirmation of saved items

### 2. Save Component

**POST** `/save-component`

Save a component from the chat to the user's personal space.

#### Request Body

```json
{
  "component_id": "comp_123",
  "component_type": "skill_tree",
  "component_data": {
    "skills": ["Python", "ML", "Statistics"]
  },
  "source_tool": "esco_skills",
  "conversation_id": 123,
  "note": "Key skills for my target role"
}
```

#### Response

```json
{
  "success": true,
  "saved_item_id": 789,
  "message": "Component saved successfully to My Space"
}
```

### 3. Get User Journey

**GET** `/journey/{user_id}`

Retrieve the aggregated career exploration journey for a user.

#### Path Parameters

- `user_id`: ID of the user (must be the authenticated user)

#### Response

```json
{
  "user_id": 123,
  "journey_stages": [
    {
      "type": "career_exploration",
      "data": {"career": "Data Scientist"},
      "achieved_at": "2024-01-15T10:00:00Z",
      "conversation_id": 123
    }
  ],
  "saved_items_count": 15,
  "tools_used": ["esco_skills", "career_tree", "peer_matching"],
  "career_goals": ["Data Scientist", "ML Engineer"],
  "skill_progression": {
    "Python": {
      "level": "advanced",
      "saved_at": "2024-01-10T10:00:00Z"
    }
  },
  "personality_insights": {
    "hexaco_scores": {
      "openness": 0.8,
      "conscientiousness": 0.75
    }
  },
  "peer_connections": [
    {
      "peer_id": 456,
      "name": "John Doe",
      "match_score": 0.85,
      "saved_at": "2024-01-12T10:00:00Z"
    }
  ],
  "challenges_completed": [
    {
      "challenge_id": 789,
      "title": "Python Basics",
      "xp_earned": 100,
      "completed_at": "2024-01-13T10:00:00Z"
    }
  ]
}
```

### 4. Get Orientator Conversations

**GET** `/conversations`

Retrieve user's conversations that involved Orientator AI interactions.

#### Query Parameters

- `limit` (optional): Number of conversations to return (1-100, default: 20)
- `offset` (optional): Number of conversations to skip (default: 0)

#### Response

```json
[
  {
    "id": 123,
    "title": "Exploring Data Science Careers",
    "created_at": "2024-01-20T10:00:00Z",
    "last_message_at": "2024-01-20T11:30:00Z",
    "message_count": 15,
    "tools_used": ["career_tree", "esco_skills"],
    "is_favorite": true,
    "is_archived": false
  }
]
```

### 5. Get Tool Analytics

**GET** `/tool-analytics`

Retrieve analytics on tool usage for the authenticated user.

#### Response

```json
{
  "total_invocations": 150,
  "tool_usage": {
    "esco_skills": {
      "count": 45,
      "success": 43,
      "success_rate": 0.956,
      "avg_execution_time": 245.5
    },
    "career_tree": {
      "count": 38,
      "success": 37,
      "success_rate": 0.974,
      "avg_execution_time": 320.0
    }
  },
  "success_rate": 0.94,
  "most_used_tools": [
    {"tool": "esco_skills", "count": 45},
    {"tool": "career_tree", "count": 38}
  ]
}
```

### 6. Submit Feedback

**POST** `/feedback`

Submit feedback on an AI response to improve the system.

#### Query Parameters

- `message_id`: ID of the AI message
- `rating` (optional): Rating from 1-5

#### Request Body

```json
{
  "message_id": 456,
  "feedback": "Very helpful response with clear next steps",
  "rating": 5
}
```

#### Response

```json
{
  "success": true,
  "message": "Thank you for your feedback!"
}
```

### 7. Health Check

**GET** `/health`

Check the health status of the Orientator AI service.

#### Response

```json
{
  "status": "healthy",
  "service": "orientator-ai",
  "version": "1.0.0"
}
```

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden

```json
{
  "detail": "Cannot access another user's journey"
}
```

### 404 Not Found

```json
{
  "detail": "Conversation not found or access denied"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "conversation_id"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to process message"
}
```

## Tool Integration

The Orientator AI integrates with the following tools:

1. **ESCO Skills Tree** (`esco_skills`)
   - Provides hierarchical skill requirements for careers
   - Returns skill trees with proficiency levels

2. **Career Tree** (`career_tree`)
   - Maps career progression paths
   - Shows milestones and timeline

3. **OaSIS Job Explorer** (`oasis_explorer`)
   - Recommends related jobs
   - Provides match scores based on user profile

4. **Peer Matching** (`peer_matching`)
   - Finds compatible peers
   - Returns top matches with explanations

5. **HEXACO Test** (`hexaco_test`)
   - Personality assessment
   - Returns personality insights

6. **Holland Test** (`holland_test`)
   - Career interest assessment
   - Returns RIASEC codes

7. **XP Challenges** (`xp_challenges`)
   - Skill development challenges
   - Tracks progress with XP rewards

## Rate Limiting

- 100 requests per minute per user for message endpoints
- 1000 requests per hour for analytics endpoints
- 10 requests per minute for save operations

## Webhooks

The API supports webhooks for the following events:

- `message.processed`: When an Orientator message is processed
- `component.saved`: When a component is saved to My Space
- `milestone.achieved`: When a user achieves a journey milestone

## SDKs and Libraries

Official SDKs are available for:

- JavaScript/TypeScript
- Python
- React (hooks and components)

## Best Practices

1. **Conversation Management**
   - Reuse conversation IDs for related queries
   - Create new conversations for different topics

2. **Component Handling**
   - Save important components immediately
   - Use component metadata for filtering

3. **Error Handling**
   - Implement retry logic for 5xx errors
   - Cache successful responses when appropriate

4. **Performance**
   - Use pagination for conversation lists
   - Batch save operations when possible

## Support

For API support and questions:
- Email: api-support@yourplatform.com
- Documentation: https://docs.yourplatform.com/api/orientator
- Status: https://status.yourplatform.com