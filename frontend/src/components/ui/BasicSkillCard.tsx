'use client';

import React from 'react';
import styles from './BasicSkillCard.module.css';

interface BasicSkillCardProps {
  skill: {
    name: string;
    value?: number | null;
    level: string;
    category: string;
  };
  className?: string;
}

const BasicSkillCard: React.FC<BasicSkillCardProps> = ({ skill, className = '' }) => {
  // Get skill level description
  const getSkillLevelText = (value?: number | null) => {
    if (value === null || value === undefined) return 'Untested';
    if (value <= 2) return 'Beginner';
    if (value <= 4) return 'Intermediate';
    if (value <= 6) return 'Proficient';
    if (value <= 8) return 'Advanced';
    return 'Expert';
  };

  // Get skill category icon
  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'cognitive':
        return '🧠';
      case 'technical':
        return '⚙️';
      case 'social':
        return '🤝';
      case 'creative':
        return '🎨';
      case 'leadership':
        return '👑';
      default:
        return '💼';
    }
  };

  // Get progress percentage
  const getProgressPercentage = (value?: number | null) => {
    if (value === null || value === undefined) return 0;
    return Math.round((value / 10) * 100);
  };

  return (
    <div className={`${styles.cardContainer} ${className}`}>
      <div className={styles.card}>
        {/* Skill category/icon */}
        <div className={styles.city}>
          {getCategoryIcon(skill.category)} {skill.name}
        </div>
        
        {/* Skill level description */}
        <div className={styles.weather}>
          {getSkillLevelText(skill.value)}
        </div>
        
        {/* Main skill value */}
        <div className={styles.temp}>
          {skill.value !== null && skill.value !== undefined ? skill.value.toFixed(1) : 'N/A'}
        </div>
        
        {/* Min/Max container - showing current and target */}
        <div className={styles.minmaxContainer}>
          <div className={styles.min}>
            <div className={styles.minHeading}>Current</div>
            <div className={styles.minTemp}>
              {skill.value !== null && skill.value !== undefined ? skill.value.toFixed(1) : '0.0'}
            </div>
          </div>
          <div className={styles.max}>
            <div className={styles.maxHeading}>Target</div>
            <div className={styles.maxTemp}>
              {skill.value !== null && skill.value !== undefined ? Math.min(skill.value + 2, 10).toFixed(1) : '2.0'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BasicSkillCard;