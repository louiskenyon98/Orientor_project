import React, { useState, useCallback } from 'react';
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
import { SkillNode, OutcomeNode, RootNode } from './CustomNodes';
import { motion } from 'framer-motion';
import { skillsTreeService, SkillsTreeNode } from '../../services/skillsTreeService';
import { convertToFlowGraph } from '../../utils/convertToFlowGraph';
import { saveTreePath } from '../../utils/treeStorage';
import XPProgress from '../ui/XPProgress';

// Define custom node types
const nodeTypes: NodeTypes = {
  skillNode: SkillNode,
  outcomeNode: OutcomeNode,
  rootNode: RootNode,
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

// Default profile placeholder text for technical skills
const TECH_PROFILE_PLACEHOLDER = `Tell us about your technical background and goals.
For example:
- What programming languages or technologies do you know?
- What specific technical field are you interested in? (web dev, data science, mobile apps, etc.)
- What level are you currently at? (beginner, intermediate, advanced)
- What technical skills do you want to develop?`;

export default function EnhancedSkillsTree() {
  // State for the skills tree
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  
  // State for user input and loading
  const [profile, setProfile] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Generate skills tree using the profile input
  const generateSkillsTree = useCallback(async () => {
    if (!profile.trim()) {
      setError('Please enter your technical background and goals first');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setIsSubmitted(true);
    
    try {
      const tree = await skillsTreeService.generateSkillsTree(profile);
      
      // Convert tree data to ReactFlow format using the utility function
      const { nodes: treeNodes, edges: treeEdges } = convertToFlowGraph(tree);
      
      setNodes(treeNodes);
      setEdges(treeEdges);
    } catch (err: any) {
      console.error('Error generating skills tree:', err);
      setError(err.message || 'Failed to load skills tree. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  }, [profile, setNodes, setEdges]);

  // Handle node click
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  // Function to save tree to user's path
  const handleSaveTree = async () => {
    if (!nodes.length) return;
    
    setIsSaving(true);
    setSaveSuccess(false);
    
    try {
      // Find the root node
      const rootNodeId = nodes.find(node => node.type === 'rootNode')?.id || 'root';
      const rootNode = nodes.find(node => node.id === rootNodeId);
      
      if (!rootNode) throw new Error('Root node not found');
      
      // Create a TreeNode structure from the ReactFlow nodes
      const createTreeStructure = (nodeId: string): any => {
        const node = nodes.find(n => n.id === nodeId);
        if (!node) return null;
        
        // Find all child edges
        const childEdges = edges.filter(e => e.source === nodeId);
        const children = childEdges
          .map(edge => createTreeStructure(edge.target))
          .filter(Boolean);
        
        return {
          id: node.id,
          label: node.data?.label || '',
          type: node.type === 'rootNode' ? 'root' : 
                node.type === 'skillNode' ? 'skill' : 'outcome',
          level: node.data?.level || 0,
          actions: node.data?.actions || [],
          children: children.length > 0 ? children : undefined
        };
      };
      
      // Create tree structure starting from root
      const treeStructure = createTreeStructure(rootNodeId);
      
      // Save to backend
      await saveTreePath(treeStructure, 'skills');
      setSaveSuccess(true);
      
      // Hide success message after a few seconds
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    } catch (err: any) {
      console.error('Error saving tree:', err);
      setError(err.message || 'Failed to save tree');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="w-full h-[calc(100vh-6rem)] bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
      <motion.div 
        className="p-4 text-2xl font-light text-gray-800 border-b border-gray-100"
        initial="hidden"
        animate="visible"
        variants={titleVariants}
      >
      </motion.div>
      
      {!isSubmitted ? (
        <div className="flex-1 p-6 flex flex-col items-center justify-center">
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-medium text-gray-800 mb-4">Tell us about your technical journey</h2>
            <textarea 
              className="w-full h-40 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={TECH_PROFILE_PLACEHOLDER}
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
            />
            <div className="mt-4 flex justify-end">
              <button
                onClick={generateSkillsTree}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                disabled={isLoading}
              >
                Generate Skills Path
              </button>
            </div>
          </div>
        </div>
      ) : isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-600">Generating your personalized skills path...</p>
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
                onClick={generateSkillsTree}
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
            defaultViewport={{ x: 0, y: 0, zoom: 0.6 }}
            fitView
            minZoom={0.4}
            maxZoom={2}
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#f8fafc" gap={16} size={1} />
            <Controls />
            <Panel position="top-right" className="bg-white p-3 rounded-lg shadow-md border border-gray-100 flex flex-col space-y-4">
              <div className="text-sm text-gray-600">
                <div className="font-medium mb-2">Your Learning Path:</div>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Follow the connections between skills</li>
                  <li>Click on a skill to see recommended actions</li>
                  <li>Complete all actions before progressing</li>
                </ul>
                <div className="flex flex-col space-y-2 mt-3">
                  <button
                    onClick={() => setIsSubmitted(false)}
                    className="w-full text-blue-600 border border-blue-600 px-2 py-1 rounded-md hover:bg-blue-50 transition-colors text-sm"
                  >
                    Edit Technical Profile
                  </button>
                  <button
                    onClick={handleSaveTree}
                    disabled={isSaving}
                    className="w-full bg-blue-600 text-white px-2 py-1 rounded-md hover:bg-blue-700 transition-colors text-sm disabled:opacity-50"
                  >
                    {isSaving ? 'Saving...' : 'Save Tree to My Path'}
                  </button>
                  {saveSuccess && (
                    <div className="text-xs text-green-600 font-medium mt-1 text-center">
                      Tree saved successfully!
                    </div>
                  )}
                </div>
              </div>
              
              {/* XP Progress */}
              <XPProgress />
            </Panel>
          </ReactFlow>
        </div>
      )}
    </div>
  );
} 