import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatOnboard from '../../../components/onboarding/ChatOnboard';
import { useOnboardingStore } from '../../../stores/onboardingStore';

// Mock the store
jest.mock('../../../stores/onboardingStore');

const mockStore = {
  messages: [
    {
      id: 'welcome',
      type: 'system' as const,
      content: 'Hey',
      timestamp: new Date()
    }
  ],
  responses: [],
  currentQuestionIndex: 0,
  isTyping: false,
  isComplete: false,
  psychProfile: undefined,
  addMessage: jest.fn(),
  addResponse: jest.fn(),
  nextQuestion: jest.fn(),
  setTyping: jest.fn(),
  reset: jest.fn(),
  getCurrentQuestion: jest.fn(() => ({
    id: 'emotion-1',
    text: "What makes you feel most alive?",
    type: 'emotion' as const
  })),
  getProgress: jest.fn(() => 0)
};

beforeEach(() => {
  (useOnboardingStore as jest.Mock).mockReturnValue(mockStore);
  jest.clearAllMocks();
});

describe('ChatOnboard Component', () => {
  it('renders welcome message', () => {
    render(<ChatOnboard />);
    expect(screen.getByText('Hey')).toBeInTheDocument();
  });

  it('displays progress bar', () => {
    render(<ChatOnboard />);
    expect(screen.getByText('0% complete')).toBeInTheDocument();
  });

  it('shows refresh button', () => {
    render(<ChatOnboard />);
    const refreshButton = screen.getByTitle('Refresh and start over');
    expect(refreshButton).toBeInTheDocument();
  });

  it('renders input field with placeholder', () => {
    render(<ChatOnboard />);
    expect(screen.getByPlaceholderText('Write here..')).toBeInTheDocument();
  });

  it('handles text input', async () => {
    const user = userEvent.setup();
    render(<ChatOnboard />);
    
    const textarea = screen.getByPlaceholderText('Write here..');
    await user.type(textarea, 'Test response');
    
    expect(textarea).toHaveValue('Test response');
  });

  it('submits response on form submission', async () => {
    const user = userEvent.setup();
    render(<ChatOnboard />);
    
    const textarea = screen.getByPlaceholderText('Write here..');
    const submitButton = screen.getByRole('button', { name: /send message/i });
    
    await user.type(textarea, 'Test response');
    await user.click(submitButton);
    
    expect(mockStore.addMessage).toHaveBeenCalledWith({
      type: 'user',
      content: 'Test response'
    });
    
    expect(mockStore.addResponse).toHaveBeenCalledWith({
      questionId: 'emotion-1',
      question: "What makes you feel most alive?",
      response: 'Test response'
    });
  });

  it('submits response on Enter key press', async () => {
    const user = userEvent.setup();
    render(<ChatOnboard />);
    
    const textarea = screen.getByPlaceholderText('Write here..');
    
    await user.type(textarea, 'Test response');
    await user.keyboard('{Enter}');
    
    expect(mockStore.addMessage).toHaveBeenCalled();
  });

  it('does not submit empty responses', async () => {
    const user = userEvent.setup();
    render(<ChatOnboard />);
    
    const submitButton = screen.getByRole('button', { name: /send message/i });
    await user.click(submitButton);
    
    expect(mockStore.addMessage).not.toHaveBeenCalled();
  });

  it('shows typing indicator when isTyping is true', () => {
    (useOnboardingStore as jest.Mock).mockReturnValue({
      ...mockStore,
      isTyping: true
    });
    
    render(<ChatOnboard />);
    expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
  });

  it('shows finish button when onboarding is complete', () => {
    (useOnboardingStore as jest.Mock).mockReturnValue({
      ...mockStore,
      isComplete: true,
      psychProfile: {
        hexaco: { extraversion: 80 },
        riasec: { artistic: 90 },
        topTraits: ['Creative'],
        description: 'Test profile'
      }
    });
    
    render(<ChatOnboard />);
    expect(screen.getByText('Finish entry')).toBeInTheDocument();
  });

  it('calls onComplete callback when onboarding finishes', () => {
    const onComplete = jest.fn();
    const responses = [{ questionId: '1', question: 'Test', response: 'Answer', timestamp: new Date() }];
    
    (useOnboardingStore as jest.Mock).mockReturnValue({
      ...mockStore,
      isComplete: true,
      responses,
      psychProfile: {
        hexaco: { extraversion: 80 },
        riasec: { artistic: 90 },
        topTraits: ['Creative'],
        description: 'Test profile'
      }
    });
    
    render(<ChatOnboard onComplete={onComplete} />);
    
    // onComplete should be called when the component detects completion
    waitFor(() => {
      expect(onComplete).toHaveBeenCalledWith(responses);
    });
  });

  it('handles refresh confirmation', async () => {
    const user = userEvent.setup();
    
    // Mock window.confirm
    const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
    
    render(<ChatOnboard />);
    
    const refreshButton = screen.getByTitle('Refresh and start over');
    await user.click(refreshButton);
    
    expect(confirmSpy).toHaveBeenCalledWith(
      'Are you sure you want to start over? This will clear all your responses.'
    );
    expect(mockStore.reset).toHaveBeenCalled();
    
    confirmSpy.mockRestore();
  });

  it('disables input when typing', () => {
    (useOnboardingStore as jest.Mock).mockReturnValue({
      ...mockStore,
      isTyping: true
    });
    
    render(<ChatOnboard />);
    
    const textarea = screen.getByPlaceholderText('Write here..');
    expect(textarea).toBeDisabled();
  });

  it('updates progress bar correctly', () => {
    (useOnboardingStore as jest.Mock).mockReturnValue({
      ...mockStore,
      getProgress: jest.fn(() => 50)
    });
    
    render(<ChatOnboard />);
    expect(screen.getByText('50% complete')).toBeInTheDocument();
  });

  it('renders custom className', () => {
    const { container } = render(<ChatOnboard className="custom-class" />);
    expect(container.firstChild).toHaveClass('custom-class');
  });
});