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
    baseClass += ` depth-${depth}`;
    baseClass += ` ${state}`;
    return baseClass;
  };

  const getNodeIcon = () => {
    if (type === "occupation") return "💼";
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
        {type !== "occupation" && challenge && (
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
  // Separate nodes by type and depth
  const anchors = nodes.filter(n => n.is_anchor);
  const skills = nodes.filter(n => !n.is_anchor && n.type === 'skill');
  const occupations = nodes.filter(n => n.type === 'occupation');
  
  const positioned: Node[] = [];
  const centerX = 800;
  const centerY = 400;
  
  // Position anchor nodes in a small circle at the center (like the inspiration image)
  const anchorRadius = 120;
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
  
  // Position related skills around each anchor in branches
  anchors.forEach((anchor, anchorIndex) => {
    // Find skills connected to this anchor
    const connectedSkills = skills.filter(skill => 
      edges.some(edge => 
        (edge.source === anchor.id && edge.target === skill.id) ||
        (edge.target === anchor.id && edge.source === skill.id)
      )
    );
    
    if (connectedSkills.length > 0) {
      // Create a branch for each anchor
      const branchAngleStart = (2 * Math.PI * anchorIndex) / anchors.length - Math.PI / 6;
      const branchAngleEnd = (2 * Math.PI * anchorIndex) / anchors.length + Math.PI / 6;
      const branchAngleStep = (branchAngleEnd - branchAngleStart) / (connectedSkills.length + 1);
      
      connectedSkills.forEach((skill, skillIndex) => {
        const angle = branchAngleStart + branchAngleStep * (skillIndex + 1);
        const distance = 250 + (skill.depth * 100); // Vary distance by depth
        const x = centerX + distance * Math.cos(angle);
        const y = centerY + distance * Math.sin(angle);
        
        positioned.push({
          id: skill.id,
          type: 'customNode',
          position: { x, y },
          data: {
            ...skill,
            onComplete: () => {} // Will be set later
          }
        });
      });
    }
  });
  
  // Position unconnected skills in outer rings
  const unconnectedSkills = skills.filter(skill => 
    !edges.some(edge => 
      edge.source === skill.id || edge.target === skill.id
    )
  );
  
  if (unconnectedSkills.length > 0) {
    const outerRadius = 400;
    unconnectedSkills.forEach((skill, index) => {
      const angle = (2 * Math.PI * index) / unconnectedSkills.length;
      const x = centerX + outerRadius * Math.cos(angle);
      const y = centerY + outerRadius * Math.sin(angle);
      
      positioned.push({
        id: skill.id,
        type: 'customNode',
        position: { x, y },
        data: {
          ...skill,
          onComplete: () => {} // Will be set later
        }
      });
    });
  }
  
  // Position occupations in the outer edge
  if (occupations.length > 0) {
    const occupationRadius = 550;
    occupations.forEach((occupation, index) => {
      // Try to position near connected anchor
      let angle = (2 * Math.PI * index) / occupations.length;
      
      // Find connected anchor for better positioning
      const connectedAnchor = anchors.find(anchor =>
        edges.some(edge =>
          (edge.source === anchor.id && edge.target === occupation.id) ||
          (edge.target === anchor.id && edge.source === occupation.id)
        )
      );
      
      if (connectedAnchor) {
        const anchorIndex = anchors.indexOf(connectedAnchor);
        angle = (2 * Math.PI * anchorIndex) / anchors.length + (Math.PI / 4) * (index % 2 === 0 ? 1 : -1);
      }
      
      const x = centerX + occupationRadius * Math.cos(angle);
      const y = centerY + occupationRadius * Math.sin(angle);
      
      positioned.push({
        id: occupation.id,
        type: 'customNode',
        position: { x, y },
        data: {
          ...occupation,
          onComplete: () => {} // Will be set later
        }
      });
    });
  }
  
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