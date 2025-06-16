import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SwipeRecommendations from '../../../components/onboarding/SwipeRecommendations';
import { PsychProfile } from '../../../types/onboarding';

const mockPsychProfile: PsychProfile = {
  hexaco: { extraversion: 80, openness: 90 },
  riasec: { artistic: 85, social: 75 },
  topTraits: ['Creative', 'Social'],
  description: 'Test profile'
};

describe('SwipeRecommendations Component', () => {
  const mockOnComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders first career recommendation', () => {
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    expect(screen.getByText('UX/UI Designer')).toBeInTheDocument();
  });

  it('displays match percentage', () => {
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    expect(screen.getByText('92% match')).toBeInTheDocument();
  });

  it('shows progress indicator', () => {
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    expect(screen.getByText('1 of 5')).toBeInTheDocument();
  });

  it('displays career description', () => {
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    expect(screen.getByText(/Design user-centered digital experiences/)).toBeInTheDocument();
  });

  it('shows required skills', () => {
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    expect(screen.getByText('Design Thinking')).toBeInTheDocument();
    expect(screen.getByText('Prototyping')).toBeInTheDocument();
    expect(screen.getByText('User Research')).toBeInTheDocument();
  });

  it('displays education requirements', () => {
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    expect(screen.getByText(/Bachelor's degree or equivalent experience/)).toBeInTheDocument();
  });

  it('handles right swipe (save) action', async () => {
    const user = userEvent.setup();
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    
    const saveButton = screen.getByRole('button', { name: '' }); // Heart icon button
    const heartButton = screen.getByTestId('heart-button') || 
                       document.querySelector('[data-testid="heart-button"]') ||
                       screen.getAllByRole('button')[1]; // Second button (heart)
    
    await user.click(heartButton);
    
    // Should advance to next career
    await waitFor(() => {
      expect(screen.getByText('Data Analyst')).toBeInTheDocument();
    });
  });

  it('handles left swipe (skip) action', async () => {
    const user = userEvent.setup();
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    
    const skipButton = screen.getAllByRole('button')[0]; // First button (X)
    await user.click(skipButton);
    
    // Should advance to next career
    await waitFor(() => {
      expect(screen.getByText('Data Analyst')).toBeInTheDocument();
    });
  });

  it('shows completion screen after all cards', async () => {
    const user = userEvent.setup();
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    
    // Swipe through all 5 cards
    for (let i = 0; i < 5; i++) {
      const skipButton = screen.getAllByRole('button')[0];
      await user.click(skipButton);
      
      if (i < 4) {
        // Wait for next card to appear
        await waitFor(() => {
          expect(screen.getByText(`${i + 2} of 5`)).toBeInTheDocument();
        });
      }
    }
    
    // Should show completion screen
    await waitFor(() => {
      expect(screen.getByText('Great choices!')).toBeInTheDocument();
    });
  });

  it('shows saved careers in completion screen', async () => {
    const user = userEvent.setup();
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    
    // Save first career
    const heartButton = screen.getAllByRole('button')[1];
    await user.click(heartButton);
    
    // Skip the rest
    for (let i = 0; i < 4; i++) {
      const skipButton = screen.getAllByRole('button')[0];
      await user.click(skipButton);
      
      if (i < 3) {
        await waitFor(() => {
          const progressText = screen.queryByText(`${i + 3} of 5`);
          if (progressText) {
            expect(progressText).toBeInTheDocument();
          }
        });
      }
    }
    
    // Should show saved career in completion screen
    await waitFor(() => {
      expect(screen.getByText('Your Saved Careers:')).toBeInTheDocument();
      expect(screen.getByText('UX/UI Designer')).toBeInTheDocument();
    });
  });

  it('calls onComplete when continue button is clicked', async () => {
    const user = userEvent.setup();
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    
    // Skip all cards to reach completion
    for (let i = 0; i < 5; i++) {
      const skipButton = screen.getAllByRole('button')[0];
      await user.click(skipButton);
    }
    
    // Click continue button
    await waitFor(async () => {
      const continueButton = screen.getByText('Continue to Orientor');
      await user.click(continueButton);
      expect(mockOnComplete).toHaveBeenCalled();
    });
  });

  it('handles back button click', async () => {
    const user = userEvent.setup();
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    
    const backButton = screen.getByTestId('back-button') || 
                      document.querySelector('[data-testid="back-button"]') ||
                      screen.getAllByRole('button').find(btn => 
                        btn.querySelector('svg') // Look for arrow icon
                      );
    
    if (backButton) {
      await user.click(backButton);
      expect(mockOnComplete).toHaveBeenCalled();
    }
  });

  it('displays swipe instructions', () => {
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    expect(screen.getByText('Swipe right to save, left to skip')).toBeInTheDocument();
  });

  it('updates progress correctly', async () => {
    const user = userEvent.setup();
    render(<SwipeRecommendations onComplete={mockOnComplete} psychProfile={mockPsychProfile} />);
    
    expect(screen.getByText('1 of 5')).toBeInTheDocument();
    
    // Advance to next card
    const skipButton = screen.getAllByRole('button')[0];
    await user.click(skipButton);
    
    await waitFor(() => {
      expect(screen.getByText('2 of 5')).toBeInTheDocument();
    });
  });

  it('renders without psychProfile prop', () => {
    render(<SwipeRecommendations onComplete={mockOnComplete} />);
    expect(screen.getByText('UX/UI Designer')).toBeInTheDocument();
  });
});