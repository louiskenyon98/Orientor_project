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
  const { 
    label, 
    skill_label, 
    challenge, 
    xp_reward, 
    revealed, 
    visible, 
    state, 
    onComplete, 
    type, 
    is_anchor, 
    depth,
    category 
  } = data;
  
  // Use label first, fallback to skill_label
  const displayLabel = label || skill_label || "Unknown Skill";
  
  if (!visible || !revealed) {
    return (
      <div className="competence-node hidden">
        <div className="node-content">
          <span className="question-mark">?</span>
          <div className="tooltip">Complete previous challenges to unlock</div>
        </div>
      </div>
    );
  }
  
  // Different styling based on node type and depth
  const getNodeClass = () => {
    let baseClass = "competence-node";
    if (is_anchor) baseClass += " anchor";
    if (type === "occupation") baseClass += " occupation";
    if (type === "skillgroup") baseClass += " skillgroup";
    baseClass += ` depth-${depth}`;
    baseClass += ` ${state}`;
    return baseClass;
  };

  const getNodeIcon = () => {
    if (type === "occupation") return "💼";
    if (type === "skillgroup") return "📋";
    if (is_anchor) return "⭐";
    switch (category) {
      case "technical": return "⚙️";
      case "interpersonal": return "🤝";
      case "cognitive": return "🧠";
      case "creative": return "🎨";
      case "leadership": return "👑";
      default: return "🔧";
    }
  };
  
  return (
    <div className={getNodeClass()}>
      <div className="node-content">
        <div className="node-header">
          <span className="node-icon">{getNodeIcon()}</span>
          <h4 className="node-title">{displayLabel}</h4>
          {is_anchor && <span className="anchor-badge">ANCHOR</span>}
        </div>
        
        {/* Show XP for skills only */}
        {type !== "occupation" && xp_reward > 0 && (
          <div className="xp-indicator">
            <span className="xp-value">{xp_reward} XP</span>
          </div>
        )}
        
        {/* Show challenge for skills that have them */}
        {type === "skill" && challenge && (
          <ChallengeCard 
            challenge={challenge} 
            xpReward={xp_reward} 
            completed={state === 'completed'} 
            onComplete={onComplete}
          />
        )}
        
        {/* Show occupation info */}
        {type === "occupation" && (
          <div className="occupation-info">
            <p className="occupation-desc">Career Path</p>
            {state !== "completed" && (
              <button 
                className="explore-button"
                onClick={() => {
                  // Navigate to career exploration for this occupation
                  console.log("Explore occupation:", displayLabel);
                }}
              >
                Explore Career
              </button>
            )}
          </div>
        )}
        
        {/* Show skillgroup info */}
        {type === "skillgroup" && (
          <div className="skillgroup-info">
            <p className="skillgroup-desc">Skill Category</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Définir les types de nœuds personnalisés
const nodeTypes: NodeTypes = {
  customNode: CustomNode,
};

// Function to calculate enhanced layout inspired by the competence tree image
const calculateEnhancedTreeLayout = (nodes: CompetenceNode[], edges: { source: string; target: string }[]) => {
  console.log("Layout calculation - Nodes:", nodes.length, "Edges:", edges.length);
  
  // Separate nodes by type and anchor status
  const anchors = nodes.filter(n => n.is_anchor);
  const nonAnchors = nodes.filter(n => !n.is_anchor);
  
  console.log("Anchors:", anchors.length, "Non-anchors:", nonAnchors.length);
  
  const positioned: Node[] = [];
  const centerX = 800;
  const centerY = 400;
  
  // Create edge lookup for faster connection finding
  const edgeMap = new Map();
  edges.forEach(edge => {
    if (!edgeMap.has(edge.source)) edgeMap.set(edge.source, []);
    if (!edgeMap.has(edge.target)) edgeMap.set(edge.target, []);
    edgeMap.get(edge.source).push(edge.target);
    edgeMap.get(edge.target).push(edge.source);
  });
  
  // Position anchor nodes in a central circle (like inspiration image)
  const anchorRadius = 150;
  anchors.forEach((anchor, index) => {
    const angle = (2 * Math.PI * index) / anchors.length;
    const x = centerX + anchorRadius * Math.cos(angle);
    const y = centerY + anchorRadius * Math.sin(angle);
    
    positioned.push({
      id: anchor.id,
      type: 'customNode',
      position: { x, y },
      data: {
        ...anchor,
        onComplete: () => {} // Will be set later
      }
    });
  });
  
  // For each anchor, create branching paths using BFS-like traversal
  const processedNodes = new Set(anchors.map(a => a.id));
  
  anchors.forEach((anchor, anchorIndex) => {
    const connectedNodes = edgeMap.get(anchor.id) || [];
    
    // Find unprocessed connected nodes
    const directConnections = connectedNodes
      .filter(nodeId => !processedNodes.has(nodeId))
      .map(nodeId => nodes.find(n => n.id === nodeId))
      .filter(Boolean);
    
    if (directConnections.length > 0) {
      // Create branching paths from this anchor
      const baseAngle = (2 * Math.PI * anchorIndex) / anchors.length;
      const branchSpread = Math.PI / 3; // 60 degrees spread per anchor
      const angleStep = branchSpread / Math.max(directConnections.length - 1, 1);
      
      directConnections.forEach((node, nodeIndex) => {
        if (processedNodes.has(node.id)) return;
        
        // Calculate branch angle
        const branchAngle = baseAngle - branchSpread / 2 + angleStep * nodeIndex;
        
        // Position based on node type and create depth levels
        let distance = 300; // First level distance
        if (node.type === 'occupation') distance = 450; // Occupations further out
        if (node.type === 'skillgroup') distance = 350; // Skill groups intermediate
        
        const x = centerX + distance * Math.cos(branchAngle);
        const y = centerY + distance * Math.sin(branchAngle);
        
        positioned.push({
          id: node.id,
          type: 'customNode',
          position: { x, y },
          data: {
            ...node,
            onComplete: () => {}
          }
        });
        
        processedNodes.add(node.id);
        
        // For each positioned node, add its connections at the next level
        const secondLevelConnections = (edgeMap.get(node.id) || [])
          .filter(nodeId => !processedNodes.has(nodeId))
          .map(nodeId => nodes.find(n => n.id === nodeId))
          .filter(Boolean)
          .slice(0, 3); // Limit to prevent overcrowding
        
        secondLevelConnections.forEach((secondNode, secondIndex) => {
          if (processedNodes.has(secondNode.id)) return;
          
          const secondAngle = branchAngle + (secondIndex - 1) * 0.3; // Small angle variation
          const secondDistance = distance + 150; // Further out
          
          const secondX = centerX + secondDistance * Math.cos(secondAngle);
          const secondY = centerY + secondDistance * Math.sin(secondAngle);
          
          positioned.push({
            id: secondNode.id,
            type: 'customNode',
            position: { x: secondX, y: secondY },
            data: {
              ...secondNode,
              onComplete: () => {}
            }
          });
          
          processedNodes.add(secondNode.id);
        });
      });
    }
  });
  
  // Position any remaining unconnected nodes in outer ring
  const remainingNodes = nodes.filter(node => !processedNodes.has(node.id));
  if (remainingNodes.length > 0) {
    const outerRadius = 600;
    remainingNodes.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / remainingNodes.length;
      const x = centerX + outerRadius * Math.cos(angle);
      const y = centerY + outerRadius * Math.sin(angle);
      
      positioned.push({
        id: node.id,
        type: 'customNode',
        position: { x, y },
        data: {
          ...node,
          onComplete: () => {}
        }
      });
    });
  }
  
  console.log("Positioned nodes:", positioned.length);
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
      console.log("loadCompetenceTree: Nombre de nodes:", data.nodes?.length || 0);
      console.log("loadCompetenceTree: Nombre d'edges:", data.edges?.length || 0);
      console.log("loadCompetenceTree: Premier node:", data.nodes?.[0]);
      console.log("loadCompetenceTree: Premier edge:", data.edges?.[0]);
      setTreeData(data);
      
      // Convertir les données en format React Flow
      // Use enhanced tree layout inspired by the competence tree image
      const positionedNodes = calculateEnhancedTreeLayout(data.nodes, data.edges);
      
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
        type: 'bezier',
        animated: false,
        style: {
          stroke: '#4ade80', // Green color like inspiration image
          strokeWidth: 3,
          strokeOpacity: 0.8,
        },
        markerEnd: {
          type: 'arrowclosed',
          color: '#4ade80',
          width: 20,
          height: 20,
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