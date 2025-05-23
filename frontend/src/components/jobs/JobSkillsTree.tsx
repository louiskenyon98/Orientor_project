'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { getJobSkillsTree } from '@/services/api';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node as FlowNode,
  Edge as FlowEdge,
  useNodesState,
  useEdgesState,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';

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
  visualizations?: {
    plotly?: any;
    matplotlib?: string;
    streamlit?: any;
  };
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
  
  // États pour ReactFlow
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Fonction pour convertir les données de l'arbre de compétences en format ReactFlow
  const convertToReactFlowFormat = useCallback((data: SkillTreeData) => {
    if (!data || !data.nodes || !data.edges) return;

    // Identifier le nœud d'emploi (occupation)
    const occupationNode = Object.values(data.nodes).find(node => node.type === 'occupation');
    if (!occupationNode) return;
    
    // Identifier les nœuds de compétences (skills) directement liés à l'emploi
    const skillNodes = Object.values(data.nodes).filter(node =>
      node.type === 'skill' &&
      data.edges.some(edge =>
        (edge.source === occupationNode.id && edge.target === node.id) ||
        (edge.target === occupationNode.id && edge.source === node.id)
      )
    );
    
    // Limiter à 5 compétences maximum
    const topSkillNodes = skillNodes.slice(0, 5);
    
    // Créer un layout en étoile avec l'emploi au centre
    const centerX = 400;
    const centerY = 250;
    const radius = 200;
    
    // Convertir les nœuds
    const flowNodes: FlowNode[] = [];
    
    // Ajouter le nœud d'emploi au centre
    flowNodes.push({
      id: occupationNode.id,
      position: { x: centerX, y: centerY },
      data: { label: occupationNode.label },
      style: { background: '#4285F4', color: 'white', padding: '10px', borderRadius: '8px', width: '200px', textAlign: 'center' },
      type: 'default'
    });
    
    // Ajouter les nœuds de compétences autour
    topSkillNodes.forEach((node, index) => {
      const angle = (index / topSkillNodes.length) * 2 * Math.PI;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      
      flowNodes.push({
        id: node.id,
        position: { x, y },
        data: { label: node.label },
        style: { background: '#34A853', color: 'white', padding: '8px', borderRadius: '8px', width: '180px', textAlign: 'center' },
        type: 'default'
      });
    });
      
    // Convertir uniquement les arêtes entre l'emploi et les compétences
    const flowEdges: FlowEdge[] = [];
    
    // Ajouter les arêtes entre l'emploi et les compétences
    topSkillNodes.forEach((node, index) => {
      // Trouver l'arête correspondante
      const edge = data.edges.find(e =>
        (e.source === occupationNode.id && e.target === node.id) ||
        (e.target === occupationNode.id && e.source === node.id)
      );
      
      if (edge) {
        flowEdges.push({
          id: `e${index}`,
          source: occupationNode.id,
          target: node.id,
          animated: false,
          style: {
            stroke: '#888',
            strokeWidth: edge.weight ? Math.max(1, edge.weight * 3) : 1,
            strokeOpacity: 0.8
          },
          type: 'default'
        });
      }
    });
    
    console.log("Nœuds ReactFlow:", flowNodes);
    console.log("Arêtes ReactFlow:", flowEdges);
    console.log("Nombre de nœuds:", flowNodes.length);
    console.log("Nombre d'arêtes:", flowEdges.length);
    
    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [setNodes, setEdges]);

  // Charger l'arbre de compétences lorsque jobId change
  useEffect(() => {
    const fetchSkillsTree = async () => {
      if (!jobId) {
        setSkillTreeData(null);
        setTopSkills([]);
        setNodes([]);
        setEdges([]);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const data = await getJobSkillsTree(jobId);
        const typedData = data as SkillTreeData;
        setSkillTreeData(typedData);
        
        console.log("Données de l'arbre de compétences reçues:", typedData);
        
        // Extraire les 5 principales compétences à développer
        const skillNodes = Object.values(typedData.nodes).filter(
          (node) => node.type === 'skill'
        ) as Node[];
        
        // Trier par score si disponible, sinon par ordre alphabétique
        const sortedSkills = skillNodes.sort((a, b) => {
          if (a.score !== undefined && b.score !== undefined) {
            return b.score - a.score; // Du plus haut au plus bas score
          }
          return a.label.localeCompare(b.label);
        });
        
        setTopSkills(sortedSkills.slice(0, 5));
        
        // Convertir les données pour ReactFlow
        convertToReactFlowFormat(typedData);
      } catch (err) {
        console.error("Erreur lors du chargement de l'arbre de compétences:", err);
        setError("Impossible de charger l'arbre de compétences");
      } finally {
        setIsLoading(false);
      }
    };

    fetchSkillsTree();
  }, [jobId, convertToReactFlowFormat]);

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
      {/* Top 5 des compétences */}
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

      {/* Visualisation de l'arbre de compétences ESCO */}
      <div className="bg-stitch-primary border border-stitch-border rounded-lg p-6">
        <h3 className="text-stitch-accent text-lg font-medium mb-4">
          Arbre de compétences ESCO
        </h3>
        
        <p className="text-stitch-sage text-sm mb-4">
          Cette visualisation montre les relations entre les différentes compétences requises pour ce poste, générées à partir du graphe ESCO.
        </p>
        
        {/* Légende */}
        <div className="flex flex-wrap gap-3 mb-4">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
            <span className="text-xs text-stitch-sage">Emploi</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
            <span className="text-xs text-stitch-sage">Compétence</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div>
            <span className="text-xs text-stitch-sage">Groupe de compétences</span>
          </div>
        </div>
        
        {/* Visualisation ReactFlow */}
        <div className="border border-stitch-border rounded-lg overflow-hidden bg-[#f5f8f6]" style={{ height: '500px' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            attributionPosition="bottom-right"
          >
            <Controls />
            <MiniMap />
            <Background color="#aaa" gap={16} />
          </ReactFlow>
        </div>
        
        <div className="mt-4 text-center">
          <p className="text-xs text-stitch-sage italic">
            Nombre total de nœuds: {Object.keys(skillTreeData.nodes).length} | 
            Nombre total de relations: {skillTreeData.edges.length}
          </p>
        </div>
      </div>
    </div>
  );
};

export default JobSkillsTree;