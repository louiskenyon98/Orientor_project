import axios from 'axios';

const API_URL = '/api/v1';

export interface CompetenceNode {
  id: string;
  skill_id: string;
  skill_label: string;
  challenge: string;
  xp_reward: number;
  visible: boolean;
  revealed: boolean;
  state: 'locked' | 'completed';
  notes: string;
}

export interface CompetenceTreeData {
  nodes: CompetenceNode[];
  edges: { source: string; target: string }[];
  graph_id: string;
}

export const generateCompetenceTree = async (userId: number): Promise<{ graph_id: string }> => {
  try {
    console.log(`Génération d'un arbre de compétences pour l'utilisateur ${userId}`);
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Authentication token not found');
    }
    const response = await axios.post(
      `${API_URL}/competence-tree/generate?user_id=${userId}`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    console.log('Réponse de génération:', response.data);
    return response.data as { graph_id: string };
  } catch (error) {
    console.error('Erreur lors de la génération de l\'arbre de compétences:', error);
    throw error;
  }
};

export const getCompetenceTree = async (graphId: string): Promise<CompetenceTreeData> => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Authentication token not found');
    }
    const response = await axios.get(`${API_URL}/competence-tree/${graphId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data as CompetenceTreeData;
  } catch (error) {
    console.error('Erreur lors de la récupération de l\'arbre de compétences:', error);
    throw error;
  }
};

export const completeChallenge = async (nodeId: string, userId: number): Promise<{ success: boolean }> => {
  try {
    console.log(`Complétion du défi ${nodeId} pour l'utilisateur ${userId}`);
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Authentication token not found');
    }
    const response = await axios.patch(
      `${API_URL}/competence-tree/node/${nodeId}/complete?user_id=${userId}`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    console.log('Réponse de complétion:', response.data);
    return response.data as { success: boolean };
  } catch (error) {
    console.error('Erreur lors de la complétion du défi:', error);
    throw error;
  }
};