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

  const nodeRadius = node.is_anchor ? 60 : 40;
  
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
        dy="8" 
        fontSize="24"
        fill="white"
        style={{ pointerEvents: 'none' }}
      >
        {getNodeIcon()}
      </text>
      <text
        x="0"
        y={nodeRadius + 25}
        textAnchor="middle"
        fontSize="14"
        fill="#ffffff"
        fontWeight="600"
        style={{ pointerEvents: 'none' }}
      >
        {displayLabel.length > 20 ? displayLabel.substring(0, 20) + '...' : displayLabel}
      </text>
      {node.xp_reward && (
        <text
          x="0"
          y={nodeRadius + 45}
          textAnchor="middle"
          fontSize="12"
          fill="#10b981"
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

// Function to calculate clean hierarchical tree layout like the inspiration image
const calculateRadialTreeLayout = (nodes: CompetenceNode[], edges: { source: string; target: string }[]): PositionedNode[] => {
  console.log("Layout calculation - Nodes:", nodes.length, "Edges:", edges.length);
  
  const centerX = 1000;
  const centerY = 700;
  const positioned: PositionedNode[] = [];
  
  // Filter to only visible nodes
  const visibleNodes = nodes.filter(n => n.visible !== false);
  const anchors = visibleNodes.filter(n => n.is_anchor);
  
  console.log("Visible nodes:", visibleNodes.length, "Anchors:", anchors.length);
  
  // Build adjacency map for hierarchy
  const adjacencyMap = new Map<string, string[]>();
  const parentMap = new Map<string, string>(); // Track parent relationships
  
  edges.forEach(edge => {
    const sourceVisible = visibleNodes.find(n => n.id === edge.source);
    const targetVisible = visibleNodes.find(n => n.id === edge.target);
    
    if (sourceVisible && targetVisible) {
      if (!adjacencyMap.has(edge.source)) adjacencyMap.set(edge.source, []);
      adjacencyMap.get(edge.source)!.push(edge.target);
      parentMap.set(edge.target, edge.source);
    }
  });
  
  // Build tree hierarchy starting from anchors
  const treeHierarchy = new Map<number, CompetenceNode[]>(); // level -> nodes
  const processedNodes = new Set<string>();
  
  // Level 0: Anchors - position in center with generous spacing
  if (anchors.length > 0) {
    treeHierarchy.set(0, anchors);
    
    if (anchors.length === 1) {
      // Single anchor in center
      positioned.push({
        ...anchors[0],
        x: centerX,
        y: centerY
      });
    } else {
      // Multiple anchors in circle with large radius
      const anchorRadius = 150;
      anchors.forEach((anchor, index) => {
        const angle = (2 * Math.PI * index) / anchors.length;
        positioned.push({
          ...anchor,
          x: centerX + anchorRadius * Math.cos(angle),
          y: centerY + anchorRadius * Math.sin(angle)
        });
      });
    }
    
    anchors.forEach(anchor => processedNodes.add(anchor.id));
  }
  
  // Build subsequent levels with proper hierarchy
  let currentLevel = 0;
  const maxLevels = 3;
  
  while (currentLevel < maxLevels) {
    const currentLevelNodes = treeHierarchy.get(currentLevel) || [];
    const nextLevelNodes: CompetenceNode[] = [];
    
    // Find children of current level nodes
    currentLevelNodes.forEach(parent => {
      const children = (adjacencyMap.get(parent.id) || [])
        .map(id => visibleNodes.find(n => n.id === id))
        .filter(node => node && !processedNodes.has(node.id))
        .slice(0, 3); // Max 3 children per parent to avoid clutter
      
      nextLevelNodes.push(...children as CompetenceNode[]);
      children.forEach(child => child && processedNodes.add(child.id));
    });
    
    if (nextLevelNodes.length === 0) break;
    
    treeHierarchy.set(currentLevel + 1, nextLevelNodes);
    currentLevel++;
  }
  
  // Position nodes level by level with clean spacing
  for (let level = 1; level <= currentLevel; level++) {
    const levelNodes = treeHierarchy.get(level) || [];
    const baseRadius = 300 + (level - 1) * 200; // Increase radius per level
    
    // Group nodes by their parent for proper positioning
    const nodesByParent = new Map<string, CompetenceNode[]>();
    levelNodes.forEach(node => {
      const parent = parentMap.get(node.id);
      if (parent) {
        if (!nodesByParent.has(parent)) nodesByParent.set(parent, []);
        nodesByParent.get(parent)!.push(node);
      }
    });
    
    // Position children around their parents
    nodesByParent.forEach((children, parentId) => {
      const parent = positioned.find(p => p.id === parentId);
      if (!parent) return;
      
      // Calculate parent's angle from center
      const parentAngle = Math.atan2(parent.y - centerY, parent.x - centerX);
      
      if (children.length === 1) {
        // Single child: extend directly outward from parent
        positioned.push({
          ...children[0],
          x: centerX + baseRadius * Math.cos(parentAngle),
          y: centerY + baseRadius * Math.sin(parentAngle)
        });
      } else {
        // Multiple children: spread around parent direction
        const spreadAngle = Math.PI / 4; // 45 degrees spread
        const angleStep = spreadAngle / Math.max(children.length - 1, 1);
        
        children.forEach((child, index) => {
          const childAngle = parentAngle - spreadAngle / 2 + angleStep * index;
          positioned.push({
            ...child,
            x: centerX + baseRadius * Math.cos(childAngle),
            y: centerY + baseRadius * Math.sin(childAngle)
          });
        });
      }
    });
  }
  
  console.log("Positioned nodes:", positioned.length, "of", visibleNodes.length, "visible");
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
  
  const svgWidth = 2000;
  const svgHeight = 1400;

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ textAlign: 'center', margin: '20px 0' }}>Arbre de Compétences</h2>
      
      <div style={{ flex: 1, display: 'flex' }}>
        {/* SVG Tree Visualization */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          <svg 
            width={svgWidth} 
            height={svgHeight}
            style={{ background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', border: '1px solid #e2e8f0' }}
          >
            {/* Render clean hierarchical edges */}
            {positionedNodes.map((sourceNode) => {
              const outgoingEdges = treeData.edges.filter(edge => 
                edge.source === sourceNode.id &&
                positionedNodes.find(n => n.id === edge.target)
              );
              
              return outgoingEdges.map((edge) => {
                const targetNode = positionedNodes.find(n => n.id === edge.target);
                if (!targetNode) return null;
                
                // Calculate clean curved paths like inspiration image
                const dx = targetNode.x - sourceNode.x;
                const dy = targetNode.y - sourceNode.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                // Create subtle curve for better visual flow
                const midX = (sourceNode.x + targetNode.x) / 2;
                const midY = (sourceNode.y + targetNode.y) / 2;
                const curveOffset = distance * 0.1; // Gentle curve
                const perpX = -dy / distance * curveOffset;
                const perpY = dx / distance * curveOffset;
                
                const pathData = `M ${sourceNode.x} ${sourceNode.y} Q ${midX + perpX} ${midY + perpY} ${targetNode.x} ${targetNode.y}`;
                
                return (
                  <path
                    key={`${sourceNode.id}-${targetNode.id}`}
                    d={pathData}
                    stroke="#64748b"
                    strokeWidth="2"
                    strokeOpacity="0.7"
                    fill="none"
                    style={{
                      filter: 'drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))'
                    }}
                  />
                );
              });
            }).flat()}
            
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