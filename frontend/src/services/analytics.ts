import { apiRequest } from '../lib/api'

export const analyticsService = {
  getOverview: () => apiRequest('/api/v1/analytics/overview'),
  getRevenue: () => apiRequest('/api/v1/analytics/revenue'),
  getSubscriptions: () => apiRequest('/api/v1/analytics/subscriptions'),
}
