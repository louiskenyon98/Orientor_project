# Orientor Onboarding Flow

A Next.js onboarding flow with a chat-like interface featuring psychological profiling and career recommendations with swipe functionality.

## Features

- **Chat-like Interface**: Progressive disclosure with left-aligned system messages and right-aligned user responses
- **Psychological Profiling**: Based on HEXACO and RIASEC frameworks
- **Career Recommendations**: Swipeable career cards with detailed information
- **Responsive Design**: Mobile-friendly with Tailwind CSS
- **Comprehensive Testing**: Full test suite with Jest and React Testing Library

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Build for production
npm run build
```

## Usage

```tsx
import { ChatOnboard } from './components/onboarding';

function App() {
  const handleOnboardingComplete = (responses) => {
    console.log('Onboarding completed:', responses);
    // Process user responses and psychological profile
  };

  return (
    <ChatOnboard onComplete={handleOnboardingComplete} />
  );
}
```

## Project Structure

```
├── components/
│   └── onboarding/
│       ├── ChatOnboard.tsx        # Main onboarding component
│       ├── TypingIndicator.tsx    # Typing animation
│       ├── PsychProfile.tsx       # Profile visualization
│       ├── SwipeRecommendations.tsx # Career swipe interface
│       └── index.ts               # Export file
├── stores/
│   └── onboardingStore.ts         # Zustand state management
├── types/
│   └── onboarding.ts              # TypeScript types
├── __tests__/                     # Test files
└── pages/
    ├── _app.tsx                   # Next.js app wrapper
    └── index.tsx                  # Demo page
```

## Technologies Used

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Zustand** - State management
- **Jest & React Testing Library** - Testing
- **Lucide React** - Icons

---

## Claude-Flow Installation Guide (Original)

- Step 1. Install Claude Code: ``` npm install -g @anthropic-ai/claude-code ```
- Step 2. Install Claude-Flow ``` npx -y claude-flow@latest --version ```
- Step 3. Run Claude-Flow ``` npx -y claude-flow@latest init --sparc ```
- Step 4. Start the orchestrator ``` npx -y claude-flow@latest sparc "build and test my project" ```