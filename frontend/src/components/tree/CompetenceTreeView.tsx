import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

// Importez les styles existants si nécessaire
import '../tree/treestyles.css';

// Composant pour afficher un défi
import ChallengeCard from '../ui/ChallengeCard';
import NodeDetailModal from './NodeDetailModal';
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
  isSaved?: boolean;
}> = ({ node, onComplete, onNodeClick, isSaved = false }) => {
  const [showTooltip, setShowTooltip] = React.useState(false);
  const displayLabel = node.label || node.skill_label || "Unknown Skill";
  
  const getNodeColor = () => {
    if (isSaved && node.type === "occupation") return "#fbbf24"; // Gold for saved jobs
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
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
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
      
      {/* Saved job indicator */}
      {isSaved && node.type === "occupation" && (
        <circle
          r="8"
          cx={-nodeRadius + 10}
          cy={-nodeRadius + 10}
          fill="#fbbf24"
          stroke="#fff"
          strokeWidth="2"
        />
      )}
      
      {/* Hover tooltip for challenge */}
      {showTooltip && node.challenge && (
        <g>
          {/* Tooltip background */}
          <rect
            x={nodeRadius + 10}
            y={-40}
            width="300"
            height="60"
            fill="rgba(0, 0, 0, 0.9)"
            stroke="#e2e8f0"
            strokeWidth="1"
            rx="8"
            style={{ filter: 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.2))' }}
          />
          {/* Tooltip text */}
          <text
            x={nodeRadius + 20}
            y={-25}
            fill="white"
            fontSize="12"
            fontWeight="600"
          >
            Challenge:
          </text>
          <text
            x={nodeRadius + 20}
            y={-10}
            fill="#e2e8f0"
            fontSize="11"
            style={{ wordWrap: 'break-word' }}
          >
            {node.challenge.length > 45 ? node.challenge.substring(0, 45) + '...' : node.challenge}
          </text>
          {node.xp_reward && (
            <text
              x={nodeRadius + 20}
              y={5}
              fill="#10b981"
              fontSize="11"
              fontWeight="600"
            >
              Reward: {node.xp_reward} XP
            </text>
          )}
        </g>
      )}
    </g>
  );
};

