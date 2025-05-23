'use client';

import React, { useState, useEffect } from 'react';
import { getJobSkillsTree } from '@/services/api';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface Node {
  id: string;
  label: string;
  type: string;
  level?: number;
  score?: number;
  [key: string]: any;
}

interface Edge {
  source: string;
  target: string;
  type?: string;
  weight?: number;
  [key: string]: any;
}

interface SkillTreeData {
  nodes: { [key: string]: Node };
  edges: Edge[];
}

interface JobSkillsTreeProps {
  jobId: string | null;
  className?: string;
}

const JobSkillsTree: React.FC<JobSkillsTreeProps> = ({ jobId, className = '' }) => {
  const [skillTreeData, setSkillTreeData] = useState<SkillTreeData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [topSkills, setTopSkills] = useState<Node[]>([]);

  // Charger l'arbre de compétences lorsque jobId change
  useEffect(() => {
    const fetchSkillsTree = async () => {
      if (!jobId) {
        setSkillTreeData(null);
        setTopSkills([]);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const data = await getJobSkillsTree(jobId);
        setSkillTreeData(data as SkillTreeData);

        // Extraire les 5 principales compétences à développer
        // (basé sur le score ou d'autres critères)
        const skillNodes = Object.values((data as SkillTreeData).nodes).filter(
          (node: any) => node.type === 'skill'
        ) as Node[];

        // Trier par score si disponible, sinon par ordre alphabétique
        const sortedSkills = skillNodes.sort((a, b) => {
          if (a.score !== undefined && b.score !== undefined) {
            return b.score - a.score; // Du plus haut au plus bas score
          }
          return a.label.localeCompare(b.label);
        });

        setTopSkills(sortedSkills.slice(0, 5));
      } catch (err) {
        console.error('Erreur lors du chargement de l\'arbre de compétences:', err);
        setError('Impossible de charger l\'arbre de compétences');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSkillsTree();
  }, [jobId]);

  // Afficher un état de chargement
  if (isLoading) {
    return (
      <div className={`flex justify-center items-center p-8 ${className}`}>
        <LoadingSpinner size="lg" />
        <p className="ml-3 text-stitch-sage">Chargement de l'arbre de compétences...</p>
      </div>
    );
  }

  // Afficher un message d'erreur
  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <p className="text-red-600">
          Erreur: {error}
        </p>
      </div>
    );
  }

  // Afficher un message si aucun emploi n'est sélectionné
  if (!jobId) {
    return (
      <div className={`bg-stitch-primary border border-stitch-border rounded-lg p-6 text-center ${className}`}>
        <p className="text-stitch-sage">
          Sélectionnez un emploi pour voir l'arbre de compétences associé.
        </p>
      </div>
    );
  }

  // Afficher un message si aucune donnée n'est disponible
  if (!skillTreeData || Object.keys(skillTreeData.nodes).length === 0) {
    return (
      <div className={`bg-stitch-primary border border-stitch-border rounded-lg p-6 text-center ${className}`}>
        <p className="text-stitch-sage">
          Aucune donnée d'arbre de compétences disponible pour cet emploi.
        </p>
      </div>
    );
  }

  return (
    <div className={`w-full ${className}`}>
      <h2 className="text-stitch-accent text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] mb-4 font-departure">
        Compétences à développer
      </h2>

      {/* Liste des 5 principales compétences à développer */}
      <div className="bg-stitch-primary border border-stitch-border rounded-lg p-6 mb-6">
        <h3 className="text-stitch-accent text-lg font-medium mb-4">
          Top 5 des compétences à acquérir
        </h3>
        
        <div className="space-y-3">
          {topSkills.map((skill, index) => (
            <div 
              key={skill.id} 
              className="flex items-center p-3 bg-[#eaf0ec] rounded-lg"
            >
              <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-stitch-accent text-white rounded-full mr-3">
                {index + 1}
              </div>
              <div>
                <p className="text-stitch-accent font-medium">{skill.label}</p>
                {skill.description && (
                  <p className="text-stitch-sage text-sm mt-1 line-clamp-2">
                    {skill.description}
                  </p>
                )}
              </div>
              {skill.score !== undefined && (
                <div className="ml-auto">
                  <span className="bg-stitch-accent text-white text-xs font-bold px-2 py-1 rounded-full">
                    {Math.round(skill.score * 100)}%
                  </span>
                </div>
              )}
            </div>
          ))}
          
          {topSkills.length === 0 && (
            <p className="text-stitch-sage text-center py-4">
              Aucune compétence à développer identifiée.
            </p>
          )}
        </div>
      </div>

      {/* Visualisation de l'arbre de compétences (version simple) */}
      <div className="bg-stitch-primary border border-stitch-border rounded-lg p-6">
        <h3 className="text-stitch-accent text-lg font-medium mb-4">
          Arbre de compétences
        </h3>
        
        <p className="text-stitch-sage text-sm mb-4">
          Cette visualisation montre les relations entre les différentes compétences requises pour ce poste.
        </p>
        
        <div className="border border-stitch-border rounded-lg p-4 bg-[#f5f8f6] min-h-[300px]">
          {/* Ici, nous pourrions intégrer une visualisation plus avancée avec react-flow ou d3.js */}
          <p className="text-stitch-sage text-center py-8">
            Visualisation interactive de l'arbre de compétences
          </p>
        </div>
      </div>
    </div>
  );
};

export default JobSkillsTree;