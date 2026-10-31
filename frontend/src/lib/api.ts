const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = {
  async getHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },
};
