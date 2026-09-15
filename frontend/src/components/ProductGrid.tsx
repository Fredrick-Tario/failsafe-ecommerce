import type { Product } from '../types'
 
interface ProductGridProps {
  products: Product[]
  loading: boolean
  onAdd: (product: Product) => void
}
 
function money(value: Product['price']): string {
  return Number(value).toLocaleString('en-PH', {
    style: 'currency',
    currency: 'PHP',
    maximumFractionDigits: 0,
  })
}
 
function initials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase()
}
 
export default function ProductGrid({ products, loading, onAdd }: ProductGridProps) {
  if (loading) {
    return (
      <div className="product-grid" aria-label="Loading products">
        {[1, 2, 3, 4].map((item) => (
          <article className="product-card skeleton-card" key={item}>
            <div className="skeleton skeleton-visual" />
            <div className="skeleton skeleton-line short" />
            <div className="skeleton skeleton-line" />
            <div className="skeleton skeleton-button" />
          </article>
        ))}
      </div>
    )
  }
 
  if (products.length === 0) {
    return <div className="empty-state">No products are available right now.</div>
  }
 
  return (
    <div className="product-grid">
      {products.map((product) => {
        const unavailable = product.active === false || product.is_active === false
 
        return (
          <article className="product-card" key={product.id}>
            <div className="product-visual" aria-hidden="true">
              <span>{initials(product.name)}</span>
            </div>
 
            <div className="product-meta">
              <span className="product-sku">{product.sku}</span>
              <span className={unavailable ? 'stock-badge unavailable' : 'stock-badge'}>
                {unavailable ? 'Unavailable' : 'In stock'}
              </span>
            </div>
 
            <h3>{product.name}</h3>
            <p className="product-description">Reliable everyday tech for your FailSafe demo store.</p>
 
            <div className="product-footer">
              <strong>{money(product.price)}</strong>
              <button
                className="secondary-button"
                type="button"
                disabled={unavailable}
                onClick={() => onAdd(product)}
              >
                Add to bag
              </button>
            </div>
          </article>
        )
      })}
    </div>
  )
}
