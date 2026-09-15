export type SystemState = 'checking' | 'operational' | 'degraded'
 
export interface Product {
  id: number
  sku: string
  name: string
  price: number | string
  active?: boolean
  is_active?: boolean
}
 
export interface CartItem extends Product {
  quantity: number
}
 
export interface UserPublic {
  username: string
  email: string
}
 
export interface RegisterInput {
  username: string
  email: string
  password: string
}
 
export interface LoginInput {
  username: string
  password: string
}
 
export interface TokenResponse {
  access_token: string
  token_type: string
}
 
export interface OrderItemPayload {
  product_id: number
  quantity: number
  unit_price: string
}
 
export interface OrderCreatePayload {
  customer_id: string
  items: OrderItemPayload[]
}
 
export interface OrderResponse {
  id: string
  customer_id: string
  total_amount: number | string
  status: string
  created_at: string
}
 
export interface Notice {
  type: 'info' | 'success' | 'error'
  message: string
}
