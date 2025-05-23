'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Image from 'next/image';

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

// Fonction pour sélectionner un avatar en fonction de l'ID et du titre de l'emploi
const getAvatarForJob = (jobId: string, title: string): string => {
  // Liste des avatars disponibles
  const avatars = [
    'academic.png',
    'artist.png',
    'businessman.png',
    'chef.png',
    'constructor.png',
    'controller.png',
    'health.png',
    'nurse.png',
    'police.png',
    'programmer.png',
    'women.png'
  ];
  
  // Mots-clés pour associer des avatars spécifiques
  const keywordMap: Record<string, string> = {
    'professor': 'academic.png',
    'teacher': 'academic.png',
    'researcher': 'academic.png',
    'artist': 'artist.png',
    'designer': 'artist.png',
    'creative': 'artist.png',
    'business': 'businessman.png',
    'manager': 'businessman.png',
    'executive': 'businessman.png',
    'chef': 'chef.png',
    'cook': 'chef.png',
    'food': 'chef.png',
    'construction': 'constructor.png',
    'builder': 'constructor.png',
    'engineer': 'constructor.png',
    'controller': 'controller.png',
    'accountant': 'controller.png',
    'finance': 'controller.png',
    'health': 'health.png',
    'doctor': 'health.png',
    'medical': 'health.png',
    'nurse': 'nurse.png',
    'caregiver': 'nurse.png',
    'police': 'police.png',
    'security': 'police.png',
    'law': 'police.png',
    'programmer': 'programmer.png',
    'developer': 'programmer.png',
    'software': 'programmer.png',
    'woman': 'women.png',
    'women': 'women.png'
  };
  
  // Vérifier si le titre contient un mot-clé
  const lowerTitle = title.toLowerCase();
  for (const [keyword, avatar] of Object.entries(keywordMap)) {
    if (lowerTitle.includes(keyword.toLowerCase())) {
      return avatar;
    }
  }
  
  // Si aucun mot-clé ne correspond, utiliser l'ID pour sélectionner un avatar
  // Convertir l'ID en nombre pour sélectionner un avatar
  let sum = 0;
  for (let i = 0; i < jobId.length; i++) {
    sum += jobId.charCodeAt(i);
  }
  
  // Utiliser le modulo pour obtenir un index dans la plage des avatars disponibles
  const index = sum % avatars.length;
  return avatars[index];
};

const JobCard: React.FC<JobCardProps> = ({ job, isSelected, onClick, className = '' }) => {
  // Extraire les informations pertinentes de l'emploi
  const rawTitle = job.metadata.preferred_label || job.metadata.title || job.id.replace('occupation::key_', '') || 'Emploi sans titre';
  
  // Assurer que le titre n'est pas trop long et ajouter une ellipse si nécessaire
  const title = rawTitle.length > 40 ? `${rawTitle.substring(0, 40)}...` : rawTitle;
  
  // Extraire les autres informations
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
      
      {/* Avatar et titre de l'emploi */}
      <div className="flex items-start mb-3">
        <div className="flex-shrink-0 mr-3">
          {/* Avatar local basé sur l'ID de l'emploi */}
          <div className="w-12 h-12 rounded-full overflow-hidden bg-stitch-accent flex items-center justify-center">
            <Image
              src={`/avatar/${getAvatarForJob(job.id, title)}`}
              alt={title}
              width={48}
              height={48}
              className="w-full h-full object-cover"
            />
          </div>
        </div>
        <h3 className="text-stitch-accent text-xl font-bold pr-16">{title}</h3>
      </div>
      
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