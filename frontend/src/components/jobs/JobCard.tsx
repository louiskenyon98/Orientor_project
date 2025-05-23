'use client';

import React from 'react';
import { motion } from 'framer-motion';

// Interface pour les données d'un emploi
export interface Job {
  id: string;
  score: number;
  metadata: {
    title: string;
    description?: string;
    skills?: string[];
    match_percentage?: number;
    isco_group?: string;
    preferred_label?: string;
    alt_labels?: string[];
    [key: string]: any; // Pour les autres propriétés potentielles
  };
}

interface JobCardProps {
  job: Job;
  isSelected: boolean;
  onClick: () => void;
  className?: string;
}

const JobCard: React.FC<JobCardProps> = ({ job, isSelected, onClick, className = '' }) => {
  // Extraire les informations pertinentes de l'emploi
  const title = job.metadata.preferred_label || job.metadata.title || 'Emploi sans titre';
  const description = job.metadata.description || 'Aucune description disponible';
  const matchPercentage = job.metadata.match_percentage || Math.round(job.score * 100);
  const skills = job.metadata.skills || [];
  
  // Limiter le nombre de compétences affichées
  const displayedSkills = skills.slice(0, 3);
  
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`
        relative flex flex-col rounded-lg border p-5 cursor-pointer transition-all duration-200
        ${isSelected 
          ? 'border-stitch-accent bg-[#eaf0ec] shadow-md' 
          : 'border-stitch-border bg-stitch-primary hover:bg-[#f5f8f6]'}
        ${className}
      `}
    >
      {/* Badge de correspondance */}
      <div className="absolute top-4 right-4 bg-stitch-accent text-white text-xs font-bold px-2 py-1 rounded-full">
        {matchPercentage}% match
      </div>
      
      {/* Titre de l'emploi */}
      <h3 className="text-stitch-accent text-xl font-bold mb-2 pr-16">{title}</h3>
      
      {/* Description courte */}
      <p className="text-stitch-sage text-sm mb-4 line-clamp-2">{description}</p>
      
      {/* Compétences principales */}
      {displayedSkills.length > 0 && (
        <div className="mt-auto">
          <p className="text-xs text-stitch-sage mb-2 font-medium">Compétences clés:</p>
          <div className="flex flex-wrap gap-2">
            {displayedSkills.map((skill, index) => (
              <span 
                key={index}
                className="bg-[#eaf0ec] text-stitch-sage text-xs px-2 py-1 rounded-md"
              >
                {skill}
              </span>
            ))}
            {skills.length > 3 && (
              <span className="text-stitch-sage text-xs px-2 py-1">
                +{skills.length - 3} autres
              </span>
            )}
          </div>
        </div>
      )}
      
      {/* Indicateur de sélection */}
      {isSelected && (
        <div className="absolute bottom-0 left-0 w-full h-1 bg-stitch-accent rounded-b-lg"></div>
      )}
    </motion.div>
  );
};

export default JobCard;