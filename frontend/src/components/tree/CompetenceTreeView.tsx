import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

// Importez les styles existants si nécessaire
import '../tree/treestyles.css';

// Composant pour afficher un défi
import ChallengeCard from '../ui/ChallengeCard';
import { getCompetenceTree, completeChallenge } from '../../services/competenceTreeService';

// Types personnalisés
interface CompetenceNode {
  id: string;
  skill_id?: string;
  skill_label?: string;
  label?: string;
  type?: string;
  challenge?: string;
  xp_reward?: number;
  visible?: boolean;
  revealed?: boolean;
  state?: 'locked' | 'available' | 'completed' | 'hidden';
  notes?: string;
  is_anchor?: boolean;
  depth?: number;
  metadata?: any;
}

interface CompetenceTreeData {
  nodes: CompetenceNode[];
  edges: { source: string; target: string; weight?: number; type?: string }[];
  graph_id: string;
}

interface CompetenceTreeViewProps {
  graphId: string;
}

interface PositionedNode extends CompetenceNode {
  x: number;
  y: number;
}

// Custom Node Component for SVG rendering
const TreeNode: React.FC<{
  node: PositionedNode;
  onComplete: (nodeId: string) => void;
  onNodeClick: (node: PositionedNode) => void;
}> = ({ node, onComplete, onNodeClick }) => {
  const displayLabel = node.label || node.skill_label || "Unknown Skill";
  
  const getNodeColor = () => {
    if (node.is_anchor) return "#667eea";
    if (node.type === "occupation") return "#f093fb";
    if (node.type === "skillgroup") return "#4facfe";
    return "#48bb78";
  };

  const getNodeIcon = () => {
    if (node.type === "occupation") return "💼";
    if (node.type === "skillgroup") return "📋";
    if (node.is_anchor) return "⭐";
    return "🔧";
  };

  const nodeRadius = node.is_anchor ? 45 : 30;
  
  if (!node.visible) {
    return (
      <g transform={`translate(${node.x}, ${node.y})`}>
        <circle
          r={nodeRadius}
          fill="#f1f5f9"
          stroke="#cbd5e0"
          strokeWidth="2"
          strokeDasharray="5,5"
        />
        <text 
          textAnchor="middle" 
          dy="5" 
          fontSize="20"
          fill="#94a3b8"
        >
          ?
        </text>
      </g>
    );
  }

  return (
    <g transform={`translate(${node.x}, ${node.y})`}>
      <circle
        r={nodeRadius}
        fill={getNodeColor()}
        stroke="#fff"
        strokeWidth="3"
        style={{ 
          cursor: 'pointer',
          filter: 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1))'
        }}
        onClick={() => onNodeClick(node)}
      />
      {/* Glow effect for anchor nodes */}
      {node.is_anchor && (
        <circle
          r={nodeRadius + 5}
          fill="none"
          stroke={getNodeColor()}
          strokeWidth="2"
          strokeOpacity="0.3"
        />
      )}
      <text 
        textAnchor="middle" 
        dy="5" 
        fontSize="16"
        fill="white"
        style={{ pointerEvents: 'none' }}
      >
        {getNodeIcon()}
      </text>
      <text
        x="0"
        y={nodeRadius + 20}
        textAnchor="middle"
        fontSize="11"
        fill="#2d3748"
        fontWeight="500"
        style={{ pointerEvents: 'none' }}
      >
        {displayLabel.length > 18 ? displayLabel.substring(0, 18) + '...' : displayLabel}
      </text>
      {node.xp_reward && (
        <text
          x="0"
          y={nodeRadius + 35}
          textAnchor="middle"
          fontSize="10"
          fill="#059669"
          fontWeight="600"
          style={{ pointerEvents: 'none' }}
        >
          {node.xp_reward} XP
        </text>
      )}
      {/* State indicator */}
      {node.state === 'completed' && (
        <circle
          r="8"
          cx={nodeRadius - 10}
          cy={-nodeRadius + 10}
          fill="#10b981"
          stroke="#fff"
          strokeWidth="2"
        />
      )}
    </g>
  );
};

