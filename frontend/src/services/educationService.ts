/**
 * Education Programs Service
 * Handles API calls for searching and fetching education programs
 */

export interface Institution {
  id: string;
  name: string;
  name_fr?: string;
  institution_type: 'cegep' | 'university' | 'college';
  city: string;
  province_state: string;
  website_url?: string;
  languages_offered: string[];
  active: boolean;
}

export interface Program {
  id: string;
  title: string;
  title_fr?: string;
  description: string;
  description_fr?: string;
  institution: Institution;
  program_type: string;
  level: 'certificate' | 'diploma' | 'associate' | 'bachelor' | 'master' | 'phd' | 'professional';
  field_of_study: string;
  duration_months?: number;
  language: string[];
  tuition_domestic?: number;
  tuition_international?: number;
  employment_rate?: number;
  admission_requirements: string[];
  career_outcomes: string[];
  cip_code?: string;
  noc_code?: string;
  holland_compatibility?: {
    R: number;
    I: number;
    A: number;
    S: number;
    E: number;
    C: number;
    overall: number;
  };
  active: boolean;
}

export interface ProgramSearchRequest {
  query?: string;
  institution_types?: ('cegep' | 'university' | 'college')[];
  program_levels?: ('certificate' | 'diploma' | 'associate' | 'bachelor' | 'master' | 'phd' | 'professional')[];
  fields_of_study?: string[];
  cities?: string[];
  languages?: string[];
  max_tuition?: number;
  min_employment_rate?: number;
  user_id?: number;
  holland_matching?: boolean;
  limit?: number;
  offset?: number;
}

export interface ProgramSearchResponse {
  programs: Program[];
  total_count: number;
  has_more: boolean;
  search_metadata: {
    search_query?: string;
    filters_applied: {
      institution_types?: string[];
      program_levels?: string[];
      cities?: string[];
      languages?: string[];
    };
    holland_matching_enabled: boolean;
    total_available_programs: number;
  };
}

export interface SearchMetadata {
  institution_types: string[];
  program_levels: string[];
  cities: string[];
  fields_of_study: string[];
  languages: string[];
  total_programs: number;
}

class EducationService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  private async makeRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          // Add auth header if available
          ...(localStorage.getItem('access_token') && {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }),
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error making request to ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * Search for education programs
   */
  async searchPrograms(searchRequest: ProgramSearchRequest): Promise<ProgramSearchResponse> {
    return this.makeRequest<ProgramSearchResponse>('/api/v1/education/programs/search', {
      method: 'POST',
      body: JSON.stringify(searchRequest),
    });
  }

  /**
   * Get detailed information about a specific program
   */
  async getProgramDetails(programId: string): Promise<Program> {
    return this.makeRequest<Program>(`/api/v1/education/programs/${programId}`);
  }

  /**
   * Get list of all institutions
   */
  async getInstitutions(): Promise<{ institutions: Institution[] }> {
    return this.makeRequest<{ institutions: Institution[] }>('/api/v1/education/institutions');
  }

  /**
   * Get metadata for search filters
   */
  async getSearchMetadata(): Promise<SearchMetadata> {
    return this.makeRequest<SearchMetadata>('/api/v1/education/metadata');
  }

  /**
   * Get user's Holland RIASEC scores for program matching
   */
  async getUserHollandScores(userId: number): Promise<{ R: number; I: number; A: number; S: number; E: number; C: number } | null> {
    try {
      // This would connect to your existing Holland test results API
      const response = await this.makeRequest<any>(`/api/v1/holland/user/${userId}/latest`);
      return {
        R: response.r_score || 0,
        I: response.i_score || 0,
        A: response.a_score || 0,
        S: response.s_score || 0,
        E: response.e_score || 0,
        C: response.c_score || 0,
      };
    } catch (error) {
      console.error('Error fetching Holland scores:', error);
      return null;
    }
  }

  /**
   * Get personalized program recommendations based on user profile
   */
  async getPersonalizedRecommendations(
    userId: number, 
    limit: number = 10
  ): Promise<ProgramSearchResponse> {
    const searchRequest: ProgramSearchRequest = {
      user_id: userId,
      holland_matching: true,
      limit,
      offset: 0,
    };

    return this.searchPrograms(searchRequest);
  }

  /**
   * Save a program to user's saved list
   */
  async saveProgram(programId: string, userId: number): Promise<void> {
    await this.makeRequest(`/api/v1/education/programs/${programId}/save`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
  }

  /**
   * Remove a program from user's saved list
   */
  async unsaveProgram(programId: string, userId: number): Promise<void> {
    await this.makeRequest(`/api/v1/education/programs/${programId}/save`, {
      method: 'DELETE',
      body: JSON.stringify({ user_id: userId }),
    });
  }

  /**
   * Get user's saved programs
   */
  async getSavedPrograms(userId: number): Promise<Program[]> {
    const response = await this.makeRequest<{ programs: Program[] }>(`/api/v1/education/users/${userId}/saved-programs`);
    return response.programs;
  }

  /**
   * Format tuition for display
   */
  formatTuition(amount?: number, isDomestic: boolean = true): string {
    if (!amount) return 'Not specified';
    
    const currency = isDomestic ? 'CAD' : 'CAD';
    const formatted = new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);

    // Add period indicator for context
    if (amount < 1000) {
      return `${formatted}/semester`;
    } else {
      return `${formatted}/year`;
    }
  }

  /**
   * Get Holland code display name
   */
  getHollandCodeName(code: string): string {
    const names: { [key: string]: string } = {
      'R': 'Realistic',
      'I': 'Investigative', 
      'A': 'Artistic',
      'S': 'Social',
      'E': 'Enterprising',
      'C': 'Conventional'
    };
    return names[code] || code;
  }

  /**
   * Calculate overall Holland compatibility percentage
   */
  calculateCompatibilityPercentage(compatibility?: Program['holland_compatibility']): number {
    if (!compatibility) return 0;
    return Math.round(compatibility.overall * 100);
  }

  /**
   * Get top Holland traits for a program
   */
  getTopHollandTraits(compatibility?: Program['holland_compatibility'], count: number = 3): string[] {
    if (!compatibility) return [];
    
    const traits = Object.entries(compatibility)
      .filter(([key]) => key !== 'overall')
      .sort(([, a], [, b]) => b - a)
      .slice(0, count)
      .map(([key]) => this.getHollandCodeName(key));
    
    return traits;
  }
}

// Export singleton instance
const educationService = new EducationService();
export default educationService;