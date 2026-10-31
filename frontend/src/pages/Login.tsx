import { FormEvent, useState } from 'react'
import { apiRequest, authStorage } from '../lib/api'

type LoginProps = { onLogin: () => void }
type AuthMode = 'login' | 'register'

export default function Login({ onLogin }: LoginProps) {
  const [mode, setMode] = useState<AuthMode>('login')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function switchMode(next: AuthMode) {
    setMode(next)
    setError('')
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (mode === 'register') {
        await apiRequest('/api/v1/auth/register', {
          method: 'POST',
          body: JSON.stringify({
            email: email.trim(),
            password,
            first_name: firstName.trim(),
            last_name: lastName.trim(),
          }),
        })
      }

      const tokens = await apiRequest('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: email.trim(), password }),
      })
      authStorage.saveTokens(tokens.access_token, tokens.refresh_token)
      onLogin()
    } catch (err) {
      const message = err instanceof Error ? err.message : ''
      if (message === 'Failed to fetch' || message.includes('NetworkError')) {
        setError('Cannot reach the server. Check your connection and try again.')
      } else if (message.includes('500') || message === 'Internal Server Error') {
        setError('The server is temporarily unavailable. Please try again later.')
      } else {
        setError(message || (mode === 'register' ? 'Unable to create your account.' : 'Unable to sign in.'))
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 p-4 sm:p-6">
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-5 rounded-2xl bg-white p-6 shadow-2xl sm:p-8">
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-indigo-600">Subscription Intelligence</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">
            {mode === 'login' ? 'Welcome back' : 'Create your account'}
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            {mode === 'login' ? 'Sign in to access your dashboard.' : 'Get started with your subscription workspace.'}
          </p>
        </div>

        <div className="grid grid-cols-2 rounded-lg bg-slate-100 p-1 text-sm font-medium">
          <button type="button" onClick={() => switchMode('login')} aria-pressed={mode === 'login'}
            className={`rounded-md px-3 py-2 transition ${mode === 'login' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}>
            Sign in
          </button>
          <button type="button" onClick={() => switchMode('register')} aria-pressed={mode === 'register'}
            className={`rounded-md px-3 py-2 transition ${mode === 'register' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}>
            Create account
          </button>
        </div>

        {mode === 'register' && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label className="block text-sm font-medium text-slate-700">
              First name
              <input required autoComplete="given-name" value={firstName} onChange={e => setFirstName(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100" />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Last name
              <input required autoComplete="family-name" value={lastName} onChange={e => setLastName(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100" />
            </label>
          </div>
        )}

        <label className="block text-sm font-medium text-slate-700">
          Email
          <input type="email" required autoComplete="username" value={email} onChange={e => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100" />
        </label>

        <label className="block text-sm font-medium text-slate-700">
          Password
          <input type="password" required minLength={mode === 'register' ? 8 : undefined}
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            value={password} onChange={e => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100" />
          {mode === 'register' && <span className="mt-1 block text-xs text-slate-500">Use at least 8 characters.</span>}
        </label>

        {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

        <button type="submit" disabled={loading}
          className="w-full rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
          {loading ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
        </button>

        <p className="text-center text-xs text-slate-400">Secure access to your subscription workspace</p>
      </form>
    </main>
  )
}
