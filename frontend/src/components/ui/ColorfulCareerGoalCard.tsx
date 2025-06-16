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
      className={`bg-gradient-to-br from-teal-500 to-teal-600 rounded-3xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden ${className}`}
      style={style}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
      <div className="absolute bottom-0 left-0 w-20 h-20 bg-white/5 rounded-full translate-y-10 -translate-x-10"></div>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4 relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
            <Target className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Career Goal</h3>
            <div className="flex items-center gap-2">
              <Calendar className="w-3 h-3 text-teal-100" />
              <span className="text-teal-100 text-sm">{careerGoal.targetDate}</span>
            </div>
          </div>
        </div>
        <Link
          href="/goals"
          className="text-white/60 hover:text-white transition-colors"
        >
          <TrendingUp className="w-5 h-5" />
        </Link>
      </div>

      {/* Goal Title */}
      <div className="mb-4 relative z-10">
        <h4 className="text-white text-xl font-semibold mb-2">
          {careerGoal.title}
        </h4>
        <p className="text-teal-100 text-sm leading-relaxed">
          {careerGoal.description}
        </p>
      </div>

      {/* Progress */}
      <div className="mb-6 relative z-10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-white text-sm font-medium">Progress</span>
          <span className="text-white text-sm font-semibold">{careerGoal.progress}%</span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-2.5">
          <div 
            className="bg-white h-2.5 rounded-full transition-all duration-500 shadow-sm"
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
        <div className="mt-4 pt-4 border-t border-white/20">
          <Link
            href="/goals"
            className="inline-flex items-center gap-2 text-white text-sm font-medium hover:text-teal-100 transition-colors"
          >
            <span>View Details</span>
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}