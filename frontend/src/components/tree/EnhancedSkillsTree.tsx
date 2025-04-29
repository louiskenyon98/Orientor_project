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

// Define custom node types
const nodeTypes: NodeTypes = {
  skillNode: SkillNode,
  outcomeNode: OutcomeNode,
  rootNode: RootNode,
};

// Sample data structure for programming path with multiple skill levels
const initialNodes: Node[] = [
  // Root Node (Career Domain)
  {
    id: 'programming',
    type: 'rootNode',
    data: { label: 'Programming' },
    position: { x: 400, y: 50 },
  },
  
  // Level 1 Skills (Basics)
  {
    id: 'python-basics',
    type: 'skillNode',
    data: { 
      label: 'Python Basics',
      actions: [
        'Complete Python Basic Syntax course',
        'Practice with 5 beginner exercises',
        'Build a simple calculator app'
      ]
    },
    position: { x: 200, y: 150 },
  },
  {
    id: 'html-css',
    type: 'skillNode',
    data: { 
      label: 'HTML & CSS',
      actions: [
        'Learn basic HTML tags',
        'Style a webpage with CSS',
        'Create a personal portfolio page'
      ]
    },
    position: { x: 600, y: 150 },
  },
  
  // Level 2 Skills (Intermediate)
  {
    id: 'git-version-control',
    type: 'skillNode',
    data: { 
      label: 'Git Version Control',
      actions: [
        'Set up Git repository',
        'Learn basic Git commands',
        'Practice branching and merging'
      ]
    },
    position: { x: 100, y: 250 },
  },
  {
    id: 'data-structures',
    type: 'skillNode',
    data: { 
      label: 'Data Structures',
      actions: [
        'Learn arrays and lists',
        'Implement linked lists',
        'Practice with stacks and queues'
      ]
    },
    position: { x: 300, y: 250 },
  },
  {
    id: 'responsive-design',
    type: 'skillNode',
    data: { 
      label: 'Responsive Design',
      actions: [
        'Learn media queries',
        'Implement flexbox layouts',
        'Create a responsive webpage'
      ]
    },
    position: { x: 500, y: 250 },
  },
  {
    id: 'javascript-basics',
    type: 'skillNode',
    data: { 
      label: 'JavaScript Basics',
      actions: [
        'Learn JS syntax and variables',
        'Implement DOM manipulation',
        'Create interactive web elements'
      ]
    },
    position: { x: 700, y: 250 },
  },
  
  // Level 3 Skills (Advanced)
  {
    id: 'sql-databases',
    type: 'skillNode',
    data: { 
      label: 'SQL & Databases',
      actions: [
        'Learn SQL query basics',
        'Connect application to database',
        'Implement CRUD operations'
      ]
    },
    position: { x: 0, y: 350 },
  },
  {
    id: 'algorithms',
    type: 'skillNode',
    data: { 
      label: 'Algorithms',
      actions: [
        'Study sorting algorithms',
        'Implement search algorithms',
        'Analyze algorithm efficiency'
      ]
    },
    position: { x: 200, y: 350 },
  },
  {
    id: 'apis',
    type: 'skillNode',
    data: { 
      label: 'APIs',
      actions: [
        'Learn RESTful API concepts',
        'Consume third-party APIs',
        'Build a simple API'
      ]
    },
    position: { x: 400, y: 350 },
  },
  {
    id: 'react-basics',
    type: 'skillNode',
    data: { 
      label: 'React Basics',
      actions: [
        'Understand React components',
        'Implement state management',
        'Build a simple React app'
      ]
    },
    position: { x: 600, y: 350 },
  },
  {
    id: 'javascript-advanced',
    type: 'skillNode',
    data: { 
      label: 'Advanced JavaScript',
      actions: [
        'Learn async programming',
        'Master closures and scope',
        'Practice with ES6+ features'
      ]
    },
    position: { x: 800, y: 350 },
  },
  
  // Level 4 Skills (Specialized)
  {
    id: 'full-stack-project',
    type: 'outcomeNode',
    data: { label: 'Full Stack Project' },
    position: { x: 400, y: 450 },
  },
];

// Define connections between nodes
const initialEdges: Edge[] = [
  // Connect root to first level skills
  { id: 'e-root-python', source: 'programming', target: 'python-basics', type: 'smoothstep', animated: true },
  { id: 'e-root-html', source: 'programming', target: 'html-css', type: 'smoothstep', animated: true },
  
  // Connect first level to second level
  { id: 'e-python-git', source: 'python-basics', target: 'git-version-control', type: 'smoothstep' },
  { id: 'e-python-ds', source: 'python-basics', target: 'data-structures', type: 'smoothstep' },
  { id: 'e-html-responsive', source: 'html-css', target: 'responsive-design', type: 'smoothstep' },
  { id: 'e-html-js', source: 'html-css', target: 'javascript-basics', type: 'smoothstep' },
  
  // Connect second level to third level
  { id: 'e-git-sql', source: 'git-version-control', target: 'sql-databases', type: 'smoothstep' },
  { id: 'e-ds-algo', source: 'data-structures', target: 'algorithms', type: 'smoothstep' },
  { id: 'e-ds-api', source: 'data-structures', target: 'apis', type: 'smoothstep' },
  { id: 'e-js-react', source: 'javascript-basics', target: 'react-basics', type: 'smoothstep' },
  { id: 'e-js-advanced', source: 'javascript-basics', target: 'javascript-advanced', type: 'smoothstep' },
  
  // Connect to final outcome
  { id: 'e-api-fullstack', source: 'apis', target: 'full-stack-project', type: 'smoothstep' },
  { id: 'e-react-fullstack', source: 'react-basics', target: 'full-stack-project', type: 'smoothstep' },
];

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

export default function EnhancedSkillsTree() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  // Handle node click
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  return (
    <div className="w-full h-[calc(100vh-6rem)] bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <motion.div 
        className="p-4 text-2xl font-light text-gray-800 border-b border-gray-100"
        initial="hidden"
        animate="visible"
        variants={titleVariants}
      >
        Programming Skills Journey
        <p className="text-sm text-gray-500 mt-1">
          Build your skills progressively from basics to advanced concepts
        </p>
      </motion.div>
      
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
        <Panel position="top-right" className="bg-white p-3 rounded-lg shadow-md border border-gray-100">
          <div className="text-sm text-gray-600">
            <div className="font-medium mb-2">Your Learning Path:</div>
            <ul className="list-disc pl-5 space-y-1">
              <li>Follow the connections between skills</li>
              <li>Click on a skill to see recommended actions</li>
              <li>Complete all actions before progressing</li>
            </ul>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
} 