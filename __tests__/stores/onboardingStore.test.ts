import { useOnboardingStore } from '../../stores/onboardingStore';
import { act, renderHook } from '@testing-library/react';

describe('onboardingStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    act(() => {
      useOnboardingStore.getState().reset();
    });
  });

  it('initializes with correct default state', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    expect(result.current.currentQuestionIndex).toBe(0);
    expect(result.current.responses).toHaveLength(0);
    expect(result.current.messages).toHaveLength(1); // Welcome message
    expect(result.current.isTyping).toBe(false);
    expect(result.current.isComplete).toBe(false);
    expect(result.current.psychProfile).toBeUndefined();
    expect(result.current.messages[0].content).toBe('Hey');
  });

  it('adds messages correctly', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    act(() => {
      result.current.addMessage({
        type: 'user',
        content: 'Test message'
      });
    });
    
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1].type).toBe('user');
    expect(result.current.messages[1].content).toBe('Test message');
    expect(result.current.messages[1].id).toBeDefined();
    expect(result.current.messages[1].timestamp).toBeInstanceOf(Date);
  });

  it('adds responses correctly', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    act(() => {
      result.current.addResponse({
        questionId: 'test-q1',
        question: 'Test question?',
        response: 'Test answer'
      });
    });
    
    expect(result.current.responses).toHaveLength(1);
    expect(result.current.responses[0].questionId).toBe('test-q1');
    expect(result.current.responses[0].question).toBe('Test question?');
    expect(result.current.responses[0].response).toBe('Test answer');
    expect(result.current.responses[0].timestamp).toBeInstanceOf(Date);
  });

  it('advances to next question', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    expect(result.current.currentQuestionIndex).toBe(0);
    
    act(() => {
      result.current.nextQuestion();
    });
    
    expect(result.current.currentQuestionIndex).toBe(1);
  });

  it('completes onboarding when reaching last question', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    // Move to last question index (there are 9 questions total, 0-indexed)
    act(() => {
      // Set to second-to-last question (index 7)
      for (let i = 0; i < 8; i++) {
        result.current.nextQuestion();
      }
    });
    
    expect(result.current.isComplete).toBe(false);
    
    // Move beyond last question - should trigger completion
    act(() => {
      result.current.nextQuestion();
    });
    
    expect(result.current.isComplete).toBe(true);
  });

  it('sets typing state correctly', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    act(() => {
      result.current.setTyping(true);
    });
    
    expect(result.current.isTyping).toBe(true);
    
    act(() => {
      result.current.setTyping(false);
    });
    
    expect(result.current.isTyping).toBe(false);
  });

  it('sets psychological profile correctly', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    const mockProfile = {
      hexaco: { extraversion: 80 },
      riasec: { artistic: 90 },
      topTraits: ['Creative'],
      description: 'Test profile'
    };
    
    act(() => {
      result.current.setPsychProfile(mockProfile);
    });
    
    expect(result.current.psychProfile).toEqual(mockProfile);
  });

  it('completes onboarding manually', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    expect(result.current.isComplete).toBe(false);
    
    act(() => {
      result.current.complete();
    });
    
    expect(result.current.isComplete).toBe(true);
  });

  it('resets store state', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    // Make some changes
    act(() => {
      result.current.addMessage({ type: 'user', content: 'Test' });
      result.current.addResponse({
        questionId: 'q1',
        question: 'Test?',
        response: 'Answer'
      });
      result.current.nextQuestion();
      result.current.setTyping(true);
    });
    
    // Verify changes were made
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.responses).toHaveLength(1);
    expect(result.current.currentQuestionIndex).toBe(1);
    expect(result.current.isTyping).toBe(true);
    
    // Reset
    act(() => {
      result.current.reset();
    });
    
    // Verify reset to initial state
    expect(result.current.currentQuestionIndex).toBe(0);
    expect(result.current.responses).toHaveLength(0);
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.isTyping).toBe(false);
    expect(result.current.isComplete).toBe(false);
  });

  it('gets current question correctly', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    const currentQuestion = result.current.getCurrentQuestion();
    expect(currentQuestion).toBeDefined();
    expect(currentQuestion?.id).toBe('emotion-1');
    expect(currentQuestion?.text).toBe("What makes you feel most alive?");
    expect(currentQuestion?.type).toBe('emotion');
  });

  it('gets progress percentage correctly', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    // At start (question 0 of 9)
    expect(result.current.getProgress()).toBe(0);
    
    // After one question (question 1 of 9)
    act(() => {
      result.current.nextQuestion();
    });
    
    expect(result.current.getProgress()).toBeGreaterThan(0);
    expect(result.current.getProgress()).toBeLessThan(100);
  });

  it('completes onboarding when reaching beyond questions', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    // Start at index 0, questions are at indices 0-8 (9 total)
    expect(result.current.currentQuestionIndex).toBe(0);
    expect(result.current.isComplete).toBe(false);
    
    // Move through all questions one by one
    for (let i = 0; i < 8; i++) { // Move to index 8 (last question)
      act(() => {
        result.current.nextQuestion();
      });
    }
    
    expect(result.current.currentQuestionIndex).toBe(8);
    expect(result.current.isComplete).toBe(false);
    
    // One more call should trigger completion
    act(() => {
      result.current.nextQuestion();
    });
    
    // Should trigger completion but currentQuestionIndex stays at 8
    expect(result.current.currentQuestionIndex).toBe(8);
    expect(result.current.isComplete).toBe(true);
    expect(result.current.getCurrentQuestion()).not.toBeNull(); // Still returns last question
  });

  it('handles multiple message additions', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    act(() => {
      result.current.addMessage({ type: 'system', content: 'Message 1' });
      result.current.addMessage({ type: 'user', content: 'Message 2' });
      result.current.addMessage({ type: 'system', content: 'Message 3' });
    });
    
    expect(result.current.messages).toHaveLength(4); // Including initial welcome message
    expect(result.current.messages[1].content).toBe('Message 1');
    expect(result.current.messages[2].content).toBe('Message 2');
    expect(result.current.messages[3].content).toBe('Message 3');
  });

  it('generates unique message IDs', () => {
    const { result } = renderHook(() => useOnboardingStore());
    
    act(() => {
      result.current.addMessage({ type: 'user', content: 'Message 1' });
      result.current.addMessage({ type: 'user', content: 'Message 2' });
    });
    
    const ids = result.current.messages.map(msg => msg.id);
    const uniqueIds = [...new Set(ids)];
    
    expect(uniqueIds).toHaveLength(ids.length); // All IDs should be unique
  });
});