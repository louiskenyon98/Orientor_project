import React, { useCallback, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  ReactFlowProvider,
  NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { TreeNode, convertToFlowGraph, NODE_TYPES } from '../../utils/convertToFlowGraph';
import { CareerNode, OutcomeNode, RootNode, SkillNode } from './CustomNodes';
import { treeService } from '../../services/treeService';

// Define custom node types
const nodeTypes: NodeTypes = {
  [NODE_TYPES.root]: RootNode,
  [NODE_TYPES.skill]: SkillNode,
  [NODE_TYPES.outcome]: OutcomeNode,
  [NODE_TYPES.career]: CareerNode,
};

// SkillTree component props
interface SkillTreeProps {
  initialTree?: TreeNode;
}

export const SkillTree: React.FC<SkillTreeProps> = ({ initialTree }) => {
  const [tree, setTree] = useState<TreeNode | null>(initialTree || null);
  const [profile, setProfile] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [detailedError, setDetailedError] = useState<any>(null);
  
  // Convert tree to ReactFlow nodes and edges
  const { nodes, edges } = tree ? convertToFlowGraph(tree) : { nodes: [], edges: [] };
  
  // Parse error details if possible
  const parseErrorDetails = (error: any): string => {
    console.log('Parsing error:', error);
    
    // Try to extract the response data
    if (error.response?.data) {
      console.log('Response data:', error.response.data);
      
      // Check if it's a detailed JSON error
      if (typeof error.response.data === 'string') {
        try {
          const parsedData = JSON.parse(error.response.data);
          if (parsedData.message) {
            return `${parsedData.message} ${parsedData.error_context ? 
              `\n\nDetails: ${JSON.stringify(parsedData.error_context, null, 2)}` : ''}`;
          }
        } catch (e) {
          // Not valid JSON, just use the string
          return error.response.data;
        }
      }
      
      // If it has a detail field
      if (error.response.data.detail) {
        try {
          // Try to parse if it's a JSON string
          const detailData = JSON.parse(error.response.data.detail);
          return detailData.message || error.response.data.detail;
        } catch (e) {
          // Not JSON, use as is
          return error.response.data.detail;
        }
      }
      
      return JSON.stringify(error.response.data, null, 2);
    }
    
    // Default to standard error message
    return error.message || 'An unknown error occurred';
  };
  
  // Handle form submission
  const handleGenerateTree = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!profile.trim()) {
      setError('Please enter a profile description');
      return;
    }
    
    setLoading(true);
    setError(null);
    setDetailedError(null);
    
    console.log(`Generating tree for profile: ${profile.substring(0, 50)}...`);
    
    try {
      console.log('Calling treeService.generateTree');
      const generatedTree = await treeService.generateTree(profile);
      console.log('Tree generated successfully:', generatedTree);
      setTree(generatedTree);
    } catch (err: any) {
      console.error('Error generating tree:', err);
      
      // Store the full error object for detailed inspection
      setDetailedError(err);
      
      // Parse and set a user-friendly error message
      const errorMessage = parseErrorDetails(err);
      setError(`Failed to generate skill tree: ${errorMessage}`);
      
      // Log additional request details if available
      if (err.response) {
        console.log('Status:', err.response.status);
        console.log('Headers:', err.response.headers);
      }
    } finally {
      setLoading(false);
    }
  }, [profile]);
  
  return (
    <div className="flex flex-col h-full">
      {/* Input form */}
      <div className="mb-6 p-4 bg-white rounded-lg shadow-md">
        <form onSubmit={handleGenerateTree} className="flex flex-col space-y-4">
          <div>
            <label htmlFor="profile" className="block mb-2 font-medium text-gray-700">
              Your Profile
            </label>
            <textarea
              id="profile"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
              
              {detailedError && (
                <div className="mt-4 pt-4 border-t border-red-200">
                  <details>
                    <summary className="cursor-pointer font-semibold mb-2">Technical Details</summary>
                    <div className="text-xs overflow-auto">
                      <p><strong>Status:</strong> {detailedError.response?.status || 'N/A'}</p>
                      <p><strong>Status Text:</strong> {detailedError.response?.statusText || 'N/A'}</p>
                      <p><strong>URL:</strong> {detailedError.config?.url || 'N/A'}</p>
                      <p><strong>Method:</strong> {detailedError.config?.method?.toUpperCase() || 'N/A'}</p>
                      {detailedError.response?.data && (
                        <>
                          <p className="font-semibold mt-2">Response Data:</p>
                          <pre className="bg-red-50 p-2 mt-1 rounded">{
                            typeof detailedError.response.data === 'object' 
                              ? JSON.stringify(detailedError.response.data, null, 2)
                              : detailedError.response.data
                          }</pre>
                        </>
                      )}
                    </div>
                  </details>
                </div>
              )}
            </div>
          )}
        </form>
      </div>
      
      {/* ReactFlow visualization */}
      <div className="flex-grow h-[80vh] bg-gray-50 rounded-lg shadow-inner">
        <ReactFlowProvider>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.1}
            maxZoom={1.5}
            defaultViewport={{ x: 0, y: 0, zoom: 0.5 }}
            attributionPosition="bottom-left"
          >
            <Background color="#f1f5f9" gap={12} />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </ReactFlowProvider>
      </div>
    </div>
  );
}; 