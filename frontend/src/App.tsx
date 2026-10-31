import { useEffect, useState } from 'react'
import { api } from './lib/api'

function App() {
  const [health, setHealth] = useState<any>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    api.getHealth()
      .then(setHealth)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f5f5f5' }}>
      <div style={{ backgroundColor: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', maxWidth: '500px', width: '100%' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem', textAlign: 'center' }}>
          Subscription Intelligence Platform
        </h1>
        <div>
          <h2 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Backend Health</h2>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          {health ? (
            <pre style={{ backgroundColor: '#f5f5f5', padding: '0.5rem', borderRadius: '4px', fontSize: '0.875rem', overflow: 'auto' }}>
              {JSON.stringify(health, null, 2)}
            </pre>
          ) : (
            <p>Loading...</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