// Function to calculate clean hierarchical tree layout like the inspiration image
const calculateRadialTreeLayout = (nodes: CompetenceNode[], edges: { source: string; target: string }[]): PositionedNode[] => {
  console.log("=== LAYOUT CALCULATION DEBUG ===");
  console.log("Input - Total nodes:", nodes.length, "Total edges:", edges.length);
  
  // Log all nodes to understand what we're working with
  console.log("All nodes:", nodes.map(n => ({
    id: n.id,
    label: n.label || n.skill_label,
    is_anchor: n.is_anchor,
    visible: n.visible,
    type: n.type
  })));
  
  console.log("All edges:", edges);
  
  // Calculate center based on actual viewport size (with SSR safety)
  const centerX = typeof window !== 'undefined' ? Math.max(1600, window.innerWidth * 0.75) : 1600;
  const centerY = typeof window !== 'undefined' ? Math.max(1100, window.innerHeight * 0.75) : 1100;
  const positioned: PositionedNode[] = [];
  
  // Show ALL nodes that have visible !== false (including undefined visible)
  const visibleNodes = nodes.filter(n => n.visible !== false);
  const anchors = visibleNodes.filter(n => n.is_anchor);
  const nonAnchors = visibleNodes.filter(n => !n.is_anchor);
  
  console.log("Filtered - Visible nodes:", visibleNodes.length, "Anchors:", anchors.length, "Non-anchors:", nonAnchors.length);
  
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
  
  console.log("Adjacency map:", Object.fromEntries(adjacencyMap));
  console.log("Parent map:", Object.fromEntries(parentMap));
  
  // Build tree hierarchy starting from anchors
  const treeHierarchy = new Map<number, CompetenceNode[]>(); // level -> nodes
  const processedNodes = new Set<string>();
  
  // Level 0: Position ALL anchors
  if (anchors.length > 0) {
    treeHierarchy.set(0, anchors);
    
    if (anchors.length === 1) {
      positioned.push({
        ...anchors[0],
        x: centerX,
        y: centerY
      });
    } else {
      const anchorRadius = typeof window !== 'undefined' ? Math.max(300, window.innerWidth * 0.2) : 300;
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
    console.log("Level 0 (anchors) positioned:", anchors.length);
  }
  
  // Build subsequent levels - increase max levels and remove child limits
  let currentLevel = 0;
  const maxLevels = 5; // Increase to show more levels
  
  while (currentLevel < maxLevels) {
    const currentLevelNodes = treeHierarchy.get(currentLevel) || [];
    const nextLevelNodes: CompetenceNode[] = [];
    
    // Find ALL children of current level nodes (no limits)
    currentLevelNodes.forEach(parent => {
      const children = (adjacencyMap.get(parent.id) || [])
        .map(id => visibleNodes.find(n => n.id === id))
        .filter(node => node && !processedNodes.has(node.id));
      
      console.log(`Level ${currentLevel} parent ${parent.label || parent.id} has ${children.length} children:`, 
        children.map(c => c?.label || c?.id));
      
      nextLevelNodes.push(...children as CompetenceNode[]);
      children.forEach(child => child && processedNodes.add(child.id));
    });
    
    if (nextLevelNodes.length === 0) {
      console.log(`No more children at level ${currentLevel + 1}, stopping`);
      break;
    }
    
    treeHierarchy.set(currentLevel + 1, nextLevelNodes);
    console.log(`Level ${currentLevel + 1} has ${nextLevelNodes.length} nodes`);
    currentLevel++;
  }
  
  // Position nodes level by level with clean spacing
  for (let level = 1; level <= currentLevel; level++) {
    const levelNodes = treeHierarchy.get(level) || [];
    const baseRadius = (typeof window !== 'undefined' ? Math.max(500, window.innerWidth * 0.3) : 500) + (level - 1) * (typeof window !== 'undefined' ? Math.max(300, window.innerHeight * 0.2) : 300);
    
    console.log(`Positioning level ${level} with ${levelNodes.length} nodes at radius ${baseRadius}`);
    
    // Group nodes by their parent for proper positioning
    const nodesByParent = new Map<string, CompetenceNode[]>();
    levelNodes.forEach(node => {
      const parent = parentMap.get(node.id);
      if (parent) {
        if (!nodesByParent.has(parent)) nodesByParent.set(parent, []);
        nodesByParent.get(parent)!.push(node);
      }
    });
    
    console.log(`Level ${level} nodes grouped by parent:`, Object.fromEntries(nodesByParent));
    
    // Position children around their parents
    nodesByParent.forEach((children, parentId) => {
      const parent = positioned.find(p => p.id === parentId);
      if (!parent) {
        console.log(`Parent ${parentId} not found in positioned nodes!`);
        return;
      }
      
      // Calculate parent's angle from center
      const parentAngle = Math.atan2(parent.y - centerY, parent.x - centerX);
      
      if (children.length === 1) {
        // Single child: extend directly outward from parent
        const child = children[0];
        positioned.push({
          ...child,
          x: centerX + baseRadius * Math.cos(parentAngle),
          y: centerY + baseRadius * Math.sin(parentAngle)
        });
        console.log(`Positioned single child ${child.label || child.id} of ${parent.label || parent.id}`);
      } else {
        // Multiple children: spread around parent direction with wider spread
        const spreadAngle = Math.PI / 2; // 90 degrees spread (much wider)
        const angleStep = spreadAngle / Math.max(children.length - 1, 1);
        
        children.forEach((child, index) => {
          const childAngle = parentAngle - spreadAngle / 2 + angleStep * index;
          positioned.push({
            ...child,
            x: centerX + baseRadius * Math.cos(childAngle),
            y: centerY + baseRadius * Math.sin(childAngle)
          });
          console.log(`Positioned child ${index + 1}/${children.length}: ${child.label || child.id} of ${parent.label || parent.id}`);
        });
      }
    });
  }
  
  // Check for any orphaned nodes (visible but not positioned)
  const orphanedNodes = visibleNodes.filter(node => !positioned.find(p => p.id === node.id));
  if (orphanedNodes.length > 0) {
    console.log("WARNING: Orphaned nodes not positioned:", orphanedNodes.map(n => ({
      id: n.id,
      label: n.label || n.skill_label,
      is_anchor: n.is_anchor
    })));
    
    // Position orphaned nodes in outer ring
    orphanedNodes.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / orphanedNodes.length;
      const outerRadius = (typeof window !== 'undefined' ? Math.max(800, window.innerWidth * 0.4) : 800) + currentLevel * (typeof window !== 'undefined' ? Math.max(350, window.innerHeight * 0.25) : 350);
      positioned.push({
        ...node,
        x: centerX + outerRadius * Math.cos(angle),
        y: centerY + outerRadius * Math.sin(angle)
      });
    });
  }
  
  console.log("=== FINAL LAYOUT RESULT ===");
  console.log("Positioned nodes:", positioned.length, "of", visibleNodes.length, "visible");
  console.log("Tree levels created:", currentLevel);
  
  return positioned;
};

