import React, { useState, useEffect } from 'react';
import { getUserProgress } from '../../utils/treeStorage';

interface XPProgressProps {
  className?: string;
}

// Define XP thresholds for each level
const XP_THRESHOLDS = [
  { level: 1, min: 0, max: 50 },
  { level: 2, min: 51, max: 150 },
  { level: 3, min: 151, max: 300 },
  { level: 4, min: 301, max: 500 },
  { level: 5, min: 501, max: 750 },
  { level: 6, min: 751, max: Infinity }
];

export default function XPProgress({ className = '' }: XPProgressProps) {
  const [totalXP, setTotalXP] = useState(0);
  const [level, setLevel] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const progress = await getUserProgress();
        setTotalXP(progress.total_xp);
        setLevel(progress.level);
      } catch (err: any) {
        console.error('Error fetching user progress:', err);
        setError(err.message || 'Failed to load progress');
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, []);

  // Calculate current level threshold and progress percentage
  const currentThreshold = XP_THRESHOLDS.find(t => t.level === level) || XP_THRESHOLDS[0];
  const nextThreshold = XP_THRESHOLDS.find(t => t.level === level + 1);
  
  // Calculate progress within current level
  const levelMinXP = currentThreshold.min;
  const levelMaxXP = currentThreshold.max;
  const xpInCurrentLevel = totalXP - levelMinXP;
  const xpRequiredForNextLevel = levelMaxXP - levelMinXP;
  const progressPercentage = Math.min(100, (xpInCurrentLevel / xpRequiredForNextLevel) * 100);

  if (loading) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="h-2 w-24 bg-gray-200 rounded-full animate-pulse"></div>
        <span className="text-xs text-gray-400">Loading...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`text-xs text-red-500 ${className}`}>
        Error loading XP
      </div>
    );
  }
  return (
    <div className={`flex items-center ${className}`}>
      {/* Level Badge */}
      <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
        {level}
      </div>
      
      {/* XP Progress Bar */}
      <div className="ml-4 flex-1">
        <div className="flex items-center justify-start gap-2 text-xs mb-1">
          <span className="font-medium text-gray-700">Level {level}</span>
          <span className="text-gray-500">
            {xpInCurrentLevel}/{xpRequiredForNextLevel} XP
            {nextThreshold ? ` to Lvl ${level + 1} ` : ' (Max)'}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 rounded-full h-2 transition-all duration-500 ease-out"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
} 