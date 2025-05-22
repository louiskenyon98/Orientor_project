import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Type definitions
export interface Recommendation {
  id?: number;
  oasis_code: string;
  label: string;
  description?: string;
  main_duties?: string;
  role_creativity?: number;
  role_leadership?: number;
  role_digital_literacy?: number;
  role_critical_thinking?: number;
  role_problem_solving?: number;
  analytical_thinking?: number;
  attention_to_detail?: number;
  collaboration?: number;
  adaptability?: number;
  independence?: number;
  evaluation?: number;
  decision_making?: number;
  stress_tolerance?: number;
  saved_at?: string;
  skill_comparison?: SkillsComparison;
  notes?: Note[];
  all_fields?: Record<string, string>;
  personal_analysis?: string;
  entry_qualifications?: string;
  suggested_improvements?: string;
}

export interface SkillComparison {
  user_skill?: number;
  role_skill?: number;
}

export interface SkillsComparison {
  creativity: SkillComparison;
  leadership: SkillComparison;
  digital_literacy: SkillComparison;
  critical_thinking: SkillComparison;
  problem_solving: SkillComparison;
}

export interface UserSkills {
  creativity: number;
  leadership: number;
  digital_literacy: number;
  critical_thinking: number;
  problem_solving: number;
  analytical_thinking: number;
  attention_to_detail: number;
  collaboration: number;
  adaptability: number;
  independence: number;
  evaluation: number;
  decision_making: number;
  stress_tolerance: number;
}

export interface Note {
  id: number;
  content: string;
  saved_recommendation_id?: number;
  created_at: string;
  updated_at: string;
}

export interface NoteCreate {
  content: string;
  saved_recommendation_id?: number;
}

export interface NoteUpdate {
  content: string;
}

// Configure axios with the token
const getAuthHeader = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  return {
    headers: {
      Authorization: `Bearer ${token}`
    }
  };
};

// Fetch saved recommendations
export const fetchSavedRecommendations = async (): Promise<Recommendation[]> => {
  try {
    const response = await axios.get<Recommendation[]>(`${API_URL}/space/recommendations`, getAuthHeader());
    console.log('API response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching saved recommendations:', error);
    throw error;
  }
};

