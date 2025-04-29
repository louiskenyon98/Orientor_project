import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  ConnectionLineType,
  Panel,
  NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { CareerDomainNode, CareerFamilyNode, CareerSkillNode } from './CareerNodes';
import { motion } from 'framer-motion';
import { careerTreeService, CareerTreeNode } from '../../services/careerTreeService';

// Custom node types
const nodeTypes: NodeTypes = {
  careerDomain: CareerDomainNode,
  careerFamily: CareerFamilyNode,
  careerSkill: CareerSkillNode,
};

// Animation variants for the title
const titleVariants = {
  hidden: { opacity: 0, y: -20 },
  visible: { 
    opacity: 1, 
    y: 0, 
    transition: { 
      duration: 0.8, 
      ease: "easeOut"
    } 
  }
};

// Default profile placeholder text
const PROFILE_PLACEHOLDER = `Tell us about your interests and aspirations.
For example:
- What subjects do you enjoy?
- What skills are you good at?
- What careers are you curious about?`;

// Convert API tree data to ReactFlow nodes and edges
function convertTreeToReactFlow(treeData: CareerTreeNode): { nodes: Node[], edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  
  // Recursively process the tree and build nodes/edges
  const processNode = (node: CareerTreeNode, position = { x: 0, y: 0 }, parentId: string | null = null) => {
    let nodeType = "";
    
    // Map API node types to CareerNodes component types
    switch (node.type) {
      case "root":
        nodeType = "careerDomain"; // We display root as a domain for visual consistency
        break;
      case "domain":
        nodeType = "careerDomain";
        break;
      case "family":
        nodeType = "careerFamily";
        break;
      case "skill":
        nodeType = "careerSkill";
        break;
      default:
        nodeType = "careerDomain"; // Default fallback
    }
    
    // Add the current node
    nodes.push({
      id: node.id,
      type: nodeType,
      data: { 
        label: node.label,
        actions: node.actions
      },
      position
    });
    
    // Add edge from parent to this node if there's a parent
    if (parentId) {
      edges.push({
        id: `${parentId}-${node.id}`,
        source: parentId,
        target: node.id,
        type: 'smoothstep',
        animated: node.level === 1 // Animate connections to first level
      });
    }
    
    // Process children if any
    if (node.children && node.children.length > 0) {
      const childCount = node.children.length;
      const horizontalSpacing = 200; // Space between nodes horizontally
      const verticalSpacing = 150; // Space between levels
      
      // Calculate starting position for children to center them under parent
      const startX = position.x - ((childCount - 1) * horizontalSpacing) / 2;
      const childY = position.y + verticalSpacing;
      
      // Process each child
      node.children.forEach((child, index) => {
        const childX = startX + index * horizontalSpacing;
        processNode(child, { x: childX, y: childY }, node.id);
      });
    }
  };
  
  // Start processing from the root
  processNode(treeData, { x: 400, y: 50 });
  
  return { nodes, edges };
}

export default function CareerTree() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  // Generate tree using the profile input
  const generateTree = useCallback(async () => {
    if (!profile.trim()) {
      setError('Please enter your profile information first');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setIsSubmitted(true);
    
    try {
      const tree = await careerTreeService.generateCareerTree(profile);
      
      // Convert tree data to ReactFlow format
      const { nodes: treeNodes, edges: treeEdges } = convertTreeToReactFlow(tree);
      
      setNodes(treeNodes);
      setEdges(treeEdges);
    } catch (err: any) {
      console.error('Error generating career tree:', err);
      setError(err.message || 'Failed to load career tree. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  }, [profile, setNodes, setEdges]);

  // Handle node click
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  return (
    <div className="w-full h-[calc(100vh-6rem)] bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
      <motion.div 
        className="p-4 text-2xl font-light text-gray-800 border-b border-gray-100"
        initial="hidden"
        animate="visible"
        variants={titleVariants}
      >
        Career Exploration
        <p className="text-sm text-gray-500 mt-1">
          Discover career domains and families that align with your interests
        </p>
      </motion.div>
      
      {!isSubmitted ? (
        <div className="flex-1 p-6 flex flex-col items-center justify-center">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-medium text-gray-800 mb-4">Tell us about yourself</h2>
            <p className="text-gray-600 mb-4">
              Describe your interests, skills, and aspirations to generate a personalized career exploration tree.
            </p>
            <textarea 
              className="w-full h-40 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={PROFILE_PLACEHOLDER}
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
            />
            <div className="mt-4 flex justify-end">
              <button
                onClick={generateTree}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                disabled={isLoading}
              >
                Generate Career Tree
              </button>
            </div>
          </div>
        </div>
      ) : isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-600">Generating your personal career tree...</p>
          </div>
        </div>
      ) : error ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="bg-red-50 p-4 rounded-lg border border-red-200 max-w-md">
            <p className="text-red-700 mb-4">{error}</p>
            <div className="flex space-x-3">
              <button 
                onClick={() => setIsSubmitted(false)}
                className="bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-md hover:bg-gray-50 transition-colors"
              >
                Edit Profile
              </button>
              <button 
                onClick={generateTree}
                className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            connectionLineType={ConnectionLineType.SmoothStep}
            defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
            fitView
            minZoom={0.4}
            maxZoom={1.5}
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#f8fafc" gap={16} size={1} />
            <Controls />
            <Panel position="top-right" className="bg-white p-3 rounded-lg shadow-md border border-gray-100">
              <div className="text-sm text-gray-600">
                <div className="font-medium mb-2">How to use:</div>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Explore different career domains</li>
                  <li>Click on skills to see recommended actions</li>
                  <li>Drag to pan the view and scroll to zoom</li>
                </ul>
                <button
                  onClick={() => setIsSubmitted(false)}
                  className="mt-3 w-full text-blue-600 border border-blue-600 px-2 py-1 rounded-md hover:bg-blue-50 transition-colors text-sm"
                >
                  Edit Profile
                </button>
              </div>
            </Panel>
          </ReactFlow>
        </div>
      )}
    </div>
  );
} 