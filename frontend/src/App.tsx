import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import { authStorage } from './lib/api'

function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(authStorage.getAccessToken()))

  if (!authenticated) return <Login onLogin={() => setAuthenticated(true)} />

  return (
    <div>
      <header className="flex justify-end border-b bg-white px-6 py-3">
        <button onClick={() => { authStorage.clear(); setAuthenticated(false) }} className="rounded-lg border px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
          Sign out
        </button>
      </header>
      <Dashboard />
    </div>
  )
}

export default App
