import { ShoppingCart, Menu, X } from 'lucide-react'
import { useState } from 'react'

function Header({ cartCount, onCheckout }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <span className="logo-icon">🎫</span>
          <span className="logo-text">CardStore</span>
        </div>
        
        <nav className="nav">
          <button className="nav-link" onClick={onCheckout}>
            <ShoppingCart size={20} />
            <span>Cart</span>
            {cartCount > 0 && (
              <span className="cart-badge">{cartCount}</span>
            )}
          </button>
        </nav>

        <button 
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {mobileMenuOpen && (
        <div className="mobile-menu">
          <button className="mobile-nav-link" onClick={() => {
            onCheckout()
            setMobileMenuOpen(false)
          }}>
            <ShoppingCart size={20} />
            <span>Cart ({cartCount})</span>
          </button>
        </div>
      )}
    </header>
  )
}

export default Header