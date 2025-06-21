import { SkillNode, TimelineTier } from '@/components/career/TimelineVisualization';

// API endpoints
const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-api.com/api'
  : 'http://localhost:8000';

// Types for API responses
interface CareerGoal {
  id: string;
  title: string;
  description: string;
  target_date: string;
  progress: number;
  tier_id?: string;
  skill_ids: string[];
  created_at: string;
  updated_at: string;
}

interface GraphSageScore {
  skill_id: string;
  confidence_score: number;
  tier_level: number;
  relationships: string[];
  metadata: {
    last_updated: string;
    model_version: string;
    training_accuracy: number;
  };
}

interface CareerProgressionResponse {
  user_id: string;
  tiers: TimelineTier[];
  goals: CareerGoal[];
  graphsage_scores: GraphSageScore[];
  last_updated: string;
}

// Utility function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
};

// Career Goals Service
export class CareerGoalsService {
  /**
   * Fetch user's career progression with GraphSage scores
   */
  static async getCareerProgression(): Promise<CareerProgressionResponse> {
    try {
      const response = await fetch(`${API_BASE}/career/progression`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching career progression:', error);
      
      // Return mock data for development
      return this.getMockCareerProgression();
    }
  }

  /**
   * Update GraphSage confidence scores for skills
   */
  static async updateGraphSageScores(skillIds: string[]): Promise<GraphSageScore[]> {
    try {
      const response = await fetch(`${API_BASE}/career/graphsage/update`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ skill_ids: skillIds }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.scores;
    } catch (error) {
      console.error('Error updating GraphSage scores:', error);
      throw error;
    }
  }

  /**
   * Set a new career goal
   */
  static async setCareerGoal(goalData: {
    title: string;
    description: string;
    target_date: string;
    skill_ids: string[];
    tier_id?: string;
  }): Promise<CareerGoal> {
    try {
      const response = await fetch(`${API_BASE}/career/goals`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(goalData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.goal;
    } catch (error) {
      console.error('Error setting career goal:', error);
      throw error;
    }
  }

  /**
   * Update career goal progress
   */
  static async updateCareerGoalProgress(goalId: string, progress: number): Promise<CareerGoal> {
    try {
      const response = await fetch(`${API_BASE}/career/goals/${goalId}/progress`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ progress }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.goal;
    } catch (error) {
      console.error('Error updating career goal progress:', error);
      throw error;
    }
  }

  /**
   * Get skill recommendations based on GraphSage analysis
   */
  static async getSkillRecommendations(currentSkillIds: string[]): Promise<SkillNode[]> {
    try {
      const response = await fetch(`${API_BASE}/career/recommendations/skills`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ current_skills: currentSkillIds }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.recommendations;
    } catch (error) {
      console.error('Error getting skill recommendations:', error);
      throw error;
    }
  }

  /**
   * Analyze skill relationships using GraphSage
   */
  static async analyzeSkillRelationships(skillIds: string[]): Promise<{
    relationships: Array<{
      source: string;
      target: string;
      strength: number;
      confidence: number;
    }>;
    clusters: Array<{
      id: string;
      skills: string[];
      theme: string;
    }>;
  }> {
    try {
      const response = await fetch(`${API_BASE}/career/graphsage/relationships`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ skill_ids: skillIds }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error analyzing skill relationships:', error);
      throw error;
    }
  }

  /**
   * Get career path optimization suggestions
   */
  static async getCareerPathOptimization(currentTier: number): Promise<{
    recommendations: Array<{
      skill_id: string;
      priority_score: number;
      expected_impact: number;
      estimated_months: number;
      reasoning: string;
    }>;
    timeline_adjustments: Array<{
      tier_id: string;
      suggested_duration: number;
      current_duration: number;
      reasoning: string;
    }>;
  }> {
    try {
      const response = await fetch(`${API_BASE}/career/optimization/${currentTier}`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting career path optimization:', error);
      throw error;
    }
  }

  /**
   * Mock data for development
   */
  private static getMockCareerProgression(): CareerProgressionResponse {
    return {
      user_id: 'mock-user-123',
      tiers: [
        {
          id: 'tier-1',
          title: 'Foundation & Exploration',
          level: 1,
          timeline_months: 6,
          confidence_threshold: 0.8,
          skills: [
            {
              id: 'skill-1-1',
              label: 'Programming Fundamentals',
              confidence_score: 0.92,
              type: 'skill',
              level: 1,
              relationships: ['skill-1-2', 'skill-2-1'],
              metadata: {
                description: 'Learn core programming concepts and syntax',
                estimated_months: 3,
                prerequisites: [],
                learning_resources: ['Online courses', 'Practice projects']
              }
            },
            {
              id: 'skill-1-2',
              label: 'Problem Solving',
              confidence_score: 0.85,
              type: 'skill',
              level: 1,
              relationships: ['skill-1-1', 'skill-2-3'],
              metadata: {
                description: 'Develop analytical thinking and debugging skills',
                estimated_months: 2,
                prerequisites: [],
                learning_resources: ['Algorithm challenges', 'Code reviews']
              }
            }
          ]
        }
      ],
      goals: [
        {
          id: 'goal-1',
          title: 'Master Frontend Development',
          description: 'Become proficient in React and modern frontend technologies',
          target_date: '2024-12-31',
          progress: 65,
          tier_id: 'tier-2',
          skill_ids: ['skill-2-1', 'skill-2-4'],
          created_at: '2024-01-15',
          updated_at: '2024-06-20'
        }
      ],
      graphsage_scores: [
        {
          skill_id: 'skill-1-1',
          confidence_score: 0.92,
          tier_level: 1,
          relationships: ['skill-1-2', 'skill-2-1'],
          metadata: {
            last_updated: '2024-06-20T10:30:00Z',
            model_version: 'graphsage-v2.1',
            training_accuracy: 0.94
          }
        }
      ],
      last_updated: '2024-06-20T10:30:00Z'
    };
  }
}

// Export types for use in components
export type { CareerGoal, GraphSageScore, CareerProgressionResponse };