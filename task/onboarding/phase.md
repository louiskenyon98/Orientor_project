Build a Next.js onboarding flow for Navigo that:

1. Renders a chat-like interface with:
   - Left-aligned system messages (questions)
   - Right-aligned user responses
   - Progressive disclosure (one question at a time)
   - Clean, minimal styling matching the screenshot

2. Implements a psychological profiling sequence:
   - Start with an emotion-first opener ("What makes you feel most alive?")
   - Follow with 3-4 HEXACO-based questions
   - Include 2-3 RIASEC career interest questions
   - End with a forward-looking question about their ideal future

3. Let the user swipe through recommended careers following the answers he was given. This swipe my way is already implemented, you should use what's existing.

4. Technical requirements:
   - Store responses in state/context
   - Validate responses before progressing
   - Show typing indicators between questions
   - Include "Refresh" and "Finish entry" buttons
   - Responsive design for mobile

5. After completion:
   - Generate a preliminary psychological profile
   - Show user their top 2-3 personality traits
   - Transition to main Navigo experience

File structure: /components/onboarding/ChatOnboard.tsx
Styling: Tailwind CSS to match the provided screenshot
State management: useState or Zustand for response collection