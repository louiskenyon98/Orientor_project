import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

// Add request interceptor to include the token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    // @ts-ignore
    config.headers = config.headers || {};
    // @ts-ignore
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Function to get career recommendations for the Find Your Way tab
export const getCareerRecommendations = async (limit = 10) => {
  try {
    console.log('Fetching career recommendations from:', `${API_URL}/careers/recommendations?limit=${limit}`);
    const response = await api.get(`/careers/recommendations?limit=${limit}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching career recommendations:', error);
    if (error?.response) {
      console.error('API Error Details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          baseURL: error.config?.baseURL,
          url: error.config?.url,
          headers: error.config?.headers
        }
      });
    }
    throw error;
  }
};

// Function to save a career when user swipes right
export const saveCareer = async (careerId: number) => {
  try {
    const response = await api.post(`/careers/save/${careerId}`);
    return response.data;
  } catch (error) {
    console.error('Error saving career:', error);
    throw error;
  }
};

// Function to get saved careers (for the My Space section)
export const getSavedCareers = async () => {
  try {
    const response = await api.get('/careers/saved');
    return response.data;
  } catch (error) {
    console.error('Error fetching saved careers:', error);
    throw error;
  }
};

export default api; 