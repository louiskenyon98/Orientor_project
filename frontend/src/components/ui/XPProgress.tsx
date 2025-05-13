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
        <div className="h-2 w-24 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse"></div>
        <span className="text-xs text-gray-400 dark:text-gray-500 font-departure">Loading...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`text-xs text-red-500 dark:text-red-400 font-departure ${className}`}>
        Error loading XP
      </div>
    );
  }

  return (
    <div className={`flex items-center ${className}`}>
      {/* Capsule-style level indicator */}
      <div className="flex items-center bg-light-background/80 dark:bg-dark-background/80 border border-gray-200 dark:border-gray-700 rounded-full px-3 py-1 shadow-sm">
        <span className="text-sm font-departure font-medium text-gray-800 dark:text-gray-200">🧭 Level {level} – {xpInCurrentLevel}/{xpRequiredForNextLevel} XP</span>
      </div>
      
      {/* XP Progress Bar */}
      <div className="ml-3 w-24">
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
          <div
            className="bg-blue-600 dark:bg-blue-500 rounded-full h-2 transition-all duration-500 ease-out animate-pulse-subtle"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}