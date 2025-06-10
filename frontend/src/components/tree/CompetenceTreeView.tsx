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
  state: 'locked' | 'available' | 'completed' | 'hidden';
  notes: string;
  is_anchor?: boolean;
  depth?: number;
  label?: string;
  metadata?: any;
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

// Function to calculate half-circle layout positions
const calculateHalfCircleLayout = (nodes: CompetenceNode[], edges: { source: string; target: string }[]) => {
  // Group nodes by depth (distance from anchor nodes)
  const nodeDepths = new Map<string, number>();
  const anchors = nodes.filter(n => n.is_anchor);
  
  // Initialize anchor nodes at depth 0
  anchors.forEach(anchor => nodeDepths.set(anchor.id, 0));
  
  // Calculate depths using BFS
  const queue = [...anchors];
  const visited = new Set<string>(anchors.map(a => a.id));
  
  while (queue.length > 0) {
    const current = queue.shift()!;
    const currentDepth = nodeDepths.get(current.id)!;
    
    // Find connected nodes
    edges.forEach(edge => {
      let targetId = null;
      if (edge.source === current.id && !visited.has(edge.target)) {
        targetId = edge.target;
      } else if (edge.target === current.id && !visited.has(edge.source)) {
        targetId = edge.source;
      }
      
      if (targetId) {
        const targetNode = nodes.find(n => n.id === targetId);
        if (targetNode) {
          nodeDepths.set(targetId, currentDepth + 1);
          visited.add(targetId);
          queue.push(targetNode);
        }
      }
    });
  }
  
  // Group nodes by depth
  const depthGroups = new Map<number, CompetenceNode[]>();
  nodes.forEach(node => {
    const depth = nodeDepths.get(node.id) || 0;
    if (!depthGroups.has(depth)) {
      depthGroups.set(depth, []);
    }
    depthGroups.get(depth)!.push(node);
  });
  
  // Calculate positions
  const centerX = 800;
  const baseY = 600;
  const radiusStep = 150;
  const maxDepth = Math.max(...Array.from(depthGroups.keys()));
  
  const positioned: Node[] = [];
  
  depthGroups.forEach((nodesAtDepth, depth) => {
    const radius = radiusStep * (maxDepth - depth + 1);
    const angleStep = Math.PI / (nodesAtDepth.length + 1); // Divide semicircle
    
    nodesAtDepth.forEach((node, index) => {
      const angle = angleStep * (index + 1);
      const x = centerX + radius * Math.cos(angle);
      const y = baseY - radius * Math.sin(angle); // Negative to go upward
      
      positioned.push({
        id: node.id,
        type: 'customNode',
        position: { x, y },
        data: {
          ...node,
          onComplete: () => {} // Will be set later
        }
      });
    });
  });
  
  return positioned;
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
      // Use half-circle layout to position nodes
      const positionedNodes = calculateHalfCircleLayout(data.nodes, data.edges);
      
      // Update nodes with onComplete handlers
      const flowNodes: Node[] = positionedNodes.map((node) => ({
        ...node,
        data: {
          ...node.data,
          onComplete: () => handleCompleteChallenge(node.id),
        },
      }));
      
      const flowEdges: Edge[] = data.edges.map((edge: any, index: number) => ({
        id: `e${index}`,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: true,
        style: {
          stroke: '#b1b1b7',
          strokeWidth: 2,
        },
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