// Function to calculate radial tree layout
const calculateRadialTreeLayout = (nodes: CompetenceNode[], edges: { source: string; target: string }[]): PositionedNode[] => {
  console.log("Layout calculation - Nodes:", nodes.length, "Edges:", edges.length);
  
  const centerX = 500;
  const centerY = 400;
  const positioned: PositionedNode[] = [];
  
  // Separate anchors and other nodes
  const anchors = nodes.filter(n => n.is_anchor);
  const nonAnchors = nodes.filter(n => !n.is_anchor);
  
  console.log("Anchors:", anchors.length, "Non-anchors:", nonAnchors.length);
  
  // Create edge lookup
  const edgeMap = new Map<string, string[]>();
  edges.forEach(edge => {
    if (!edgeMap.has(edge.source)) edgeMap.set(edge.source, []);
    if (!edgeMap.has(edge.target)) edgeMap.set(edge.target, []);
    edgeMap.get(edge.source)!.push(edge.target);
    edgeMap.get(edge.target)!.push(edge.source);
  });
  
  // Position anchor nodes in center circle
  const anchorRadius = 120;
  anchors.forEach((anchor, index) => {
    const angle = (2 * Math.PI * index) / anchors.length;
    positioned.push({
      ...anchor,
      x: centerX + anchorRadius * Math.cos(angle),
      y: centerY + anchorRadius * Math.sin(angle)
    });
  });
  
  // Track processed nodes
  const processedNodes = new Set(anchors.map(a => a.id));
  
  // For each anchor, create branching layout
  anchors.forEach((anchor, anchorIndex) => {
    const connectedNodeIds = edgeMap.get(anchor.id) || [];
    const connectedNodes = connectedNodeIds
      .filter(id => !processedNodes.has(id))
      .map(id => nodes.find(n => n.id === id))
      .filter(Boolean) as CompetenceNode[];
    
    if (connectedNodes.length === 0) return;
    
    const baseAngle = (2 * Math.PI * anchorIndex) / anchors.length;
    const branchSpread = Math.PI / 2; // 90 degrees per anchor
    
    connectedNodes.forEach((node, nodeIndex) => {
      if (processedNodes.has(node.id)) return;
      
      const nodeAngle = baseAngle - branchSpread / 2 + (branchSpread * nodeIndex) / (connectedNodes.length - 1 || 1);
      
      // Different distances for different node types
      let distance = 250;
      if (node.type === 'occupation') distance = 350;
      if (node.type === 'skillgroup') distance = 200;
      
      positioned.push({
        ...node,
        x: centerX + distance * Math.cos(nodeAngle),
        y: centerY + distance * Math.sin(nodeAngle)
      });
      
      processedNodes.add(node.id);
      
      // Add second level connections
      const secondLevelIds = edgeMap.get(node.id) || [];
      const secondLevelNodes = secondLevelIds
        .filter(id => !processedNodes.has(id))
        .map(id => nodes.find(n => n.id === id))
        .filter(Boolean)
        .slice(0, 2) as CompetenceNode[]; // Limit to 2 per node
      
      secondLevelNodes.forEach((secondNode, secondIndex) => {
        if (processedNodes.has(secondNode.id)) return;
        
        const secondAngle = nodeAngle + (secondIndex - 0.5) * 0.4;
        const secondDistance = distance + 120;
        
        positioned.push({
          ...secondNode,
          x: centerX + secondDistance * Math.cos(secondAngle),
          y: centerY + secondDistance * Math.sin(secondAngle)
        });
        
        processedNodes.add(secondNode.id);
      });
    });
  });
  
  // Position remaining nodes in outer ring
  const remainingNodes = nodes.filter(node => !processedNodes.has(node.id));
  if (remainingNodes.length > 0) {
    remainingNodes.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / remainingNodes.length;
      positioned.push({
        ...node,
        x: centerX + 450 * Math.cos(angle),
        y: centerY + 450 * Math.sin(angle)
      });
    });
  }
  
  console.log("Positioned nodes:", positioned.length);
  return positioned;
};

