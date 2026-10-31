const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const analyticsService = {
  async getOverview() {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/overview`)
    if (!response.ok) throw new Error('Failed to fetch analytics overview')
    return response.json()
  },
  async getRevenue() {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/revenue`)
    if (!response.ok) throw new Error('Failed to fetch revenue')
    return response.json()
  },
  async getSubscriptions() {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/subscriptions`)
    if (!response.ok) throw new Error('Failed to fetch subscriptions')
    return response.json()
  },
}
