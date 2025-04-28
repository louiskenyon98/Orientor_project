import axios from 'axios';
import { TreeNode } from '../utils/convertToFlowGraph';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TreeResponse {
  tree: TreeNode;
}

// Service to interact with the tree API endpoint
export const treeService = {
  /**
   * Generate a skill tree based on the provided profile
   * @param profile - The student profile (interests, traits, etc.)
   * @returns The generated skill tree
   */
  async generateTree(profile: string): Promise<TreeNode> {
    console.log(`treeService: Generating tree with API URL: ${API_URL}`);
    console.log(`treeService: Profile length: ${profile.length} characters`);
    
    try {
      // Get auth token if available
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      console.log(`treeService: Auth token ${token ? 'found' : 'not found'}`);
      
      // Set up request config with auth header if token exists
      const config = token ? {
        headers: {
          Authorization: `Bearer ${token}`
        }
      } : {};
      
      console.log(`treeService: Making POST request to ${API_URL}/tree`);
      console.time('treeService:apiCall');
      
      const response = await axios.post<TreeResponse>(
        `${API_URL}/tree`, 
        { profile },
        config
      );
      
      console.timeEnd('treeService:apiCall');
      console.log(`treeService: Request successful - Status: ${response.status}`);
      
      if (!response.data || !response.data.tree) {
        console.error('treeService: Response missing tree data:', response.data);
        throw new Error('API response missing tree data structure');
      }
      
      // Basic validation of tree structure
      const tree = response.data.tree;
      if (!tree.id || !tree.type || tree.type !== 'root' || !tree.children || !Array.isArray(tree.children)) {
        console.error('treeService: Invalid tree structure received:', tree);
        throw new Error('API returned invalid tree structure');
      }
      
      console.log(`treeService: Tree generated successfully with root ID: ${tree.id}`);
      console.log(`treeService: Tree has ${tree.children?.length || 0} level 1 children`);
      
      return tree;
    } catch (error: any) {
      // Enhance error logging
      console.error('treeService: Error generating skill tree:', error);
      
      if (error.response) {
        // The request was made and the server responded with a status code outside of 2xx
        console.error(`treeService: Server error - Status: ${error.response.status}`);
        console.error('treeService: Response headers:', error.response.headers);
        console.error('treeService: Response data:', error.response.data);
        
        // Add specific error handling for common status codes
        if (error.response.status === 401) {
          console.error('treeService: Authentication error - not authorized');
        } else if (error.response.status === 400) {
          console.error('treeService: Bad request - check payload format');
        } else if (error.response.status === 500) {
          console.error('treeService: Server error - check backend logs');
        }
      } else if (error.request) {
        // The request was made but no response was received
        console.error('treeService: No response received from server');
        console.error('treeService: Request details:', error.request);
      } else {
        // Something happened in setting up the request
        console.error('treeService: Request setup error:', error.message);
      }
      
      // Forward the error for handling in the component
      throw error;
    }
  },
}; 