import {
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
  type MouseEvent,
} from 'react'
import { getCurrentUser, loginUser, registerUser } from '../api'
import type { UserPublic } from '../types'
 
type AuthMode = 'login' | 'register'
 
interface AuthModalProps {
  open: boolean
  onClose: () => void
  onAuthenticated: (user: UserPublic, token: string) => void
}
 
function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Something went wrong.'
}
 
export default function AuthModal({
  open,
  onClose,
  onAuthenticated,
}: AuthModalProps) {
  const [mode, setMode] = useState<AuthMode>('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
 
  useEffect(() => {
    if (open) {
      setMessage(null)
    }
  }, [open])
 
  if (!open) {
    return null
  }
 
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setMessage(null)
 
    try {
      if (mode === 'register') {
        await registerUser({ username, email, password })
      }
 
      const token = await loginUser({ username, password })
      const user = await getCurrentUser(token.access_token)
      onAuthenticated(user, token.access_token)
      onClose()
    } catch (error: unknown) {
      setMessage(errorMessage(error))
    } finally {
      setBusy(false)
    }
  }
 
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="auth-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-title"
        onMouseDown={(event: MouseEvent<HTMLElement>) => event.stopPropagation()}
      >
        <button className="icon-button modal-close" type="button" onClick={onClose}>
          ×
        </button>
 
        <p className="eyebrow">FailSafe account</p>
        <h2 id="auth-title">{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
        <p className="modal-copy">
          {mode === 'login'
            ? 'Sign in to continue to checkout.'
            : 'Create an account, then continue shopping.'}
        </p>
 
        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Username
            <input
              value={username}
              onChange={(event: ChangeEvent<HTMLInputElement>) => setUsername(event.target.value)}
              minLength={3}
              required
              autoComplete="username"
            />
          </label>
 
          {mode === 'register' && (
            <label>
              Email
              <input
                type="email"
                value={email}
                onChange={(event: ChangeEvent<HTMLInputElement>) => setEmail(event.target.value)}
                required
                autoComplete="email"
              />
            </label>
          )}
 
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event: ChangeEvent<HTMLInputElement>) => setPassword(event.target.value)}
              minLength={8}
              required
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />
          </label>
 
          {message && <div className="form-message error-message">{message}</div>}
 
          <button className="primary-button full-button" type="submit" disabled={busy}>
            {busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>
 
        <button
          className="text-button auth-switch"
          type="button"
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
        >
          {mode === 'login' ? 'New here? Create an account' : 'Already registered? Sign in'}
        </button>
      </section>
    </div>
  )
}
