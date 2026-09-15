import type {
  LoginInput,
  OrderCreatePayload,
  OrderResponse,
  Product,
  RegisterInput,
  SystemState,
  TokenResponse,
  UserPublic,
} from './types'
 
type ErrorBody = {
  detail?: string
}
 
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)
 
  if (!response.ok) {
    let message = `Request failed (${response.status})`
 
    try {
      const body = (await response.json()) as ErrorBody
      if (body.detail) {
        message = body.detail
      }
    } catch {
      // Keep the fallback message when the response is not JSON.
    }
 
    throw new Error(message)
  }
 
  return (await response.json()) as T
}
 
export function getProducts(): Promise<Product[]> {
  return request<Product[]>('/api/products/products')
}
 
export function registerUser(input: RegisterInput): Promise<UserPublic> {
  return request<UserPublic>('/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(input),
  })
}
 
export function loginUser(input: LoginInput): Promise<TokenResponse> {
  const form = new URLSearchParams()
  form.set('username', input.username)
  form.set('password', input.password)
 
  return request<TokenResponse>('/api/auth/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: form,
  })
}
 
export function getCurrentUser(token: string): Promise<UserPublic> {
  return request<UserPublic>('/api/auth/users/me', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}
 
export function createOrder(input: OrderCreatePayload): Promise<OrderResponse> {
  return request<OrderResponse>('/api/orders/orders', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(input),
  })
}
 
async function health(url: string): Promise<boolean> {
  try {
    const response = await fetch(url)
    return response.ok
  } catch {
    return false
  }
}
 
export async function getSystemHealth(): Promise<SystemState> {
  const checks = await Promise.all([
    health('/api/auth/health'),
    health('/api/products/health'),
    health('/api/inventory/health'),
    health('/api/orders/health'),
    health('/api/payment/health'),
  ])
 
  return checks.every(Boolean) ? 'operational' : 'degraded'
}
