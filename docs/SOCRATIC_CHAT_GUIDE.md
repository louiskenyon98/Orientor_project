# Socratic Chat Guide

## Overview

The Socratic Chat feature provides a dual-mode conversational AI experience designed to help students articulate thoughts they don't even know they're thinking. Through two distinct approaches - Socratic questioning and bold challenging - students can explore ideas and develop deeper understanding.

## Two Conversational Modes

### 1. Socratic Guide Mode
- **Purpose**: Help students discover insights through gentle, thoughtful questioning
- **Style**: Patient, exploratory, nurturing
- **Best for**:
  - Deep self-reflection
  - Exploring complex ideas
  - Developing critical thinking
  - Understanding your own assumptions
- **Powered by**: GPT-4

**Example Interaction:**
```
Student: "I think I want to be a software engineer."

Socratic Guide: "That's interesting! What draws you to software engineering? 

I'm curious - when you imagine yourself as a software engineer, what does a typical day look like in your mind? What aspects of that vision excite you most?"
```

### 2. Claude Challenger Mode
- **Purpose**: Push thinking further through direct challenges and provocative questions
- **Style**: Bold, direct, intellectually demanding
- **Best for**:
  - Breaking through mental blocks
  - Challenging assumptions quickly
  - Rapid intellectual growth
  - Getting unstuck from circular thinking
- **Powered by**: Claude 3 Sonnet

**Example Interaction:**
```
Student: "I think I want to be a software engineer."

Claude Challenger: "Everyone thinks they want to be a software engineer these days. But why really? 

Is it the actual work that excites you, or just the salary and prestige? What specific problems are you burning to solve with code? If you can't name them, you might be chasing someone else's dream."
```

## Key Features

### Mode Selection Interface
When starting a chat session, users are presented with clear descriptions of both modes, allowing them to choose based on their current needs and mental state.

### Adaptive Questioning
Both modes adapt their questions based on:
- User profile information
- Career goals
- Previous responses in the conversation
- Detected patterns in thinking

### Educational Psychology Principles

#### Socratic Mode implements:
- **Clarification questions**: "What do you mean when you say...?"
- **Assumption probing**: "What must be true for that to work?"
- **Perspective shifting**: "How might someone who disagrees see this?"
- **Implication exploration**: "If that's true, what follows?"
- **Metacognitive reflection**: "What made you think of that?"

#### Claude Mode implements:
- **Direct challenges**: "That's surface-level. Dig deeper."
- **Precision demands**: "Too vague. Be specific."
- **Boundary pushing**: "You're thinking too small. What if..."
- **Core issue focus**: Cuts straight to the heart of matters

## Technical Implementation

### Backend Architecture
- **Service**: `socratic_chat_service.py`
- **Router**: `socratic_chat.py`
- **Endpoints**:
  - `POST /api/v1/socratic-chat/send` - Send message in selected mode
  - `POST /api/v1/socratic-chat/introduction` - Get mode introduction
  - `GET /api/v1/socratic-chat/modes` - Get available modes info
  - `GET /api/v1/socratic-chat/status` - Check service status

### Frontend Components
- **Main Component**: `SocraticChat.tsx`
- **Page**: `/socratic-chat`
- **Features**:
  - Mode selection cards with detailed descriptions
  - Real-time chat interface
  - Visual distinction between modes (blue vs purple theming)
  - Conversation persistence

### API Integration
- **OpenAI GPT-4**: For Socratic mode responses
- **Anthropic Claude**: For challenger mode responses
- **Environment Variables**:
  - `OPENAI_API_KEY`: For GPT-4 access
  - `CLAUDE_KEY`: For Claude API access

## Usage Guidelines

### When to Use Socratic Mode
- When you need time to think deeply
- When exploring new ideas or concepts
- When you feel uncertain or confused
- When you want to understand your own reasoning better

### When to Use Claude Mode
- When you're stuck in analysis paralysis
- When you need a reality check
- When you want rapid clarity
- When you're ready to be challenged

## Best Practices

1. **Start with Intent**: Choose your mode based on what you need, not what feels comfortable
2. **Be Honest**: Both modes work best with genuine, thoughtful responses
3. **Embrace Discomfort**: Growth happens at the edge of your comfort zone
4. **Reflect on Responses**: Take time to think about the questions asked
5. **Switch Modes**: Don't hesitate to change modes if your needs shift

## Future Enhancements

- Session summaries highlighting key insights
- Progress tracking across conversations
- Integration with career goals and skill development
- Personalized question patterns based on learning style
- Export conversation insights for reflection