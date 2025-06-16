'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ChatOnboard from '../../components/onboarding/ChatOnboard';
import { onboardingService } from '../../services/onboardingService';

const OnboardingPage: React.FC = () => {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [needsOnboarding, setNeedsOnboarding] = useState(true);

  useEffect(() => {
    checkOnboardingStatus();
  }, []);

  const checkOnboardingStatus = async () => {
    try {
      const status = await onboardingService.getStatus();
      if (status.isComplete) {
        // User has already completed onboarding, redirect to dashboard
        router.push('/');
        return;
      }
      setNeedsOnboarding(true);
    } catch (error) {
      console.error('Error checking onboarding status:', error);
      // If we can't check, assume they need onboarding
      setNeedsOnboarding(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOnboardingComplete = async (responses: any[]) => {
    try {
      console.log('Onboarding completed with responses:', responses);
      
      // Show a success message briefly, then redirect
      setTimeout(() => {
        // Redirect to dashboard
        router.push('/');
      }, 1000);
    } catch (error) {
      console.error('Error handling onboarding completion:', error);
      // Still redirect to dashboard even if there's an error
      router.push('/');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading onboarding...</p>
        </div>
      </div>
    );
  }

  if (!needsOnboarding) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-text-secondary">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <ChatOnboard onComplete={handleOnboardingComplete} />
    </div>
  );
};

export default OnboardingPage;