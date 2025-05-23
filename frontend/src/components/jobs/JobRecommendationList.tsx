'use client';

import React, { useState } from 'react';
import JobCard, { Job } from './JobCard';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface JobRecommendationListProps {
  recommendations: Job[];
  isLoading: boolean;
  error: string | null;
  onSelectJob: (job: Job) => void;
  className?: string;
}

const JobRecommendationList: React.FC<JobRecommendationListProps> = ({
  recommendations,
  isLoading,
  error,
  onSelectJob,
  className = '',
}) => {
  const [selectedJobId, setSelectedJobId] = useState<string | null>(
    recommendations.length > 0 ? recommendations[0].id : null
  );

  // Gérer la sélection d'un emploi
  const handleSelectJob = (job: Job) => {
    setSelectedJobId(job.id);
    onSelectJob(job);
  };

  // Afficher un état de chargement
  if (isLoading) {
    return (
      <div className={`flex justify-center items-center p-8 ${className}`}>
        <LoadingSpinner size="lg" />
        <p className="ml-3 text-stitch-sage">Chargement des recommandations...</p>
      </div>
    );
  }

  // Afficher un message d'erreur
  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <p className="text-red-600">
          Erreur lors du chargement des recommandations: {error}
        </p>
      </div>
    );
  }

  // Afficher un message si aucune recommandation n'est disponible
  if (recommendations.length === 0) {
    return (
      <div className={`bg-stitch-primary border border-stitch-border rounded-lg p-6 text-center ${className}`}>
        <p className="text-stitch-sage">
          Aucune recommandation d'emploi disponible pour le moment.
        </p>
        <p className="text-stitch-sage text-sm mt-2">
          Complétez votre profil pour obtenir des recommandations personnalisées.
        </p>
      </div>
    );
  }

  return (
    <div className={`w-full ${className}`}>
      <h2 className="text-stitch-accent text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] mb-4 font-departure">
        Recommandations d'emploi
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        {recommendations.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            isSelected={job.id === selectedJobId}
            onClick={() => handleSelectJob(job)}
          />
        ))}
      </div>
    </div>
  );
};

export default JobRecommendationList;