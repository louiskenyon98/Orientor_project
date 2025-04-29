import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Define TreeNode interface for the skills tree
export interface SkillsTreeNode {
  id: string;
  label: string;
  type: "root" | "skill" | "outcome" | "career";
  level: number;
  actions?: string[];
  children?: SkillsTreeNode[];
}

interface SkillsTreeResponse {
  tree: SkillsTreeNode;
}

// Service to interact with the tree API endpoint for skills
export const skillsTreeService = {
  /**
   * Generate a technical skills tree based on the provided profile
   * @param profile - The technical profile (languages, technologies, goals, etc.)
   * @returns The generated skills tree
   */
  async generateSkillsTree(profile: string): Promise<SkillsTreeNode> {
    console.log(`skillsTreeService: Generating tree with API URL: ${API_URL}`);
    console.log(`skillsTreeService: Profile length: ${profile.length} characters`);
    
    try {
      // Get auth token if available
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      console.log(`skillsTreeService: Auth token ${token ? 'found' : 'not found'}`);
      
      // Set up request config with auth header if token exists
      const config = token ? {
        headers: {
          Authorization: `Bearer ${token}`
        }
      } : {};
      
      console.log(`skillsTreeService: Making POST request to ${API_URL}/tree`);
      console.time('skillsTreeService:apiCall');
      
      // Use the existing /tree endpoint
      const response = await axios.post<SkillsTreeResponse>(
        `${API_URL}/tree`, 
        { profile },
        config
      );
      
      console.timeEnd('skillsTreeService:apiCall');
      console.log(`skillsTreeService: Request successful - Status: ${response.status}`);
      
      if (!response.data || !response.data.tree) {
        console.error('skillsTreeService: Response missing tree data:', response.data);
        throw new Error('API response missing tree data structure');
      }
      
      // Basic validation of tree structure
      const tree = response.data.tree;
      if (!tree.id || !tree.type || !tree.children || !Array.isArray(tree.children)) {
        console.error('skillsTreeService: Invalid tree structure received:', tree);
        throw new Error('API returned invalid tree structure');
      }
      
      console.log(`skillsTreeService: Tree generated successfully with root ID: ${tree.id}`);
      console.log(`skillsTreeService: Tree has ${tree.children?.length || 0} level 1 children`);
      
      return tree;
    } catch (error: any) {
      // Enhance error logging
      console.error('skillsTreeService: Error generating skills tree:', error);
      
      if (error.response) {
        // The request was made and the server responded with a status code outside of 2xx
        console.error(`skillsTreeService: Server error - Status: ${error.response.status}`);
        console.error('skillsTreeService: Response headers:', error.response.headers);
        console.error('skillsTreeService: Response data:', error.response.data);
        
        // Add specific error handling for common status codes
        if (error.response.status === 401) {
          console.error('skillsTreeService: Authentication error - not authorized');
        } else if (error.response.status === 400) {
          console.error('skillsTreeService: Bad request - check payload format');
        } else if (error.response.status === 500) {
          console.error('skillsTreeService: Server error - check backend logs');
        }
      } else if (error.request) {
        // The request was made but no response was received
        console.error('skillsTreeService: No response received from server');
        console.error('skillsTreeService: Request details:', error.request);
      } else {
        // Something happened in setting up the request
        console.error('skillsTreeService: Request setup error:', error.message);
      }
      
      // Forward the error for handling in the component
      throw error;
    }
  },
}; 