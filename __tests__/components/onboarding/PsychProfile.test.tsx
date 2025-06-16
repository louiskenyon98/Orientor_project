import React from 'react';
import { render, screen } from '@testing-library/react';
import PsychProfile from '../../../components/onboarding/PsychProfile';
import { PsychProfile as PsychProfileType } from '../../../types/onboarding';

const mockProfile: PsychProfileType = {
  hexaco: {
    extraversion: 85,
    openness: 92,
    conscientiousness: 76,
    emotionality: 45,
    agreeableness: 88,
    honesty: 72
  },
  riasec: {
    artistic: 90,
    social: 85,
    investigative: 78,
    enterprising: 65,
    realistic: 45,
    conventional: 30
  },
  topTraits: ['Creative', 'Analytical', 'Collaborative'],
  description: 'You have a unique blend of creativity and analytical thinking, with strong collaborative instincts.'
};

describe('PsychProfile Component', () => {
  it('renders profile title', () => {
    render(<PsychProfile profile={mockProfile} />);
    expect(screen.getByText('Your Psychological Profile')).toBeInTheDocument();
  });

  it('displays profile description', () => {
    render(<PsychProfile profile={mockProfile} />);
    expect(screen.getByText(mockProfile.description)).toBeInTheDocument();
  });

  it('renders top traits section', () => {
    render(<PsychProfile profile={mockProfile} />);
    expect(screen.getByText('Top Traits')).toBeInTheDocument();
    
    mockProfile.topTraits.forEach(trait => {
      expect(screen.getByText(trait)).toBeInTheDocument();
    });
  });

  it('renders career interests section', () => {
    render(<PsychProfile profile={mockProfile} />);
    expect(screen.getByText('Career Interests')).toBeInTheDocument();
  });

  it('renders personality dimensions section', () => {
    render(<PsychProfile profile={mockProfile} />);
    expect(screen.getByText('Personality Dimensions')).toBeInTheDocument();
  });

  it('displays top HEXACO traits with scores', () => {
    render(<PsychProfile profile={mockProfile} />);
    
    // Should show top 2 HEXACO traits (Openness: 92%, Agreeableness: 88%)
    expect(screen.getByText('92%')).toBeInTheDocument();
    expect(screen.getByText('88%')).toBeInTheDocument();
    expect(screen.getByText('Openness')).toBeInTheDocument();
    expect(screen.getByText('Agreeableness')).toBeInTheDocument();
  });

  it('displays top RIASEC interests with progress bars', () => {
    render(<PsychProfile profile={mockProfile} />);
    
    // Should show top 2 RIASEC interests (Artistic: 90%, Social: 85%)
    expect(screen.getByText('Artistic')).toBeInTheDocument();
    expect(screen.getByText('Social')).toBeInTheDocument();
    expect(screen.getByText('90%')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('handles partial profile data', () => {
    const partialProfile: PsychProfileType = {
      hexaco: {
        extraversion: 80
      },
      riasec: {
        artistic: 75
      },
      topTraits: ['Creative'],
      description: 'Partial profile test'
    };

    render(<PsychProfile profile={partialProfile} />);
    expect(screen.getByText('Partial profile test')).toBeInTheDocument();
    expect(screen.getByText('Creative')).toBeInTheDocument();
  });

  it('applies correct CSS classes for styling', () => {
    const { container } = render(<PsychProfile profile={mockProfile} />);
    
    // Check for gradient background
    const profileContainer = container.querySelector('.bg-gradient-to-br');
    expect(profileContainer).toBeInTheDocument();
    
    // Check for rounded corners
    const roundedElements = container.querySelectorAll('.rounded-2xl, .rounded-3xl');
    expect(roundedElements.length).toBeGreaterThan(0);
  });

  it('renders brain icon', () => {
    const { container } = render(<PsychProfile profile={mockProfile} />);
    
    // Lucide icons are rendered as SVG elements
    const brainIcon = container.querySelector('svg');
    expect(brainIcon).toBeInTheDocument();
  });

  it('handles empty traits array', () => {
    const profileWithNoTraits: PsychProfileType = {
      ...mockProfile,
      topTraits: []
    };

    render(<PsychProfile profile={profileWithNoTraits} />);
    expect(screen.getByText('Top Traits')).toBeInTheDocument();
  });

  it('formats trait names correctly', () => {
    render(<PsychProfile profile={mockProfile} />);
    
    // Check that trait names are capitalized properly
    expect(screen.getByText('Openness')).toBeInTheDocument();
    expect(screen.getByText('Agreeableness')).toBeInTheDocument();
    expect(screen.getByText('Artistic')).toBeInTheDocument();
    expect(screen.getByText('Social')).toBeInTheDocument();
  });
});