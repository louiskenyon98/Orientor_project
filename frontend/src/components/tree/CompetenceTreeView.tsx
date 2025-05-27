import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';

// Importez les styles existants si nécessaire
import '../tree/treestyles.css';

// Composant pour afficher un défi
import ChallengeCard from '../ui/ChallengeCard';
import { getCompetenceTree, completeChallenge } from '../../services/competenceTreeService';

// Types personnalisés
interface CompetenceNode {
  id: string;
  skill_id: string;
  skill_label: string;
  challenge: string;
  xp_reward: number;
  visible: boolean;
  revealed: boolean;
  state: 'locked' | 'completed';
  notes: string;
}

interface CompetenceTreeData {
  nodes: CompetenceNode[];
  edges: { source: string; target: string }[];
  graph_id: string;
}

interface CompetenceTreeViewProps {
  graphId: string;
}

// Composant de nœud personnalisé
const CustomNode = ({ data }: { data: any }) => {
  const { skill_label, challenge, xp_reward, revealed, state, onComplete } = data;
  
  if (!revealed) {
    return (
      <div className="competence-node hidden">
        <div className="node-content">
          <span className="question-mark">?</span>
          <div className="tooltip">Complétez les défis précédents pour débloquer</div>
        </div>
      </div>
    );
  }
  
  return (
    <div className={`competence-node ${state}`}>
      <div className="node-content">
        <h4>{skill_label}</h4>
        <ChallengeCard 
          challenge={challenge} 
          xpReward={xp_reward} 
          completed={state === 'completed'} 
          onComplete={onComplete}
        />
      </div>
    </div>
  );
};

// Définir les types de nœuds personnalisés
const nodeTypes: NodeTypes = {
  customNode: CustomNode,
};

const CompetenceTreeView: React.FC<CompetenceTreeViewProps> = ({ graphId }) => {
  console.log("CompetenceTreeView: Composant chargé avec graphId:", graphId);
  
  const [treeData, setTreeData] = useState<CompetenceTreeData | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Fonction pour charger l'arbre de compétences
  const loadCompetenceTree = useCallback(async () => {
    console.log("loadCompetenceTree: Début du chargement avec graphId:", graphId);
    if (!graphId) {
      console.log("loadCompetenceTree: Pas de graphId, abandon du chargement");
      return;
    }
    
    try {
      setLoading(true);
      console.log("loadCompetenceTree: Loading state set to true");
      console.log("loadCompetenceTree: Appel à getCompetenceTree avec graphId:", graphId);
      const data = await getCompetenceTree(graphId);
      console.log("loadCompetenceTree: Données reçues:", data);
      setTreeData(data);
      
      // Convertir les données en format React Flow
      const flowNodes: Node[] = data.nodes.map((node: CompetenceNode) => ({
        id: node.id,
        type: 'customNode',
        position: { x: 0, y: 0 }, // Les positions seront calculées par le layout
        data: {
          ...node,
          onComplete: () => handleCompleteChallenge(node.id),
        },
      }));
      
      const flowEdges: Edge[] = data.edges.map((edge: any, index: number) => ({
        id: `e${index}`,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
      }));
      
      setNodes(flowNodes);
      setEdges(flowEdges);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors du chargement de l\'arbre de compétences');
      setLoading(false);
    }
  }, [graphId, setNodes, setEdges]);
  
  // Charger l'arbre au montage du composant
  useEffect(() => {
    if (graphId) {
      loadCompetenceTree();
    }
  }, [graphId, loadCompetenceTree]);
  
  // Fonction pour marquer un défi comme complété
  const handleCompleteChallenge = async (nodeId: string) => {
    try {
      // Récupérer l'ID utilisateur (à adapter selon votre système d'authentification)
      const userId = 1; // Exemple, à remplacer par l'ID réel de l'utilisateur
      
      await completeChallenge(nodeId, userId);
      
      // Mettre à jour l'état local
      setNodes((prevNodes) =>
        prevNodes.map((node) => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: {
                ...node.data,
                state: 'completed',
              },
            };
          }
          return node;
        })
      );
      
      // Recharger l'arbre pour obtenir les nouveaux nœuds révélés
      loadCompetenceTree();
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors de la complétion du défi');
    }
  };
  
  if (loading) {
    return <div>Chargement de l'arbre de compétences...</div>;
  }
  
  if (error) {
    return <div>Erreur: {error}</div>;
  }
  
  if (!treeData) {
    return <div>Aucun arbre de compétences trouvé</div>;
  }
  
  return (
    <div style={{ width: '100%', height: '80vh' }}>
      <h2>Arbre de Compétences</h2>
      <div style={{ width: '100%', height: '100%' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <Background />
        </ReactFlow>
      </div>
    </div>
  );
};

export default CompetenceTreeView;