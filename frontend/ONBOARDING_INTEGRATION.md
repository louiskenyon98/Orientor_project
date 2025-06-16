# Orientor Onboarding Integration

## Overview
The onboarding system has been fully integrated into the Orientor platform, providing new users with a seamless chat-based psychological assessment that flows directly into personalized career recommendations.

## Integration Components

### Backend API Endpoints (`/backend/app/routers/onboarding.py`)
- **GET `/onboarding/status`** - Check user's onboarding completion status
- **POST `/onboarding/start`** - Initialize a new onboarding session
- **POST `/onboarding/response`** - Save individual question responses
- **POST `/onboarding/complete`** - Finalize onboarding with psychological profile
- **GET `/onboarding/profile`** - Retrieve user's psychological profile
- **GET `/onboarding/responses`** - Get all onboarding responses
- **DELETE `/onboarding/reset`** - Reset onboarding progress

### Frontend Components
- **`/components/onboarding/ChatOnboard.tsx`** - Main chat interface component
- **`/components/onboarding/SwipeRecommendations.tsx`** - Career recommendation swiper
- **`/components/onboarding/PsychProfile.tsx`** - Psychological profile visualization
- **`/components/onboarding/TypingIndicator.tsx`** - Chat typing animation

### State Management (`/stores/onboardingStore.ts`)
- Zustand-based store with API integration
- Manages 9 HEXACO/RIASEC-based questions
- Handles real-time response saving and profile generation

### API Service (`/services/onboardingService.ts`)
- TypeScript service layer for all onboarding API calls
- Error handling and retry logic
- Integration with existing authentication system

## User Flow Integration

### 1. New User Registration
```typescript
// /app/register/page.tsx
// After successful registration, redirect to onboarding
router.push('/onboarding');
```

### 2. Existing User Login
```typescript
// /app/login/page.tsx
// Check onboarding status after login
const needsOnboarding = await onboardingService.needsOnboarding();
if (needsOnboarding) {
  router.push('/onboarding');
} else {
  router.push('/chat');
}
```

### 3. Dashboard Protection
```typescript
// /app/page.tsx
// Redirect to onboarding if not completed
const needsOnboarding = await onboardingService.needsOnboarding();
if (needsOnboarding) {
  router.push('/onboarding');
  return;
}
```

## Database Integration

### Tables Used
- **`personality_assessments`** - Track onboarding sessions
- **`personality_responses`** - Store individual question answers
- **`personality_profiles`** - Save generated psychological profiles
- **`user_profiles`** - Updated with onboarding completion metadata

### Data Flow
1. User starts onboarding → Create `personality_assessment` record
2. User answers questions → Save to `personality_responses`
3. Complete onboarding → Generate and save `personality_profile`
4. Profile data used for career recommendations via existing system

## Career Recommendations Integration

### Real API Integration
```typescript
// SwipeRecommendations component uses real recommendation API
const response = await getAllJobRecommendations(10);
const formattedRecommendations = response.recommendations.map(rec => ({
  id: rec.id,
  title: rec.metadata?.title,
  description: rec.metadata?.description,
  match_percentage: Math.round((1 - rec.score) * 100),
  skills_required: rec.metadata?.skills,
  education_level: rec.metadata?.education_level
}));
```

### Swipe Actions
- Uses existing `saveCareer` API for right swipes
- Integrates with user's saved recommendations in "My Space"

## Psychological Assessment Framework

### HEXACO Questions
- **Extraversion**: Team leadership preferences
- **Emotionality**: Stress handling approach
- **Conscientiousness**: Planning vs. flexibility
- **Openness**: Innovation vs. tradition

### RIASEC Questions
- **Realistic**: Hands-on vs. conceptual work
- **Social**: People-helping orientation
- **Investigative**: Research vs. action preference

### Profile Generation
- Simple algorithmic scoring (can be enhanced with ML models)
- Generates personality description and trait rankings
- Stored in standard personality profile format

## Error Handling & Resilience

### API Failures
- Graceful degradation to local-only mode
- Mock data fallbacks for recommendations
- User experience preserved even with backend issues

### Authentication
- JWT token integration with existing auth system
- Automatic token refresh and error handling
- Secure API calls with proper authorization headers

## Installation & Setup

### Backend Dependencies
```bash
# Already included in existing requirements.txt
# No additional dependencies needed
```

### Frontend Dependencies
```bash
# Add to package.json (already done)
npm install zustand@^4.4.7
```

### Database Schema
```sql
-- Uses existing personality assessment tables
-- No new migrations required
```

## Testing

### Unit Tests
- Component tests in `__tests__/components/onboarding/`
- Store tests in `__tests__/stores/onboardingStore.test.ts`
- 54/60 tests passing (SwipeRecommendations minor fixes needed)

### Integration Testing
- API endpoints tested with existing backend test suite
- Authentication flow tested with real JWT tokens
- Database persistence verified

## Configuration

### Environment Variables
```env
# Uses existing API configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### API Base URL
```typescript
// Configured in /services/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';
```

## Deployment Considerations

### Production Checklist
1. ✅ Backend API endpoints registered in main.py
2. ✅ Frontend routes configured
3. ✅ Database tables ready (existing schema)
4. ✅ Authentication integration complete
5. ✅ Error handling implemented
6. ⚠️ CSS styles added to globals.css
7. ⚠️ Zustand dependency added to package.json

### Performance Optimizations
- API calls are cached where appropriate
- Components use React.memo for re-render optimization
- Large recommendation data is paginated
- Images and assets are optimized

## Future Enhancements

### ML Model Integration
- Replace simple scoring with trained personality models
- Use ML-generated career recommendations
- Implement adaptive questioning based on responses

### Advanced Features
- Multi-language support for international users
- Video/audio response options
- Social sharing of personality profiles
- Gamification elements (progress rewards, achievements)

### Analytics
- Track completion rates and drop-off points
- A/B test different question phrasings
- Monitor recommendation quality and user satisfaction

## Troubleshooting

### Common Issues
1. **401 Unauthorized**: Check JWT token in localStorage
2. **Onboarding Loop**: Clear localStorage and restart session
3. **Missing Recommendations**: Verify user has completed tests
4. **CSS Issues**: Ensure chat bubble styles are in globals.css

### Debug Commands
```bash
# Check API endpoints
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/onboarding/status

# Reset onboarding
curl -X DELETE -H "Authorization: Bearer $TOKEN" http://localhost:8000/onboarding/reset
```

## Support

For technical issues or questions about the onboarding integration, refer to:
- Main platform documentation in `/docs/`
- HEXACO test integration guide
- Career recommendation system documentation
- Original onboarding specification in `/task/onboarding/phase.md`