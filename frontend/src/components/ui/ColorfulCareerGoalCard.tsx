'use client';

import React from 'react';
import Link from 'next/link';
import { Target, TrendingUp, Calendar, CheckCircle, Circle } from 'lucide-react';

interface ColorfulCareerGoalCardProps {
  style?: React.CSSProperties;
  className?: string;
}

export default function ColorfulCareerGoalCard({ style, className = '' }: ColorfulCareerGoalCardProps) {
  // Mock career goal data
  const careerGoal = {
    title: "Senior Data Scientist",
    description: "Lead ML projects & mentor team members",
    targetDate: "Dec 2025",
    progress: 68,
    milestones: [
      { task: "Advanced ML Certification", completed: true },
      { task: "Lead 2 ML Projects", completed: true },
      { task: "Publish Research Paper", completed: false },
      { task: "Build Leadership Skills", completed: false }
    ]
  };

  const completedMilestones = careerGoal.milestones.filter(m => m.completed).length;
  const totalMilestones = careerGoal.milestones.length;

  return (
    <div 
      className={`bg-gradient-to-br from-teal-500 to-teal-600 rounded-3xl p-4 sm:p-6 shadow-lg hover:shadow-xl active:scale-95 transition-all duration-300 relative overflow-hidden touch-none select-none ${className}`}
      style={{
        minHeight: '200px',
        WebkitTapHighlightColor: 'transparent',
        touchAction: 'manipulation',
        ...style
      }}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
      <div className="absolute bottom-0 left-0 w-20 h-20 bg-white/5 rounded-full translate-y-10 -translate-x-10"></div>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-3 sm:mb-4 relative z-10">
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="w-8 h-8 sm:w-10 sm:h-10 bg-white/20 rounded-xl sm:rounded-2xl flex items-center justify-center backdrop-blur-sm">
            <Target className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-semibold text-white">Career Goal</h3>
            <div className="flex items-center gap-1 sm:gap-2">
              <Calendar className="w-3 h-3 text-teal-100" />
              <span className="text-teal-100 text-xs sm:text-sm">{careerGoal.targetDate}</span>
            </div>
          </div>
        </div>
        <Link
          href="/goals"
          className="text-white/60 hover:text-white active:text-white transition-colors p-2 -m-2 rounded-lg"
          style={{ minWidth: '44px', minHeight: '44px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5" />
        </Link>
      </div>

      {/* Goal Title */}
      <div className="mb-3 sm:mb-4 relative z-10">
        <h4 className="text-white text-lg sm:text-xl font-semibold mb-1 sm:mb-2">
          {careerGoal.title}
        </h4>
        <p className="text-teal-100 text-xs sm:text-sm leading-relaxed line-clamp-2">
          {careerGoal.description}
        </p>
      </div>

      {/* Progress */}
      <div className="mb-4 sm:mb-6 relative z-10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-white text-xs sm:text-sm font-medium">Progress</span>
          <span className="text-white text-xs sm:text-sm font-semibold">{careerGoal.progress}%</span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-2">
          <div 
            className="bg-white h-2 rounded-full transition-all duration-500 shadow-sm"
            style={{ width: `${careerGoal.progress}%` }}
          ></div>
        </div>
      </div>

      {/* Milestones */}
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-3">
          <span className="text-white text-sm font-medium">Key Milestones</span>
          <span className="text-teal-100 text-xs">{completedMilestones}/{totalMilestones} completed</span>
        </div>
        
        <div className="space-y-2">
          {careerGoal.milestones.slice(0, 3).map((milestone, index) => (
            <div key={index} className="flex items-center gap-3">
              {milestone.completed ? (
                <CheckCircle className="w-4 h-4 text-white flex-shrink-0" />
              ) : (
                <Circle className="w-4 h-4 text-white/60 flex-shrink-0" />
              )}
              <span 
                className={`text-xs flex-1 ${
                  milestone.completed ? 'text-white' : 'text-teal-100'
                }`}
              >
                {milestone.task}
              </span>
            </div>
          ))}
        </div>

        {/* Action Button */}
        <div className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-white/20">
          <Link
            href="/goals"
            className="inline-flex items-center gap-2 text-white text-xs sm:text-sm font-medium hover:text-teal-100 active:text-teal-100 transition-colors p-2 -m-2 rounded-lg"
            style={{ minHeight: '44px' }}
          >
            <span>View Details</span>
            <svg className="w-3 h-3 sm:w-4 sm:h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}