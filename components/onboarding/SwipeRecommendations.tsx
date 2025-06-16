'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { Heart, X, ArrowLeft, CheckCircle } from 'lucide-react';
import { PsychProfile, CareerRecommendation } from '../../types/onboarding';

interface SwipeRecommendationsProps {
  onComplete: () => void;
  psychProfile?: PsychProfile;
}

// Mock career recommendations - in production, this would come from the API
const mockRecommendations: CareerRecommendation[] = [
  {
    id: '1',
    title: 'UX/UI Designer',
    description: 'Design user-centered digital experiences that solve real problems. Combine creativity with analytical thinking to create interfaces that users love.',
    match_percentage: 92,
    skills_required: ['Design Thinking', 'Prototyping', 'User Research', 'Visual Design'],
    education_level: 'Bachelor\'s degree or equivalent experience'
  },
  {
    id: '2',
    title: 'Data Analyst',
    description: 'Transform raw data into actionable insights. Use statistical analysis and visualization to help organizations make informed decisions.',
    match_percentage: 88,
    skills_required: ['Statistical Analysis', 'SQL', 'Data Visualization', 'Python/R'],
    education_level: 'Bachelor\'s degree in related field'
  },
  {
    id: '3',
    title: 'Product Manager',
    description: 'Bridge the gap between technical teams and business objectives. Lead product development from concept to launch.',
    match_percentage: 85,
    skills_required: ['Strategic Thinking', 'Project Management', 'Market Research', 'Communication'],
    education_level: 'Bachelor\'s degree, MBA preferred'
  },
  {
    id: '4',
    title: 'Software Developer',
    description: 'Build applications and systems that power modern technology. Solve complex problems through code and innovation.',
    match_percentage: 82,
    skills_required: ['Programming', 'Problem Solving', 'Software Architecture', 'Testing'],
    education_level: 'Bachelor\'s degree or coding bootcamp'
  },
  {
    id: '5',
    title: 'Marketing Specialist',
    description: 'Create compelling campaigns that connect brands with their audiences. Blend creativity with data-driven strategies.',
    match_percentage: 79,
    skills_required: ['Content Creation', 'Digital Marketing', 'Analytics', 'Brand Strategy'],
    education_level: 'Bachelor\'s degree in Marketing or related field'
  }
];

const SwipeRecommendations: React.FC<SwipeRecommendationsProps> = ({ 
  onComplete, 
  psychProfile 
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [savedCareers, setSavedCareers] = useState<CareerRecommendation[]>([]);
  const [isComplete, setIsComplete] = useState(false);

  const currentCard = mockRecommendations[currentIndex];
  const progress = ((currentIndex + 1) / mockRecommendations.length) * 100;

  const handleSwipe = (direction: 'left' | 'right') => {
    if (direction === 'right' && currentCard) {
      setSavedCareers(prev => [...prev, currentCard]);
    }

    if (currentIndex >= mockRecommendations.length - 1) {
      setIsComplete(true);
    } else {
      setCurrentIndex(prev => prev + 1);
    }
  };

  const handleCardDrag = (info: PanInfo) => {
    const { offset, velocity } = info;
    const swipeThreshold = 100;
    const swipeVelocityThreshold = 500;

    if (
      offset.x > swipeThreshold || 
      (velocity.x > swipeVelocityThreshold && offset.x > 0)
    ) {
      handleSwipe('right');
    } else if (
      offset.x < -swipeThreshold || 
      (velocity.x < -swipeVelocityThreshold && offset.x < 0)
    ) {
      handleSwipe('left');
    }
  };

  if (isComplete) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-3xl p-8 shadow-lg max-w-md w-full text-center"
        >
          <div className="mb-6">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-text-primary mb-2">
              Great choices!
            </h2>
            <p className="text-text-secondary">
              You've saved {savedCareers.length} career{savedCareers.length !== 1 ? 's' : ''} to explore further.
            </p>
          </div>

          {savedCareers.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold text-text-primary mb-3">Your Saved Careers:</h3>
              <div className="space-y-2">
                {savedCareers.map((career) => (
                  <div key={career.id} className="bg-surface rounded-xl p-3 text-left">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">{career.title}</span>
                      <span className="text-xs text-primary font-semibold">
                        {career.match_percentage}% match
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={onComplete}
            className="w-full bg-primary text-white py-3 px-6 rounded-2xl font-semibold
              hover:bg-primary/90 transition-colors"
          >
            Continue to Orientor
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-sm border-b border-gray-200 p-4">
        <div className="flex items-center justify-between max-w-md mx-auto">
          <button
            onClick={onComplete}
            className="p-2 text-text-secondary hover:text-primary transition-colors"
            data-testid="back-button"
          >
            <ArrowLeft size={24} />
          </button>
          <div className="flex-1 mx-4">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-primary"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
            <p className="text-sm text-text-secondary mt-1 text-center">
              {currentIndex + 1} of {mockRecommendations.length}
            </p>
          </div>
          <div className="w-10" /> {/* Spacer */}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="relative w-full max-w-sm">
          <AnimatePresence mode="wait">
            {currentCard && (
              <motion.div
                key={currentCard.id}
                className="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                drag="x"
                dragConstraints={{ left: 0, right: 0 }}
                dragElastic={0.1}
                onDragEnd={(_, info) => handleCardDrag(info)}
                whileDrag={{ rotate: 0 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
              >
                {/* Match Percentage Badge */}
                <div className="absolute top-4 right-4 z-10">
                  <div className="bg-primary text-white px-3 py-1 rounded-full text-sm font-semibold">
                    {currentCard.match_percentage}% match
                  </div>
                </div>

                {/* Card Content */}
                <div className="p-6">
                  <h3 className="text-2xl font-bold text-text-primary mb-3">
                    {currentCard.title}
                  </h3>
                  
                  <p className="text-text-secondary mb-6 leading-relaxed">
                    {currentCard.description}
                  </p>

                  {/* Skills */}
                  <div className="mb-6">
                    <h4 className="font-semibold text-text-primary mb-2">
                      Key Skills:
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {currentCard.skills_required?.map((skill) => (
                        <span
                          key={skill}
                          className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Education */}
                  {currentCard.education_level && (
                    <div className="text-sm text-text-secondary">
                      <strong>Education:</strong> {currentCard.education_level}
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Swipe Instructions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="text-center mt-6 text-text-muted"
          >
            <p className="text-sm mb-4">Swipe right to save, left to skip</p>
          </motion.div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="sticky bottom-0 bg-background/95 backdrop-blur-sm border-t border-gray-200 p-4">
        <div className="flex items-center justify-center space-x-8 max-w-md mx-auto">
          <button
            onClick={() => handleSwipe('left')}
            className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center
              hover:bg-gray-200 transition-colors active:scale-95"
          >
            <X size={24} className="text-gray-600" />
          </button>
          
          <button
            onClick={() => handleSwipe('right')}
            className="w-16 h-16 bg-primary rounded-full flex items-center justify-center
              hover:bg-primary/90 transition-colors active:scale-95"
            data-testid="heart-button"
          >
            <Heart size={24} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default SwipeRecommendations;