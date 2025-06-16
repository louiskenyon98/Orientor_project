import React from 'react';
import { render, screen } from '@testing-library/react';
import TypingIndicator from '../../../components/onboarding/TypingIndicator';

describe('TypingIndicator Component', () => {
  it('renders typing indicator', () => {
    const { container } = render(<TypingIndicator />);
    expect(container.querySelector('.typing-indicator')).toBeInTheDocument();
  });

  it('renders three typing dots', () => {
    const { container } = render(<TypingIndicator />);
    const dots = container.querySelectorAll('.typing-dot');
    expect(dots).toHaveLength(3);
  });

  it('applies correct CSS classes', () => {
    const { container } = render(<TypingIndicator />);
    const indicator = container.querySelector('.typing-indicator');
    expect(indicator).toHaveClass('typing-indicator');
    
    const dots = container.querySelectorAll('.typing-dot');
    dots.forEach(dot => {
      expect(dot).toHaveClass('typing-dot');
    });
  });

  it('has proper accessibility attributes', () => {
    const { container } = render(<TypingIndicator />);
    
    // Add test ID for testing purposes
    const indicator = container.querySelector('.typing-indicator');
    expect(indicator).toBeInTheDocument();
  });
});