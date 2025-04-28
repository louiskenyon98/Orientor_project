import React, { useCallback, useState, useEffect, useRef } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  ReactFlowProvider,
  NodeTypes,
  useReactFlow,
  Panel,
  ConnectionLineType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { TreeNode, convertToFlowGraph, NODE_TYPES } from '../../utils/convertToFlowGraph';
import { CareerNode, OutcomeNode, RootNode, SkillNode } from './CustomNodes';
import { treeService } from '../../services/treeService';

// Custom node types
const nodeTypes: NodeTypes = {
  [NODE_TYPES.root]: RootNode,
  [NODE_TYPES.skill]: SkillNode,
  [NODE_TYPES.outcome]: OutcomeNode,
  [NODE_TYPES.career]: CareerNode,
};

// Flow with custom controls and design
const FlowWithControls = ({ nodes, edges }: { nodes: any[], edges: any[] }) => {
  const reactFlowInstance = useReactFlow();

  useEffect(() => {
    if (nodes.length > 0) {
      setTimeout(() => {
        reactFlowInstance.fitView({
          padding: 0.25, // Reduced padding for more compact view
          includeHiddenNodes: false,
          minZoom: 0.3,
          maxZoom: 1.5,
          duration: 800, // Smooth animation when fitting view
        });
      }, 200);
    }
  }, [nodes, reactFlowInstance]);

  return (
    <>
      <Background color="#e5e7eb" gap={16} size={1} />
      <Controls
        showInteractive={false}
        position="bottom-right"
        style={{
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)',
          borderRadius: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        }}
      />
      <MiniMap
        zoomable
        pannable
        nodeStrokeWidth={2}
        nodeBorderRadius={6}
        style={{
          backgroundColor: 'rgba(255,255,255,0.85)',
          border: '1px solid #d1d5db',
          borderRadius: '12px',
        }}
        nodeColor={(node) => {
          switch (node.type) {
            case 'rootNode': return '#1e40af';
            case 'skillNode': return '#0284c7';
            case 'outcomeNode': return '#ffffff';
            case 'careerNode': return '#d97706';
            default: return '#9ca3af';
          }
        }}
      />
      <Panel
        position="top-right"
        className="bg-white bg-opacity-80 backdrop-blur-md p-3 rounded-xl shadow-md"
      >
        <div className="text-xs text-gray-600 leading-relaxed">
          <strong className="font-semibold text-gray-700">Tip:</strong> Click on skill nodes to see action steps. Drag nodes to reposition.
        </div>
      </Panel>
    </>
  );
};

interface SkillTreeProps {
  initialTree?: TreeNode;
}

export const SkillTree: React.FC<SkillTreeProps> = ({ initialTree }) => {
  const [tree, setTree] = useState<TreeNode | null>(initialTree || null);
  const [profile, setProfile] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [detailedError, setDetailedError] = useState<any>(null);

  const { nodes, edges } = tree ? convertToFlowGraph(tree) : { nodes: [], edges: [] };

  const parseErrorDetails = (error: any): string => {
    if (error.response?.data) {
      try {
        if (typeof error.response.data === 'string') {
          const parsedData = JSON.parse(error.response.data);
          if (parsedData.message) {
            return parsedData.message;
          }
        }
        if (error.response.data.detail) {
          return error.response.data.detail;
        }
        return JSON.stringify(error.response.data, null, 2);
      } catch (e) {
        return error.response.data;
      }
    }
    return error.message || 'An unknown error occurred';
  };

  const handleGenerateTree = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!profile.trim()) {
      setError('Please enter a profile description');
      return;
    }
    
    setLoading(true);
    setError(null);
    setDetailedError(null);

    try {
      const generatedTree = await treeService.generateTree(profile);
      setTree(generatedTree);
    } catch (err: any) {
      setDetailedError(err);
      const errorMessage = parseErrorDetails(err);
      setError(`Failed to generate skill tree: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  }, [profile]);
  
  return (
    <div className="flex flex-col h-full">
      {/* Profile input form */}
      <div className="mb-4 p-4 bg-white rounded-xl shadow-md">
        <form onSubmit={handleGenerateTree} className="flex flex-col space-y-4">
          <div>
            <label htmlFor="profile" className="block mb-2 font-medium text-gray-700">
              Your Profile
            </label>
            <textarea
              id="profile"
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe your interests, traits, skills..."
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              disabled={loading}
            />
          </div>
          
          <div>
            <button
              type="submit"
              disabled={loading}
              className={`px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                loading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {loading ? 'Generating...' : 'Generate Skill Tree'}
            </button>
          </div>
          
          {error && (
            <div className="p-4 text-red-700 bg-red-100 rounded-lg overflow-auto max-h-80">
              <h3 className="font-bold mb-2">Error</h3>
              <pre className="whitespace-pre-wrap text-sm">{error}</pre>
            </div>
          )}
        </form>
      </div>

      {/* Skill tree visualization */}
      <div className="flex-grow h-[80vh] bg-gray-50 rounded-xl shadow-inner p-4">
        <ReactFlowProvider>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            defaultViewport={{ x: 0, y: 0, zoom: 0.6 }}
            minZoom={0.2}
            maxZoom={1.5}
            fitView
            fitViewOptions={{ 
              padding: 0.25,
              duration: 800,
            }}
            connectionLineType={ConnectionLineType.SmoothStep}
            defaultEdgeOptions={{
              type: 'smoothstep',
              animated: true,
              style: { 
                strokeWidth: 1.5, 
                stroke: '#94a3b8',
                strokeDasharray: '6 3' 
              },
            }}
            nodesDraggable={true}
            elementsSelectable={true}
            panOnScroll={true}
            zoomOnScroll={true}
            zoomOnPinch={true}
            className="rounded-lg transition-all duration-500 ease-in-out"
            proOptions={{ hideAttribution: true }}
          >
            <FlowWithControls nodes={nodes} edges={edges} />
          </ReactFlow>
        </ReactFlowProvider>
      </div>
    </div>
  );
};