const CompetenceTreeView: React.FC<CompetenceTreeViewProps> = ({ graphId }) => {
  console.log("CompetenceTreeView: Composant chargé avec graphId:", graphId);
  
  const [treeData, setTreeData] = useState<CompetenceTreeData | null>(null);
  const [positionedNodes, setPositionedNodes] = useState<PositionedNode[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<PositionedNode | null>(null);
  
  // Fonction pour charger l'arbre de compétences
  const loadCompetenceTree = useCallback(async () => {
    console.log("loadCompetenceTree: Début du chargement avec graphId:", graphId);
    if (!graphId) {
      console.log("loadCompetenceTree: Pas de graphId, abandon du chargement");
      return;
    }
    
    try {
      setLoading(true);
      console.log("loadCompetenceTree: Appel à getCompetenceTree avec graphId:", graphId);
      const data = await getCompetenceTree(graphId);
      console.log("loadCompetenceTree: Données reçues:", data);
      console.log("loadCompetenceTree: Nombre de nodes:", data.nodes?.length || 0);
      console.log("loadCompetenceTree: Nombre d'edges:", data.edges?.length || 0);
      
      setTreeData(data);
      
      // Calculate positions using radial layout
      const positioned = calculateRadialTreeLayout(data.nodes, data.edges);
      setPositionedNodes(positioned);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors du chargement de l\'arbre de compétences');
      setLoading(false);
    }
  }, [graphId]);
  
  // Charger l'arbre au montage du composant
  useEffect(() => {
    if (graphId) {
      loadCompetenceTree();
    }
  }, [graphId, loadCompetenceTree]);
  
  // Fonction pour marquer un défi comme complété
  const handleCompleteChallenge = async (nodeId: string) => {
    try {
      const userId = 1; // À adapter selon votre système d'authentification
      await completeChallenge(nodeId, userId);
      
      // Recharger l'arbre pour obtenir les nouveaux nœuds révélés
      loadCompetenceTree();
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors de la complétion du défi');
    }
  };

  const handleNodeClick = (node: PositionedNode) => {
    setSelectedNode(node);
  };
  
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <div>Chargement de l'arbre de compétences...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <div style={{ color: 'red' }}>Erreur: {error}</div>
      </div>
    );
  }
  
  if (!treeData || positionedNodes.length === 0) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <div>Aucun arbre de compétences trouvé</div>
      </div>
    );
  }
  
  const svgWidth = 1000;
  const svgHeight = 800;

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ textAlign: 'center', margin: '20px 0' }}>Arbre de Compétences</h2>
      
      <div style={{ flex: 1, display: 'flex' }}>
        {/* SVG Tree Visualization */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          <svg 
            width={svgWidth} 
            height={svgHeight}
            style={{ background: '#f8fafc', border: '1px solid #e2e8f0' }}
          >
            {/* Render edges first so they appear behind nodes */}
            {treeData.edges.map((edge, index) => {
              const sourceNode = positionedNodes.find(n => n.id === edge.source);
              const targetNode = positionedNodes.find(n => n.id === edge.target);
              
              if (!sourceNode || !targetNode) return null;
              
              // Create curved path for more organic look
              const midX = (sourceNode.x + targetNode.x) / 2;
              const midY = (sourceNode.y + targetNode.y) / 2;
              const dx = targetNode.x - sourceNode.x;
              const dy = targetNode.y - sourceNode.y;
              const distance = Math.sqrt(dx * dx + dy * dy);
              
              // Add curve based on distance
              const curvature = Math.min(distance * 0.2, 50);
              const perpX = -dy / distance * curvature;
              const perpY = dx / distance * curvature;
              
              const controlX = midX + perpX;
              const controlY = midY + perpY;
              
              const pathData = `M ${sourceNode.x} ${sourceNode.y} Q ${controlX} ${controlY} ${targetNode.x} ${targetNode.y}`;
              
              return (
                <path
                  key={index}
                  d={pathData}
                  stroke="#4ade80"
                  strokeWidth="2"
                  strokeOpacity="0.7"
                  fill="none"
                />
              );
            })}
            
            {/* Render nodes */}
            {positionedNodes.map((node) => (
              <TreeNode
                key={node.id}
                node={node}
                onComplete={handleCompleteChallenge}
                onNodeClick={handleNodeClick}
              />
            ))}
          </svg>
        </div>
        
        {/* Node Details Panel */}
        {selectedNode && (
          <div style={{ 
            width: '300px', 
            padding: '20px', 
            background: 'white', 
            borderLeft: '1px solid #e2e8f0',
            overflow: 'auto'
          }}>
            <h3>{selectedNode.label || selectedNode.skill_label || "Unknown Skill"}</h3>
            <p><strong>Type:</strong> {selectedNode.type || 'skill'}</p>
            {selectedNode.is_anchor && <p><strong>🌟 Anchor Skill</strong></p>}
            {selectedNode.xp_reward && <p><strong>XP Reward:</strong> {selectedNode.xp_reward}</p>}
            {selectedNode.challenge && (
              <div>
                <h4>Challenge:</h4>
                <p style={{ fontSize: '14px', lineHeight: '1.4' }}>{selectedNode.challenge}</p>
                {selectedNode.state !== 'completed' && (
                  <button
                    onClick={() => handleCompleteChallenge(selectedNode.id)}
                    style={{
                      background: '#4ade80',
                      color: 'white',
                      border: 'none',
                      padding: '8px 16px',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      marginTop: '10px'
                    }}
                  >
                    Complete Challenge
                  </button>
                )}
              </div>
            )}
            <button
              onClick={() => setSelectedNode(null)}
              style={{
                background: '#e2e8f0',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '4px',
                cursor: 'pointer',
                marginTop: '10px'
              }}
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompetenceTreeView;