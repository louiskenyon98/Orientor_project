'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, RefreshCw, Check } from 'lucide-react';
import { useOnboardingStore } from '../../stores/onboardingStore';
import { ChatMessage as ChatMessageType } from '../../types/onboarding';
import TypingIndicator from './TypingIndicator';
import PsychProfile from './PsychProfile';
import SwipeRecommendations from './SwipeRecommendations';

interface ChatOnboardProps {
  onComplete?: (responses: any[]) => void;
  className?: string;
}

const ChatOnboard: React.FC<ChatOnboardProps> = ({ onComplete, className = '' }) => {
  const [inputValue, setInputValue] = useState('');
  const [showSwipe, setShowSwipe] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const {
    messages,
    responses,
    currentQuestionIndex,
    isTyping,
    isComplete,
    psychProfile,
    addMessage,
    addResponse,
    nextQuestion,
    setTyping,
    reset,
    getCurrentQuestion,
    getProgress
  } = useOnboardingStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (currentQuestionIndex === 0) {
      // Show first question after welcome message
      setTimeout(() => {
        const firstQuestion = getCurrentQuestion();
        if (firstQuestion) {
          setTyping(true);
          setTimeout(() => {
            addMessage({
              type: 'system',
              content: firstQuestion.text
            });
            setTyping(false);
          }, 1500);
        }
      }, 1000);
    }
  }, []);

  useEffect(() => {
    if (isComplete && psychProfile) {
      onComplete?.(responses);
      // Show swipe interface after profile generation
      setTimeout(() => setShowSwipe(true), 2000);
    }
  }, [isComplete, psychProfile, responses, onComplete]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const currentQuestion = getCurrentQuestion();
    if (!currentQuestion) return;

    // Add user message
    addMessage({
      type: 'user',
      content: inputValue.trim()
    });

    // Add response to store
    addResponse({
      questionId: currentQuestion.id,
      question: currentQuestion.text,
      response: inputValue.trim()
    });

    setInputValue('');

    // Show typing indicator
    setTyping(true);

    // Simulate processing time
    setTimeout(() => {
      nextQuestion();
      
      const nextQ = getCurrentQuestion();
      if (nextQ) {
        // Add next question
        addMessage({
          type: 'system',
          content: nextQ.text
        });
      } else {
        // Generate psychological profile
        generatePsychProfile();
      }
      
      setTyping(false);
    }, 1500);
  };

  const generatePsychProfile = () => {
    // Simple profile generation based on responses
    // In a real implementation, this would use ML models
    const profile = {
      hexaco: {
        extraversion: Math.random() * 100,
        openness: Math.random() * 100,
        conscientiousness: Math.random() * 100,
        emotionality: Math.random() * 100,
        agreeableness: Math.random() * 100,
        honesty: Math.random() * 100
      },
      riasec: {
        realistic: Math.random() * 100,
        investigative: Math.random() * 100,
        artistic: Math.random() * 100,
        social: Math.random() * 100,
        enterprising: Math.random() * 100,
        conventional: Math.random() * 100
      },
      topTraits: ['Creative', 'Analytical', 'Collaborative'],
      description: 'You have a unique blend of creativity and analytical thinking, with strong collaborative instincts.'
    };

    useOnboardingStore.getState().setPsychProfile(profile);
    
    addMessage({
      type: 'system',
      content: "Great! I've analyzed your responses and created your psychological profile. Let me show you some career recommendations based on your personality."
    });
  };

  const handleRefresh = () => {
    if (window.confirm('Are you sure you want to start over? This will clear all your responses.')) {
      reset();
      setShowSwipe(false);
    }
  };

  if (showSwipe) {
    return (
      <div className={`min-h-screen bg-background ${className}`}>
        <SwipeRecommendations 
          onComplete={() => setShowSwipe(false)}
          psychProfile={psychProfile}
        />
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-background flex flex-col ${className}`}>
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-sm border-b border-gray-200 p-4">
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          <div className="flex-1">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-primary"
                initial={{ width: 0 }}
                animate={{ width: `${getProgress()}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            <p className="text-sm text-text-secondary mt-1">
              {getProgress()}% complete
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="ml-4 p-2 text-text-secondary hover:text-primary transition-colors"
            title="Refresh and start over"
          >
            <RefreshCw size={20} />
          </button>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-2xl mx-auto space-y-6">
          <AnimatePresence mode="wait">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
          </AnimatePresence>
          
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex justify-start"
            >
              <div className="chat-bubble-system">
                <TypingIndicator />
              </div>
            </motion.div>
          )}

          {isComplete && psychProfile && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <PsychProfile profile={psychProfile} />
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form */}
      {!isComplete && (
        <div className="sticky bottom-0 bg-background/95 backdrop-blur-sm border-t border-gray-200 p-4">
          <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
            <div className="flex items-end space-x-3">
              <div className="flex-1 relative">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Write here.."
                  className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-2xl 
                    focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
                    resize-none min-h-[48px] max-h-32"
                  rows={1}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit(e);
                    }
                  }}
                  disabled={isTyping}
                />
                <button
                  type="submit"
                  disabled={!inputValue.trim() || isTyping}
                  className="absolute right-2 bottom-2 p-2 bg-primary text-white rounded-full 
                    hover:bg-primary/90 disabled:bg-gray-300 disabled:cursor-not-allowed
                    transition-colors"
                  aria-label="Send message"
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </form>
        </div>
      )}

      {/* Finish Button */}
      {isComplete && (
        <div className="sticky bottom-0 bg-background/95 backdrop-blur-sm border-t border-gray-200 p-4">
          <div className="max-w-2xl mx-auto">
            <button
              onClick={() => setShowSwipe(true)}
              className="w-full bg-primary text-white py-3 px-6 rounded-2xl 
                hover:bg-primary/90 transition-colors flex items-center justify-center space-x-2"
            >
              <Check size={20} />
              <span>Finish entry</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Chat Message Component
const ChatMessage: React.FC<{ message: ChatMessageType }> = ({ message }) => {
  const isSystem = message.type === 'system';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isSystem ? 'justify-start' : 'justify-end'}`}
    >
      <div className={isSystem ? 'chat-bubble-system' : 'chat-bubble-user'}>
        <p className="text-sm leading-relaxed">{message.content}</p>
      </div>
    </motion.div>
  );
};

export default ChatOnboard;