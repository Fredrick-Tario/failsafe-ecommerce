import { useEffect, useState } from 'react'
import { createOrder, getProducts, getSystemHealth } from './api'
import AuthModal from './components/AuthModal'
import CartDrawer from './components/CartDrawer'
import ProductGrid from './components/ProductGrid'
import StatusPill from './components/StatusPill'
import type { CartItem, Notice, Product, SystemState, UserPublic } from './types'
 
function readSavedUser(): UserPublic | null {
  const raw = localStorage.getItem('failsafe_user')
 
  if (!raw) {
    return null
  }
 
  try {
    return JSON.parse(raw) as UserPublic
  } catch {
    localStorage.removeItem('failsafe_user')
    return null
  }
}
 
function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'The request could not be completed.'
}
 
export default function App() {
  const [products, setProducts] = useState<Product[]>([])
  const [loadingProducts, setLoadingProducts] = useState(true)
  const [cart, setCart] = useState<CartItem[]>([])
  const [user, setUser] = useState<UserPublic | null>(() => readSavedUser())
  const [systemState, setSystemState] = useState<SystemState>('checking')
  const [authOpen, setAuthOpen] = useState(false)
  const [cartOpen, setCartOpen] = useState(false)
  const [checkoutBusy, setCheckoutBusy] = useState(false)
  const [notice, setNotice] = useState<Notice | null>(null)
 
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0)
 
  useEffect(() => {
    async function loadProducts() {
      setLoadingProducts(true)
 
      try {
        setProducts(await getProducts())
      } catch (error: unknown) {
        setNotice({ type: 'error', message: errorMessage(error) })
      } finally {
        setLoadingProducts(false)
      }
    }
 
    async function refreshHealth() {
      setSystemState(await getSystemHealth())
    }
 
    void loadProducts()
    void refreshHealth()
 
    const timer = window.setInterval(() => {
      void refreshHealth()
    }, 30000)
 
    return () => window.clearInterval(timer)
  }, [])
 
  function addToCart(product: Product) {
    setCart((current) => {
      const existing = current.find((item) => item.id === product.id)
 
      if (existing) {
        return current.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item,
        )
      }
 
      return [...current, { ...product, quantity: 1 }]
    })
 
    setNotice({ type: 'success', message: `${product.name} added to your bag.` })
    setCartOpen(true)
  }
 
  function increase(productId: number) {
    setCart((current) =>
      current.map((item) =>
        item.id === productId ? { ...item, quantity: item.quantity + 1 } : item,
      ),
    )
  }
 
  function decrease(productId: number) {
    setCart((current) =>
      current
        .map((item) =>
          item.id === productId ? { ...item, quantity: item.quantity - 1 } : item,
        )
        .filter((item) => item.quantity > 0),
    )
  }
 
  function remove(productId: number) {
    setCart((current) => current.filter((item) => item.id !== productId))
  }
 
  function handleAuthenticated(nextUser: UserPublic, token: string) {
    localStorage.setItem('failsafe_user', JSON.stringify(nextUser))
    localStorage.setItem('failsafe_token', token)
    setUser(nextUser)
    setNotice({ type: 'success', message: `Welcome, ${nextUser.username}.` })
  }
 
  function logout() {
    localStorage.removeItem('failsafe_user')
    localStorage.removeItem('failsafe_token')
    setUser(null)
    setNotice({ type: 'info', message: 'You are signed out.' })
  }
 
  async function checkout() {
    if (!user) {
      setCartOpen(false)
      setAuthOpen(true)
      return
    }
 
    if (cart.length === 0) {
      return
    }
 
    setCheckoutBusy(true)
    setNotice(null)
 
    try {
      const order = await createOrder({
        customer_id: user.username,
        items: cart.map((item) => ({
          product_id: item.id,
          quantity: item.quantity,
          unit_price: String(item.price),
        })),
      })
 
      if (order.status === 'CONFIRMED') {
        setCart([])
        setNotice({
          type: 'success',
          message: `Order ${order.id.slice(0, 8)} confirmed.`,
        })
      } else {
        setNotice({
          type: 'error',
          message: `Order could not be completed: ${order.status}.`,
        })
      }
    } catch (error: unknown) {
      setNotice({
        type: 'error',
        message: `Checkout is temporarily unavailable. ${errorMessage(error)}`,
      })
      setSystemState('degraded')
    } finally {
      setCheckoutBusy(false)
    }
  }
 
  function scrollToCollection() {
    document.getElementById('collection')?.scrollIntoView({ behavior: 'smooth' })
  }
 
  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="#top" aria-label="FailSafe home">
          <span className="brand-mark">F</span>
          <span>FailSafe</span>
        </a>
 
        <nav className="header-actions" aria-label="Store navigation">
          <StatusPill state={systemState} />
 
          {user ? (
            <button className="text-button" type="button" onClick={logout}>
              {user.username} · Sign out
            </button>
          ) : (
            <button className="text-button" type="button" onClick={() => setAuthOpen(true)}>
              Sign in
            </button>
          )}
 
          <button className="bag-button" type="button" onClick={() => setCartOpen(true)}>
            Bag <span>{cartCount}</span>
          </button>
        </nav>
      </header>
 
      <main id="top">
        <section className="hero section-shell">
          <div className="hero-copy">
            <p className="eyebrow">Resilient commerce, intentionally simple</p>
            <h1>Technology that keeps moving when systems get tested.</h1>
            <p className="hero-description">
              A premium storefront built on the FailSafe microservice platform—designed to make
              reliability, failure, and recovery visible from the customer experience.
            </p>
 
            <div className="hero-actions">
              <button className="primary-button" type="button" onClick={scrollToCollection}>
                Shop the collection
              </button>
              <span className="hero-note">Five backend services · Docker Compose · SRE ready</span>
            </div>
          </div>
 
          <div className="hero-panel" aria-hidden="true">
            <div className="hero-orbit orbit-one" />
            <div className="hero-orbit orbit-two" />
            <div className="hero-device">
              <span>FAILSAFE</span>
              <strong>01</strong>
            </div>
            <div className="hero-mini-card card-a">API</div>
            <div className="hero-mini-card card-b">UP</div>
          </div>
        </section>
 
        <section className="trust-strip section-shell" aria-label="Store qualities">
          <span>Fast checkout</span>
          <span>Live service state</span>
          <span>Failure-aware UX</span>
          <span>Local microservices</span>
        </section>
 
        <section className="collection section-shell" id="collection">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Featured collection</p>
              <h2>Simple products. Production-style platform.</h2>
            </div>
            <p>
              Product data comes directly from your Product Service. Checkout flows through Order,
              Inventory, and Payment services.
            </p>
          </div>
 
          <ProductGrid products={products} loading={loadingProducts} onAdd={addToCart} />
        </section>
 
        <section className="reliability-card section-shell">
          <div>
            <p className="eyebrow">Built for the incident lab</p>
            <h2>The storefront is part of the observability story.</h2>
          </div>
          <p>
            Stop a backend service later and watch the customer experience change. Recover the
            service, refresh the health state, and validate the full path again.
          </p>
        </section>
      </main>
 
      <footer className="site-footer section-shell">
        <div>
          <strong>FailSafe E-Commerce</strong>
          <span>DevOps · SRE · Cloud Engineering Lab</span>
        </div>
        <StatusPill state={systemState} />
      </footer>
 
      <CartDrawer
        open={cartOpen}
        items={cart}
        user={user}
        busy={checkoutBusy}
        notice={notice}
        onClose={() => setCartOpen(false)}
        onIncrease={increase}
        onDecrease={decrease}
        onRemove={remove}
        onCheckout={checkout}
      />
 
      <AuthModal
        open={authOpen}
        onClose={() => setAuthOpen(false)}
        onAuthenticated={handleAuthenticated}
      />
    </div>
  )
}
