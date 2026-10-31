import { useEffect, useState } from 'react'
import { analyticsService } from '../services/analytics'

export default function Dashboard() {
  const [overview, setOverview] = useState<any>(null)
  const [revenue, setRevenue] = useState<any[]>([])
  const [subscriptions, setSubscriptions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const [ov, rev, subs] = await Promise.all([
        analyticsService.getOverview(),
        analyticsService.getRevenue(),
        analyticsService.getSubscriptions(),
      ])
      setOverview(ov)
      setRevenue(rev)
      setSubscriptions(subs)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="bg-white p-4 rounded shadow animate-pulse h-24"></div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
        <div className="bg-red-50 p-4 rounded text-red-600">
          {error}
          <button onClick={fetchData} className="ml-4 px-3 py-1 bg-red-600 text-white rounded">Retry</button>
        </div>
      </div>
    )
  }

  const formatCurrency = (val: number) => `$${val.toLocaleString()}`

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">Total Customers</div>
          <div className="text-2xl font-bold">{overview?.total_customers || 0}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">Active Subscriptions</div>
          <div className="text-2xl font-bold">{overview?.active_subscriptions || 0}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">Trial Subscriptions</div>
          <div className="text-2xl font-bold">{overview?.trial_subscriptions || 0}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">Cancelled Subscriptions</div>
          <div className="text-2xl font-bold">{overview?.cancelled_subscriptions || 0}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">Churn Rate</div>
          <div className="text-2xl font-bold">{overview?.churn_rate || 0}%</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">MRR</div>
          <div className="text-2xl font-bold">{formatCurrency(overview?.mrr || 0)}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">ARR</div>
          <div className="text-2xl font-bold">{formatCurrency(overview?.arr || 0)}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">Revenue Collected</div>
          <div className="text-2xl font-bold">{formatCurrency(overview?.revenue_collected || 0)}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">Outstanding</div>
          <div className="text-2xl font-bold">{formatCurrency(overview?.outstanding_invoice_amount || 0)}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-sm text-gray-500">Overdue Invoices</div>
          <div className="text-2xl font-bold">{overview?.overdue_invoices || 0}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-lg font-semibold mb-4">Monthly Revenue</h2>
          {revenue.length === 0 ? (
            <div className="text-gray-500 text-center py-8">No revenue data</div>
          ) : (
            <div className="space-y-2">
              {revenue.map((r, i) => (
                <div key={i} className="flex justify-between">
                  <span>{r.month}</span>
                  <span className="font-semibold">{formatCurrency(r.revenue)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-lg font-semibold mb-4">Subscription Status</h2>
          {subscriptions.length === 0 ? (
            <div className="text-gray-500 text-center py-8">No subscription data</div>
          ) : (
            <div className="space-y-2">
              {subscriptions.map((s, i) => (
                <div key={i} className="flex justify-between">
                  <span className="capitalize">{s.status}</span>
                  <span className="font-semibold">{s.count}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