const CompetenceTreeView: React.FC<CompetenceTreeViewProps> = ({ graphId }) => {
  console.log("CompetenceTreeView: Composant chargé avec graphId:", graphId);
  
  const [treeData, setTreeData] = useState<CompetenceTreeData | null>(null);
  const [positionedNodes, setPositionedNodes] = useState<PositionedNode[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<PositionedNode | null>(null);
  const [showNodeModal, setShowNodeModal] = useState<boolean>(false);
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());
  const [zoom, setZoom] = useState<number>(1);
  const [panX, setPanX] = useState<number>(0);
  const [panY, setPanY] = useState<number>(0);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [lastMousePos, setLastMousePos] = useState<{x: number, y: number}>({x: 0, y: 0});
  
  // Calculate dimensions based on viewport (with SSR safety)
  const svgWidth = typeof window !== 'undefined' ? Math.max(3200, window.innerWidth * 1.5) : 3200;
  const svgHeight = typeof window !== 'undefined' ? Math.max(2200, window.innerHeight * 1.5) : 2200;
  
  // Function to automatically save the tree as an image
  const saveTreeAsImage = useCallback(() => {
    try {
      const svgElement = document.querySelector('svg');
      if (!svgElement) {
        console.error('SVG element not found');
        return;
      }

      // Create a canvas element
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = svgWidth;
      canvas.height = svgHeight;

      // Convert SVG to data URL
      const svgData = new XMLSerializer().serializeToString(svgElement);
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
      const svgUrl = URL.createObjectURL(svgBlob);

      // Create an image and draw it on canvas
      const img = new Image();
      img.onload = function() {
        if (ctx) {
          ctx.drawImage(img, 0, 0);
          
          // Convert canvas to blob and download
          canvas.toBlob(function(blob) {
            if (blob) {
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = `competence-tree-${new Date().getTime()}.png`;
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              URL.revokeObjectURL(url);
              console.log('Tree saved successfully as image');
            }
          }, 'image/png');
        }
        URL.revokeObjectURL(svgUrl);
      };
      img.src = svgUrl;
    } catch (error) {
      console.error('Error saving tree as image:', error);
    }
  }, [svgWidth, svgHeight]);
  
  // Fonction pour charger l'arbre de compétences
  const loadCompetenceTree = useCallback(async () => {
    console.log("loadCompetenceTree: Début du chargement avec graphId:", graphId);
    if (!graphId) {
      console.log("loadCompetenceTree: Pas de graphId, abandon du chargement");
      return;
    }
    
    try {
      setLoading(true);
      
      // Check localStorage first for cached tree data
      const cachedTreeData = localStorage.getItem(`competence-tree-${graphId}`);
      if (cachedTreeData) {
        console.log("loadCompetenceTree: Found cached tree data, using it");
        const data = JSON.parse(cachedTreeData);
        setTreeData(data);
        const positioned = calculateRadialTreeLayout(data.nodes, data.edges);
        setPositionedNodes(positioned);
        setLoading(false);
        return;
      }
      
      console.log("loadCompetenceTree: No cached data, fetching from API with graphId:", graphId);
      const data = await getCompetenceTree(graphId);
      console.log("loadCompetenceTree: Données reçues:", data);
      console.log("loadCompetenceTree: Nombre de nodes:", data.nodes?.length || 0);
      console.log("loadCompetenceTree: Nombre d'edges:", data.edges?.length || 0);
      
      // Debug node visibility
      const allNodes = data.nodes || [];
      const anchors = allNodes.filter(n => n.is_anchor);
      const visibleNodes = allNodes.filter(n => n.visible !== false);
      const hiddenNodes = allNodes.filter(n => n.visible === false);
      
      console.log("DEBUG - All anchors:", anchors.map(a => ({
        id: a.id,
        label: a.label || a.skill_label,
        visible: a.visible,
        is_anchor: a.is_anchor
      })));
      
      console.log("DEBUG - Visible vs Hidden nodes:", {
        total: allNodes.length,
        anchors: anchors.length,
        visible: visibleNodes.length,
        hidden: hiddenNodes.length,
        visibleAnchors: anchors.filter(a => a.visible !== false).length
      });
      
      // Debug edge connections for anchors
      anchors.forEach(anchor => {
        const outgoingEdges = (data.edges || []).filter(e => e.source === anchor.id);
        const incomingEdges = (data.edges || []).filter(e => e.target === anchor.id);
        console.log(`Anchor ${anchor.label || anchor.id}:`, {
          outgoing: outgoingEdges.length,
          incoming: incomingEdges.length,
          totalConnections: outgoingEdges.length + incomingEdges.length
        });
      });
      
      setTreeData(data);
      
      // Save tree data to localStorage for persistence
      localStorage.setItem(`competence-tree-${graphId}`, JSON.stringify(data));
      
      // Calculate positions using radial layout
      const positioned = calculateRadialTreeLayout(data.nodes, data.edges);
      setPositionedNodes(positioned);
      setLoading(false);
      
      // Automatically save the tree after it's loaded and positioned
      setTimeout(() => {
        saveTreeAsImage();
      }, 2000); // Wait 2 seconds for rendering to complete
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
    setShowNodeModal(true);
  };

  const handleCloseModal = () => {
    setShowNodeModal(false);
    setSelectedNode(null);
  };

  const handleJobSaved = (node: CompetenceNode) => {
    setSavedJobs(prev => new Set([...prev, node.id]));
  };

  // Zoom and pan handlers with smooth transitions
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    
    // Get the SVG bounding box to calculate mouse position relative to SVG
    const svgRect = e.currentTarget.getBoundingClientRect();
    const mouseX = e.clientX - svgRect.left;
    const mouseY = e.clientY - svgRect.top;
    
    // Much smaller zoom increments for smoother zooming
    const zoomStep = 0.03; // Even smaller for ultra-smooth zooming
    const zoomDirection = e.deltaY > 0 ? -1 : 1;
    
    setZoom(prev => {
      const newZoom = prev + (zoomStep * zoomDirection);
      const clampedZoom = Math.max(0.2, Math.min(4, newZoom));
      
      // Calculate zoom towards mouse position
      if (clampedZoom !== prev) {
        const zoomRatio = clampedZoom / prev;
        const deltaX = (mouseX - panX) * (1 - zoomRatio);
        const deltaY = (mouseY - panY) * (1 - zoomRatio);
        
        setPanX(currentPanX => currentPanX + deltaX);
        setPanY(currentPanY => currentPanY + deltaY);
      }
      
      return clampedZoom;
    });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setLastMousePos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    
    const deltaX = e.clientX - lastMousePos.x;
    const deltaY = e.clientY - lastMousePos.y;
    
    setPanX(prev => prev + deltaX);
    setPanY(prev => prev + deltaY);
    
    setLastMousePos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const resetView = () => {
    setZoom(1);
    setPanX(0);
    setPanY(0);
  };

  const zoomIn = () => {
    setZoom(prev => Math.min(4, prev + 0.2));
  };

  const zoomOut = () => {
    setZoom(prev => Math.max(0.2, prev - 0.2));
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

  return (
    <div style={{ 
      width: '100vw',
      height: '100vh',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 1000,
      display: 'flex', 
      flexDirection: 'column',
      background: '#f8fafc'
    }}>
      {/* Header bar */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        padding: '12px 24px',
        background: 'rgba(255, 255, 255, 0.98)',
        borderBottom: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        zIndex: 1001
      }}>
        <div className="flex items-center gap-4">
          <button
            onClick={() => window.history.back()}
            style={{
              background: '#6b7280',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            ← Back
          </button>
          <h1 style={{ margin: 0, fontSize: '20px', color: '#1f2937', fontWeight: '600' }}>
            Competence Tree Explorer
          </h1>
        </div>
        
        <div className="flex items-center gap-3">
          <span style={{ 
            fontSize: '14px', 
            color: '#6b7280',
            background: '#f3f4f6',
            padding: '6px 12px',
            borderRadius: '6px'
          }}>
            {positionedNodes.length} nodes • Zoom: {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={zoomOut}
            style={{
              background: '#6b7280',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px 0 0 6px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '500',
              borderRight: '1px solid #4b5563'
            }}
          >
            −
          </button>
          <button
            onClick={zoomIn}
            style={{
              background: '#6b7280',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '0 6px 6px 0',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '500',
              marginRight: '8px'
            }}
          >
            +
          </button>
          <button
            onClick={resetView}
            style={{
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
          >
            🎯 Reset View
          </button>
          <button
            onClick={saveTreeAsImage}
            style={{
              background: '#10b981',
              color: 'white',
              border: 'none',
              padding: '10px 16px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              boxShadow: '0 2px 4px rgba(16, 185, 129, 0.2)'
            }}
          >
            💾 Save Tree
          </button>
        </div>
      </div>
      
      {/* Full screen tree visualization */}
      <div style={{ 
        flex: 1,
        width: '100vw',
        height: 'calc(100vh - 60px)',
        overflow: 'auto',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
        position: 'relative'
      }}>
        <svg 
          width={svgWidth} 
          height={svgHeight}
          style={{ 
            background: 'transparent',
            display: 'block',
            cursor: isDragging ? 'grabbing' : 'grab'
          }}
          onWheel={handleWheel}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <g 
            transform={`translate(${panX}, ${panY}) scale(${zoom})`}
            style={{
              transition: isDragging ? 'none' : 'transform 0.15s ease-out',
              transformOrigin: 'center'
            }}
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
                isSaved={savedJobs.has(node.id)}
              />
            ))}
          </g>
        </svg>
        
        {/* Node Detail Modal */}
        {showNodeModal && selectedNode && (
          <NodeDetailModal
            node={selectedNode}
            graphId={treeData?.graph_id}
            onClose={handleCloseModal}
            onCompleteChallenge={handleCompleteChallenge}
            onSaveJob={handleJobSaved}
          />
        )}
      </div>
    </div>
  );
};

export default CompetenceTreeView;