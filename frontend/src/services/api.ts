import axios from 'axios';

class ApiService {
  private api: any;

  constructor() {
    // For Replit environment, use relative path to avoid CORS issues
    // The proxy will handle routing to the backend
    const baseURL = import.meta.env.VITE_API_BASE_URL || '/api';

    this.api = axios.create({
      baseURL,
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add interceptor to handle 401 responses
    this.api.interceptors.response.use(
      (response: any) => response,
      (error: any) => {
        if (error.response?.status === 401) {
          // Redirect to login if not authenticated
          window.location.reload();
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(sessionId: string, phoneNumber: string) {
    const params = new URLSearchParams();
    params.append('sessionId', sessionId);
    params.append('phoneNumber', phoneNumber);

    const response = await this.api.post('/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  // Get financial insights
  async getQuickInsights() {
    const response = await this.api.get('/quick-insights');
    return response.data;
  }

  // Ask AI assistant
  async askAI(query: string) {
    const response = await this.api.post('/ask-ai', {
      query,
    });
    return response.data;
  }

  // Health check
  async healthCheck() {
    // Health endpoint is at root level, not /api
    const response = await axios.get('/health', { withCredentials: true });
    return response.data;
  }

  // Get transactions
  async getTransactions() {
    const response = await this.api.get('/transactions');
    return response.data;
  }

  // Get net worth
  async getNetWorth() {
    const response = await this.api.get('/net_worth');
    return response.data;
  }

  // Visualize data
  async visualize(query: string) {
    const response = await this.api.post('/visualize', { query });
    return response.data;
  }
}

export const apiService = new ApiService();