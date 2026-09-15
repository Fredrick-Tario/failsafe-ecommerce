import type { CartItem, Notice, UserPublic } from '../types'
 
interface CartDrawerProps {
  open: boolean
  items: CartItem[]
  user: UserPublic | null
  busy: boolean
  notice: Notice | null
  onClose: () => void
  onIncrease: (productId: number) => void
  onDecrease: (productId: number) => void
  onRemove: (productId: number) => void
  onCheckout: () => void
}
 
function money(value: number): string {
  return value.toLocaleString('en-PH', {
    style: 'currency',
    currency: 'PHP',
    maximumFractionDigits: 0,
  })
}
 
export default function CartDrawer({
  open,
  items,
  user,
  busy,
  notice,
  onClose,
  onIncrease,
  onDecrease,
  onRemove,
  onCheckout,
}: CartDrawerProps) {
  const total = items.reduce(
    (sum, item) => sum + Number(item.price) * item.quantity,
    0,
  )
 
  return (
    <>
      <button
        className={`drawer-backdrop ${open ? 'visible' : ''}`}
        type="button"
        aria-label="Close shopping bag"
        onClick={onClose}
      />
 
      <aside className={`cart-drawer ${open ? 'open' : ''}`} aria-hidden={!open}>
        <div className="drawer-header">
          <div>
            <p className="eyebrow">Your bag</p>
            <h2>{items.length === 0 ? 'Nothing here yet' : `${items.length} item type(s)`}</h2>
          </div>
          <button className="icon-button" type="button" onClick={onClose}>
            ×
          </button>
        </div>
 
        <div className="drawer-body">
          {items.length === 0 ? (
            <div className="cart-empty">
              <div className="empty-icon">+</div>
              <p>Add a product to start your order.</p>
            </div>
          ) : (
            items.map((item) => (
              <article className="cart-line" key={item.id}>
                <div>
                  <h3>{item.name}</h3>
                  <p>{money(Number(item.price))}</p>
                </div>
 
                <div className="quantity-control">
                  <button type="button" onClick={() => onDecrease(item.id)} aria-label="Decrease quantity">
                    −
                  </button>
                  <span>{item.quantity}</span>
                  <button type="button" onClick={() => onIncrease(item.id)} aria-label="Increase quantity">
                    +
                  </button>
                </div>
 
                <button className="remove-button" type="button" onClick={() => onRemove(item.id)}>
                  Remove
                </button>
              </article>
            ))
          )}
        </div>
 
        <div className="drawer-footer">
          {notice && <div className={`notice notice-${notice.type}`}>{notice.message}</div>}
 
          <div className="total-row">
            <span>Total</span>
            <strong>{money(total)}</strong>
          </div>
 
          <p className="checkout-caption">
            {user ? `Checking out as ${user.username}` : 'Sign in before placing an order.'}
          </p>
 
          <button
            className="primary-button full-button"
            type="button"
            disabled={busy || items.length === 0}
            onClick={onCheckout}
          >
            {busy ? 'Processing order…' : user ? 'Place order' : 'Sign in to checkout'}
          </button>
        </div>
      </aside>
    </>
  )
}