// Save a recommendation
export const saveRecommendation = async (recommendation: Recommendation): Promise<Recommendation> => {
  try {
    const response = await axios.post<Recommendation>(
      `${API_URL}/space/recommendations`,
      recommendation,
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error saving recommendation:', error);
    throw error;
  }
};

// Save a recommendation with LLM analysis
export const saveRecommendationWithLLMAnalysis = async (
  recommendation: Recommendation,
  userProfile: {
    skills: UserSkills;
    experience?: string;
    education?: string;
    interests?: string;
  }
): Promise<Recommendation> => {
  try {
    // Préparer les données pour l'analyse LLM
    const analysisInput: LLMAnalysisInput = {
      oasis_code: recommendation.oasis_code,
      job_description: recommendation.description || '',
      user_profile: userProfile
    };

    // Générer l'analyse LLM
    const analysisResult = await generateLLMAnalysis(analysisInput);

    // Ajouter les résultats de l'analyse à la recommandation
    const enrichedRecommendation: Recommendation = {
      ...recommendation,
      personal_analysis: analysisResult.personal_analysis,
      entry_qualifications: analysisResult.entry_qualifications,
      suggested_improvements: analysisResult.suggested_improvements
    };

    // Sauvegarder la recommandation enrichie
    return await saveRecommendation(enrichedRecommendation);
  } catch (error) {
    console.error('Error saving recommendation with LLM analysis:', error);
    throw error;
  }
};

// Delete a saved recommendation
export const deleteRecommendation = async (recommendationId: number): Promise<void> => {
  try {
    await axios.delete(
      `${API_URL}/space/recommendations/${recommendationId}`, 
      getAuthHeader()
    );
  } catch (error) {
    console.error('Error deleting recommendation:', error);
    throw error;
  }
};

// Fetch notes for a recommendation
export const fetchNotes = async (recommendationId: number): Promise<Note[]> => {
  try {
    const response = await axios.get<Note[]>(
      `${API_URL}/space/notes?saved_recommendation_id=${recommendationId}`, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching notes:', error);
    throw error;
  }
};

// Create a new note
export const createNote = async (note: NoteCreate): Promise<Note> => {
  try {
    const response = await axios.post<Note>(
      `${API_URL}/space/notes`, 
      note, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error creating note:', error);
    throw error;
  }
};

// Update a note
export const updateNote = async (noteId: number, updates: NoteUpdate): Promise<Note> => {
  try {
    const response = await axios.put<Note>(
      `${API_URL}/space/notes/${noteId}`, 
      updates, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error updating note:', error);
    throw error;
  }
};

// Delete a note
export const deleteNote = async (noteId: number): Promise<void> => {
  try {
    await axios.delete(
      `${API_URL}/space/notes/${noteId}`, 
      getAuthHeader()
    );
  } catch (error) {
    console.error('Error deleting note:', error);
    throw error;
  }
};

// Interface pour les données d'entrée de l'analyse LLM
export interface LLMAnalysisInput {
  oasis_code: string;
  job_description: string;
  user_profile: {
    skills: UserSkills;
    experience?: string;
    education?: string;
    interests?: string;
  };
}

// Interface pour les résultats de l'analyse LLM
export interface LLMAnalysisResult {
  personal_analysis: string;
  entry_qualifications: string;
  suggested_improvements: string;
}

// Générer une analyse LLM pour une recommandation
export const generateLLMAnalysis = async (input: LLMAnalysisInput): Promise<LLMAnalysisResult> => {
  try {
    // Simulation côté client en attendant que l'API soit implémentée
    console.log('Simulation de génération d\'analyse LLM pour:', input.oasis_code);
    
    // Délai artificiel pour simuler le traitement
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Générer des analyses simulées basées sur le code OASIS et la description
    const jobTitle = input.job_description.split('.')[0] || 'ce poste';
    const userSkills = Object.entries(input.user_profile.skills)
      .filter(([_, value]) => value >= 4)
      .map(([key]) => key.replace(/_/g, ' '))
      .slice(0, 3)
      .join(', ');
    
    return {
      personal_analysis: `Votre profil correspond bien à ${jobTitle}. Vos compétences en ${userSkills} sont particulièrement pertinentes pour ce rôle. Votre formation et votre expérience vous donnent une base solide pour réussir dans ce domaine. Ce poste vous permettrait de mettre à profit vos points forts tout en développant de nouvelles compétences.`,
      
      entry_qualifications: `Pour réussir dans ce rôle, les qualifications suivantes sont généralement requises :
- Formation en lien avec le domaine d'activité
- Maîtrise des outils et technologies spécifiques au secteur
- Capacité d'analyse et de résolution de problèmes
- Compétences en communication et travail d'équipe
- Adaptabilité et volonté d'apprentissage continu`,
      
      suggested_improvements: `Pour améliorer votre adéquation avec ce poste, vous pourriez :
1. Développer davantage vos compétences techniques spécifiques au domaine
2. Acquérir des certifications pertinentes pour valider vos connaissances
3. Participer à des projets collaboratifs pour renforcer votre expérience pratique
4. Élargir votre réseau professionnel dans ce secteur
5. Suivre les dernières tendances et innovations du domaine`
    };
    
    // Quand l'API sera implémentée, décommenter le code ci-dessous
    /*
    const response = await axios.post<LLMAnalysisResult>(
      `${API_URL}/space/recommendations/llm-analysis`,
      input,
      getAuthHeader()
    );
    return response.data;
    */
  } catch (error) {
    console.error('Erreur lors de la génération de l\'analyse LLM:', error);
    // Retourner des valeurs par défaut en cas d'erreur
    return {
      personal_analysis: "Une erreur s'est produite lors de la génération de l'analyse personnelle.",
      entry_qualifications: "Les qualifications requises n'ont pas pu être générées.",
      suggested_improvements: "Les suggestions d'amélioration n'ont pas pu être générées."
    };
  }
};

// Update user skills
export const updateUserSkills = async (skills: UserSkills): Promise<UserSkills> => {
  try {
    const response = await axios.put<UserSkills>(
      `${API_URL}/space/skills`, 
      skills, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error updating skills:', error);
    throw error;
  }
};

// Get skill comparison data
export const getSkillComparison = async (oasisCode: string): Promise<any> => {
  try {
    const response = await axios.get(
      `${API_URL}/space/recommendations/${oasisCode}/skill-comparison`, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching skill comparison:', error);
    throw error;
  }
}; 