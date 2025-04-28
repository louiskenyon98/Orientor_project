import { Node, Edge } from 'reactflow';

// Define the TreeNode interface that matches the backend schema
export interface TreeNode {
  id: string;
  label: string;
  type: "root" | "skill" | "outcome" | "career";
  level: number;
  actions?: string[];
  children?: TreeNode[];
}

// Define the node types for custom styling
export const NODE_TYPES = {
  root: 'rootNode',
  skill: 'skillNode',
  outcome: 'outcomeNode',
  career: 'careerNode',
};

// Helper to convert the tree to ReactFlow nodes and edges
export function convertToFlowGraph(tree: TreeNode) {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  
  // Layout constants
  const X_SPACING = 250;
  const Y_SPACING = 150;
  
  let nodeCount = 0;
  
  // Recursive function to traverse the tree and build nodes and edges
  function processNode(node: TreeNode, depth: number, parentId?: string, xOffset = 0) {
    const id = node.id;
    nodeCount++;
    
    // Create node with appropriate type and data
    nodes.push({
      id,
      type: NODE_TYPES[node.type],  // Custom node type for styling
      data: { 
        label: node.label, 
        actions: node.actions,
        nodeType: node.type,
      },
      position: { x: xOffset, y: depth * Y_SPACING }
    });
    
    // Create edge from parent to this node
    if (parentId) {
      edges.push({
        id: `${parentId}-${id}`,
        source: parentId,
        target: id,
        type: 'smoothstep',  // Smooth transitions between nodes
      });
    }
    
    // Process children
    if (node.children && node.children.length > 0) {
      const childWidth = X_SPACING * Math.pow(3, 3 - depth);  // Width changes based on depth
      const startX = xOffset - (childWidth * (node.children.length - 1)) / 2;
      
      // Process each child
      node.children.forEach((child, index) => {
        const childX = startX + index * childWidth;
        processNode(child, depth + 1, id, childX);
      });
    }
  }
  
  // Start processing from the root node
  processNode(tree, 0);
  
  return { nodes, edges };
}

// Helper to get the appropriate node style based on node type
export function getNodeStyle(type: string) {
  switch (type) {
    case 'root':
      return {
        background: '#6366f1', // Indigo
        color: 'white',
        borderRadius: '50%',
        width: 120,
        height: 120,
        fontSize: '14px',
        fontWeight: 'bold',
      };
    case 'skill':
      return {
        background: '#3b82f6', // Blue
        color: 'white',
        borderRadius: '8px',
        width: 160,
        padding: '10px',
        fontSize: '14px',
      };
    case 'outcome':
      return {
        background: '#10b981', // Emerald
        color: 'white',
        borderRadius: '12px',
        width: 180,
        padding: '10px',
        fontSize: '15px',
        fontWeight: 'bold',
      };
    case 'career':
      return {
        background: '#f59e0b', // Amber
        color: 'white',
        borderRadius: '8px',
        width: 150,
        padding: '8px',
        fontSize: '13px',
      };
    default:
      return {
        background: '#9ca3af', // Gray
        color: 'white',
        borderRadius: '4px',
      };
  }
} 