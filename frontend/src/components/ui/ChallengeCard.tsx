'use client';
import React from 'react';
import { motion } from 'framer-motion';

interface ChallengeCardProps {
  title: string;
  description: string;
  xpReward: number;
  progress?: number; // 0-100
  isCompleted?: boolean;
  difficulty?: 'easy' | 'medium' | 'hard';
  domain?: 'builder' | 'communicator' | undefined;
  className?: string;
  onClick?: () => void;
}

export default function ChallengeCard({
  title,
  description,
  xpReward,
  progress = 0,
  isCompleted = false,
  difficulty = 'medium',
  domain,
  className = '',
  onClick
}: ChallengeCardProps) {
  // Déterminer les couleurs en fonction du domaine
  const domainColor = domain === 'builder' 
    ? 'border-domain-builder' 
    : domain === 'communicator' 
      ? 'border-domain-communicator' 
      : 'border-stitch-accent';
  
  // Déterminer la couleur de difficulté
  const difficultyBadge = {
    easy: 'bg-green-500',
    medium: 'bg-yellow-500',
    hard: 'bg-red-500'
  };

  return (
    <motion.div 
      className={`card ${domainColor} overflow-hidden ${className}`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      {/* Header avec badge de difficulté */}
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-bold font-departure text-stitch-accent">{title}</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full text-white ${difficultyBadge[difficulty]}`}>
          {difficulty}
        </span>
      </div>
      
      {/* Description */}
      <p className="text-sm text-stitch-sage mb-4">{description}</p>
      
      {/* Barre de progression */}
      <div className="mb-3">
        <div className="flex justify-between text-xs text-stitch-sage mb-1">
          <span>Progression</span>
          <span>{progress}%</span>
        </div>
        <div className="progress-container">
          <div 
            className="progress-fill" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>
      
      {/* Footer avec récompense XP et statut */}
      <div className="flex justify-between items-center mt-2">
        <div className="flex items-center">
          <span className="material-icons-outlined text-stitch-accent mr-1 text-sm">stars</span>
          <span className="text-sm font-bold text-stitch-sage">{xpReward} XP</span>
        </div>
        
        {isCompleted ? (
          <span className="flex items-center text-stitch-accent text-sm">
            <span className="material-icons-outlined mr-1 text-sm">check_circle</span>
            Complété
          </span>
        ) : (
          <span className="text-stitch-sage text-sm">En cours</span>
        )}
      </div>
    </motion.div>
  );
}